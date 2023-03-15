import airflow
from airflow import DAG
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.sensors.http_sensor import HttpSensor
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.hive_operator import HiveOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.slack_operator import SlackAPIPostOperator
from datetime import datetime, timedelta
from ftp_footage_helper import ftp_helpers
from ftplib import FTP_TLS
from tqdm import tqdm
from ftp_footage_helper import ftp_helpers
from dotenv import load_dotenv
from pathlib import Path
import os
import csv
import requests
import json

def upload_footage():
    dotenv_path = Path('/.env')
    load_dotenv(dotenv_path=dotenv_path)

    obj_ftp = ftp_helpers()
    folder_path = os.getenv("FTP_folder_path")
    folders_last_week = obj_ftp.get_number_days(folder_path)
    print(folders_last_week)
    obj_ftp.connect_ftp_server()

    for folder_name in folders_last_week:
        selected_folder = folder_name
        obj_ftp.FTP_create_folder_structure(selected_folder)
        complete_path = f"{folder_path}/{selected_folder}"
        footage_front = f"{complete_path}/F"
        footage_rear = f"{complete_path}/R"
        file_count_F = obj_ftp.count_files(footage_front)
        file_count_R = obj_ftp.count_files(footage_rear)
        Total_Count = file_count_F + file_count_R
        obj_ftp.FTP_upload_files(selected_folder, footage_front, footage_rear, Total_Count)

    obj_ftp.FTP_close_connection()



default_args = {
            "owner": "Airflow",
            "start_date": airflow.utils.dates.days_ago(1),
            "depends_on_past": False,
            "email_on_failure": False,
            "email_on_retry": False,
            "email": "mannyelaine26@gmail.com",
            "retries": 1,
            "retry_delay": timedelta(minutes=5)
        }

def _get_message() -> str:
    return "Hi from ftp_upload_data_pipeline"

with DAG(dag_id="ftp_footage_upload", schedule_interval="@daily", default_args=default_args, catchup=False) as dag:

    # Parsing forex_pairs.csv and downloading the files
    downloading_rates = PythonOperator(
            task_id="uploading_rates",
            python_callable=upload_footage
    )
