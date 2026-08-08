import os
from dotenv import load_dotenv
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests

load_dotenv()
API_BASE = os.getenv("API_BASE")
import logging

logger = logging.getLogger(__name__)


def refresh_forecasts(**context):
    # In production, pull the entity list from the DB; hardcoded here for the single test entity
    resp = requests.get(f"{API_BASE}/entities/")  # add this list endpoint if not present
    entities = resp.json() if resp.ok else []

    results = []
    for entity in entities:
        r = requests.post(f"{API_BASE}/analytics/forecast/", json={"entity_id": entity["id"], "periods_months": 6})
        if r.ok:
            results.append(entity["id"])
        else:
            logger.warning(f"Forecast failed for entity {entity['id']}: {r.text}")
    return results


with DAG(
    dag_id="forecast_refresh",
    schedule_interval="@weekly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["apexsync", "analytics"],
) as dag:

    refresh = PythonOperator(
        task_id="refresh_forecasts",
        python_callable=refresh_forecasts,
    )