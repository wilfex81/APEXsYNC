import os
from dotenv import load_dotenv
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


load_dotenv()

DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "null")
MAIN_PROJECT_DIR = os.getenv("MAIN_PROJECT_DIR", "null")

default_args = {
    "owner": "apexsync",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="daily_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["apexsync", "ingestion", "dbt"],
) as dag:

    load_data = BashOperator(
        task_id="load_synthetic_data",
        bash_command=f"cd {MAIN_PROJECT_DIR} && python manage.py load_synthetic_data",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
    )

    load_data >> dbt_run >> dbt_test