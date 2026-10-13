"""Daily demo batch; preserve the pipeline's all-or-nothing transaction."""
from datetime import timedelta

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="banking_data_pipeline",
    description="Synthetic CSV -> PostgreSQL UPSERT -> four quality checks",
    start_date=pendulum.datetime(2026, 10, 1, tz="Asia/Almaty"),
    schedule="0 8 * * *",
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "execution_timeout": timedelta(minutes=15),
    },
    tags=["banking", "etl", "data-quality", "demo"],
) as dag:
    prepare_data = BashOperator(
        task_id="prepare_demo_data",
        bash_command="python /opt/banking/airflow_support/prepare_data.py",
        cwd="/opt/banking",
        do_xcom_push=False,
    )
    load_and_validate = BashOperator(
        task_id="load_and_validate",
        bash_command="python /opt/banking/run_pipeline.py",
        cwd="/opt/banking",
        do_xcom_push=False,
    )
    prepare_data >> load_and_validate
