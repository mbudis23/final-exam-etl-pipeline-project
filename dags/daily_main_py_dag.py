from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import subprocess
import os 

current_dir = os.path.dirname(os.path.abspath(__file__))

# Path ke model
file_path = os.path.join(current_dir, "../src/main.py")
file1_path = os.path.join(current_dir, "../src/scrap_twitter.py")
file2_path = os.path.join(current_dir, "../src/scrap_thread.py")
file3_path = os.path.join(current_dir, "../src/transform.py")
file4_path = os.path.join(current_dir, "../src/load.py")


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

def run_scrap_py():
    """Function to execute scrap_twitter.py script."""
    subprocess.run(["python", file1_path], check=True)

def run_scrap_thread_py():
    """Function to execute scrap_thread.py script."""
    subprocess.run(["python", file2_path], check=True)

def run_transform_py():
    """Function to execute transform.py script."""
    subprocess.run(["python", file3_path], check=True)

def run_load_py():
    """Function to execute load.py script."""
    subprocess.run(["python", file4_path], check=True)

with DAG(
    'daily_main_py_dag',
    default_args=default_args,
    description='DAG to run scrap_twitter.py and scrap_thread.py in parallel, followed by main.py',
    schedule_interval='0 8 * * *',  # Cron expression for daily at 8 AM
    catchup=False
) as dag:
    scrap_thread = PythonOperator(
        task_id='run_scrap_thread',
        python_callable=run_scrap_thread_py
    )
    scrap_twitter = PythonOperator(
        task_id='run_scrap_twitter',
        python_callable=run_scrap_py
    )

    execute_transform = PythonOperator(
        task_id='run_transform_py',
        python_callable=run_transform_py
    )
    execite_load = PythonOperator(
        task_id='run_load_py',
        python_callable=run_load_py
    )
    # execute_main = PythonOperator(
    #     task_id='run_main_py',
    #     python_callable=run_main_py
    # )

    # Set the order of execution
    [scrap_twitter, scrap_thread] >> execute_transform >> execite_load