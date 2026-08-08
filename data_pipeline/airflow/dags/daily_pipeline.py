import os
from dotenv import load_dotenv
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


load_dotenv()

DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "null")
MAIN_PROJECT_DIR = os.getenv("MAIN_PROJECT_DIR", "null")
APP_VENV_PYTHON = os.getenv("APP_VENV_PYTHON", "null")
APP_VENV_DBT = os.getenv("APP_VENV_DBT", "null")

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
        bash_command=f"cd {MAIN_PROJECT_DIR} && {APP_VENV_PYTHON} manage.py load_synthetic_data",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && {APP_VENV_DBT} run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && {APP_VENV_DBT} test",
    )

    load_data >> dbt_run >> dbt_test