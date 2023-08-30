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


dotenv_path = Path('/opt/airflow/dags/.env')
load_dotenv(dotenv_path=dotenv_path)
html_str = ""

def upload_footage():
    global html_str
    html_str = f"<h3>Following folders have been uploaded to {os.getenv('FTP_server_name')}.</h3> </br><ol>"    
    obj_ftp = ftp_helpers()
    folder_path = os.getenv("FTP_folder_path")
    obj_ftp.connect_ftp_server()
    folders_last_week = obj_ftp.get_number_days(folder_path)
    obj_ftp.generate_upload_queue(folders_last_week)
    folder_counter = 0
    for folder_name in folders_last_week:
        selected_folder = folder_name
        if(obj_ftp.chk_folder_present(selected_folder) == False):
            html_str += f"<li>{selected_folder}</li>"
            folder_counter += 1
            obj_ftp.FTP_create_folder_structure(selected_folder)
            complete_path = f"{folder_path}/{selected_folder}"
            footage_front = f"{complete_path}/F"
            footage_rear = f"{complete_path}/R"
            file_count_F = obj_ftp.count_files(footage_front)
            file_count_R = obj_ftp.count_files(footage_rear)
            Total_Count = file_count_F + file_count_R
            obj_ftp.FTP_upload_files(selected_folder, footage_front, footage_rear, Total_Count)
            
    
    html_str += "</ol>" 
    if(os.path.exists('/opt/airflow/dags/html_content.txt')):
        os.remove('/opt/airflow/dags/html_content.txt')
    
    if(folder_counter == 0):
        html_str = "<h3>No folder(s) present to upload today.</h3>"
        
    
    with open('/opt/airflow/dags/html_content.txt', 'w') as file_content:
        file_content.write(html_str)
        
    obj_ftp.FTP_close_connection()
    
def create_html_content(**kwargs):
    with open('/opt/airflow/dags/html_content.txt', 'r') as file_content:
        email_content = file_content.read()

    send_email = EmailOperator(
        task_id="send_email",
        to="mannyelaine26@gmail.com",
        subject="Footage Status",
        html_content=email_content
    )
    send_email.execute(context=kwargs)

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
    uploading_footage = PythonOperator(
            task_id="uploading_footage",
            python_callable=upload_footage
    )
    
    send_email = PythonOperator(
        task_id="send_email",
        python_callable=create_html_content,
        provide_context=True
    )

    uploading_footage >> send_email