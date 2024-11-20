from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import subprocess
import os 

current_dir = os.path.dirname(os.path.abspath(__file__))

# Path ke model
file_path = os.path.join(current_dir, "../src/main.py")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retry_delay': timedelta(minutes=15),
    'retries': 1
}


def run_main_py():
    """Function to execute main.py script."""
    subprocess.run(["python", file_path], check=True)

with DAG(
    'daily_main_py_dag',
    default_args=default_args,
    description='DAG to run main.py daily at 8 AM',
    schedule_interval='0 8 * * *',  # Cron expression for daily at 8 AM
    catchup=False
) as dag:

    execute_script = PythonOperator(
        task_id='run_main_py',
        python_callable=run_main_py
    )

execute_script
