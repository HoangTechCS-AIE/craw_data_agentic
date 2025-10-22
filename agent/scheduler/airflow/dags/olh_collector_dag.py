"""Airflow DAG for the OpenLinkedHub collector."""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner": "openlinkedhub",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="olh_agentic_collector",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 * * * *",
    catchup=False,
    max_active_runs=1,
    tags=["open-data", "vietnam"],
) as dag:
    env_export = "export $(grep -v '^#' /opt/olh/.env | xargs)"
    run_worldbank = BashOperator(
        task_id="worldbank",
        bash_command=f"cd /opt/olh && {env_export} && scrapy crawl worldbank",
    )
    run_ckan = BashOperator(
        task_id="ckan",
        bash_command=f"cd /opt/olh && {env_export} && python -m agent.orchestrator --only ckan",
    )
    run_mic = BashOperator(
        task_id="mic",
        bash_command=f"cd /opt/olh && {env_export} && scrapy crawl mic_portal",
    )
    finalize = BashOperator(
        task_id="finalize",
        bash_command="echo 'OpenLinkedHub collection complete'",
    )

    run_worldbank >> run_ckan >> run_mic >> finalize
