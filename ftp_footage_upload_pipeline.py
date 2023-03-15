from ftplib import FTP_TLS
from tqdm import tqdm
import os
from helpers.FolderFunctions import FolderFunction
from ftp_footage_helper import ftp_helpers
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

obj_ftp = ftp_helpers()
folder_path = os.getenv("FTP_folder_path")
obj_ftp.connect_ftp_server()
folders_last_week = obj_ftp.get_number_days(folder_path)

for folder_name in folders_last_week:
    selected_folder = folder_name
    print(obj_ftp.chk_folder_present(selected_folder))
    if(obj_ftp.chk_folder_present(selected_folder) == False):
        print(f"Uploading {selected_folder}........")
        obj_ftp.FTP_create_folder_structure(selected_folder)
        complete_path = f"{folder_path}/{selected_folder}"
        footage_front = f"{complete_path}/F"
        footage_rear = f"{complete_path}/R"
        file_count_F = obj_ftp.count_files(footage_front)
        file_count_R = obj_ftp.count_files(footage_rear)
        Total_Count = file_count_F + file_count_R
        obj_ftp.FTP_upload_files(selected_folder, footage_front, footage_rear, Total_Count)

obj_ftp.FTP_close_connection()