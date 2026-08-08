import os
from dotenv import load_dotenv
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.base import BaseSensorOperator
from airflow.models import Variable
from datetime import datetime
import requests

load_dotenv()
API_BASE = os.getenv("API_BASE")


class ManualApprovalSensor(BaseSensorOperator):
    """
    Polls an Airflow Variable that a human flips to 'approved' via the CLI/UI
    once they've reviewed the draft rule set in the Django admin.
    """
    def poke(self, context):
        rule_set_id = context["ti"].xcom_pull(task_ids="create_draft_rule_set")
        approval_key = f"tax_approval_{rule_set_id}"
        return Variable.get(approval_key, default_var="pending") == "approved"


def create_draft_rule_set(**context):
    payload = {
        "jurisdiction": "MX",
        "effective_date": context["ds"],
        "published_gazette_ref": "PENDING - manual entry required",
        "notes": "Auto-created draft, awaiting SHCP/Gaceta Oficial confirmation and human review.",
        "rules": [
            {"rule_type": "IVA", "applies_to": "general", "rate": "0.16"},
        ],
    }
    resp = requests.post(f"{API_BASE}/tax/rule-sets/", json=payload)
    resp.raise_for_status()
    rule_set_id = resp.json()["id"]
    context["ti"].xcom_push(key="rule_set_id", value=rule_set_id)
    return rule_set_id


def publish_rule_set(**context):
    rule_set_id = context["ti"].xcom_pull(task_ids="create_draft_rule_set")
    resp = requests.post(
        f"{API_BASE}/tax/rule-sets/{rule_set_id}/publish/",
        json={"published_by": "airflow_monthly_dag"},
    )
    resp.raise_for_status()
    return resp.json()


with DAG(
    dag_id="monthly_tax_rule_update",
    schedule_interval="@monthly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["apexsync", "tax_engine", "compliance"],
) as dag:

    create_draft = PythonOperator(
        task_id="create_draft_rule_set",
        python_callable=create_draft_rule_set,
    )

    wait_for_approval = ManualApprovalSensor(
        task_id="wait_for_human_approval",
        poke_interval=3600,   # check hourly
        timeout=60 * 60 * 24 * 5,  # give it 5 days before failing
        mode="reschedule",     # don't hold a worker slot while waiting
    )

    publish = PythonOperator(
        task_id="publish_rule_set",
        python_callable=publish_rule_set,
    )

    create_draft >> wait_for_approval >> publish