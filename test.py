#import pywhatkit
'''from whatsapp_api_client_python import API as API
greenAPI = API.GreenApi('1101804127', '491d90967627494dbc2a560f5a3226acb9573b770a4340f0ba')
result = greenAPI.sending.sendMessage('919868388666', 'Message text')
print(result.data)
'''
'''from heyoo import WhatsApp
messenger = WhatsApp('EAAXTFoYgkHMBAEnZBeUAZC4U2faSpzcKYrx1tzUP82oU9EsnjPPB9XLkSAlF8VlEdmIoSh2CWgzFjZAfgvmBM8iKgFzIij1hbtTGUvU51wgq9PbsEjW75BnNZBGaI0yZBZCmEKjkknx2u84C3xq2wXKvztkz0ZBDerEGKEZAjZAOC9DSgfP8aYWx1',phone_number_id=102717549453928)

messenger.send_message('Hello I am WhatsApp Cloud API', '+61416438047')
'''
#pywhatkit.sendwhatmsg('+61416438047', 'Message 1', 22, 13)
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
html_str = f"<h3>Following folders have been uploaded uploaded to {os.getenv('FTP_server_name')}.</h3> </br><ol>"

obj_ftp = ftp_helpers()
folder_path = os.getenv("FTP_folder_path")
obj_ftp.connect_ftp_server()
folders_last_week = obj_ftp.get_number_days(folder_path)
obj_ftp.generate_upload_queue(folders_last_week)
print(folders_last_week)
for folder_name in folders_last_week:
    selected_folder = folder_name
    if(obj_ftp.chk_folder_present(selected_folder) == False):
        obj_ftp.FTP_create_folder_structure(selected_folder)
        complete_path = f"{folder_path}/{selected_folder}"
        footage_front = f"{complete_path}/F"
        footage_rear = f"{complete_path}/R"
        file_count_F = obj_ftp.count_files(footage_front)
        file_count_R = obj_ftp.count_files(footage_rear)
        Total_Count = file_count_F + file_count_R
        obj_ftp.FTP_upload_files(selected_folder, footage_front, footage_rear, Total_Count)
        html_str += f"<li>{selected_folder}</li>"
    

html_str += "</ol>"
obj_ftp.FTP_close_connection()

print(html_str)