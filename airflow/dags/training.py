from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago

args = {
    'owner': 'airflow',
}

dag = DAG(
    dag_id='training',
    default_args=args,
    schedule_interval='@daily',
    start_date=days_ago(0),
    dagrun_timeout=timedelta(minutes=60),
)

command = "/opt/airflow/dags/spark-submit.sh "

BashOperator(
    task_id='credit',
    bash_command=command,
    dag=dag,
)

if __name__ == "__main__":
    dag.cli()
