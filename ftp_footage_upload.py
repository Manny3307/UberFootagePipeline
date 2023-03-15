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
folder_dict = obj_ftp.create_folder_dict(folder_path)


for folder_name_counter in folder_dict:
    for i in folder_name_counter.items():
        print(f"{i[0]}: {i[1]}")

pick_counter = input("Please enter the number in front of the folder to upload: ")
selected_folder = obj_ftp.get_folder_name(folder_dict, pick_counter)

obj_ftp.connect_ftp_server()
obj_ftp.FTP_create_folder_structure(selected_folder)

complete_path = f"{folder_path}/{selected_folder}"
footage_front = f"{complete_path}/F"
footage_rear = f"{complete_path}/R"
file_count_F = obj_ftp.count_files(footage_front)
file_count_R = obj_ftp.count_files(footage_rear)
Total_Count = file_count_F + file_count_R

obj_ftp.FTP_upload_files(selected_folder, footage_front, footage_rear, Total_Count)
obj_ftp.FTP_close_connection()