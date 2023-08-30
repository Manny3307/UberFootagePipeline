from pathlib import Path
from ftp_footage_helper import ftp_helpers
from ftplib import FTP_TLS
from tqdm import tqdm
from dotenv import load_dotenv
import ftplib

import os
import pathlib

ftps = FTP_TLS()
dotenv_path = Path('/home/manny/UberFootagePipeline/.env')
load_dotenv(dotenv_path=dotenv_path)


obj_ftp = ftp_helpers()
folder_path = os.getenv("FTP_folder_path")
ftps = ftplib.FTP(os.getenv("FTP_server"), os.getenv("FTP_server_login"), os.getenv("FTP_server_password"))

def count_files(path):
    count = 0
    for root,d_names,f_names in os.walk(path):
        count += len(f_names)
    return count


def get_total_file_count():
    file_count = 0
    Local_Path = os.getenv('FTP_Local_folder_path')
    folders_last_week = obj_ftp.get_number_days(Local_Path)
    for folder_name in folders_last_week:
        FTP_Path = os.getenv('FTP_server_folder_path')
        ftps.cwd(FTP_Path)
        if(folder_name not in ftps.nlst()):
            complete_local_path = os.path.join(Local_Path, folder_name)
            print(complete_local_path)
            file_count1 = count_files(complete_local_path)
            file_count += file_count1
    
    return file_count

def get_folder_name(complete_path):
	complete_local_path = complete_path.split('/')
	return complete_local_path[len(complete_local_path) - 1]

def upload_files_to_ftp_server():
    html_str = f"<h3>Following folders have been uploaded to {os.getenv('FTP_server_name')}.</h3> </br><ol>"    
    FTP_Path = os.getenv('FTP_server_folder_path')
    Local_Path = os.getenv('FTP_Local_folder_path')
    folders_last_week = obj_ftp.get_number_days(Local_Path)
    ftps.cwd(FTP_Path)
    folder_counter = 0
    for folder_name in folders_last_week:
        complete_local_path = os.path.join(Local_Path, folder_name)
        
        for root,d_names,f_names in os.walk(complete_local_path):
            server_folder_path = root.replace(Local_Path,FTP_Path)
            server_folder_path_excluded_current_folder = server_folder_path.split('/')
            #Get the parent folder to the given folder with complete root path
            server_folder_path_without_current_folder = '/'.join(server_folder_path_excluded_current_folder[:len(server_folder_path_excluded_current_folder) - 1])
            #Setting the current working directory to the parent of the current folder
            ftps.cwd(server_folder_path_without_current_folder)
            #Get the current server including subfolders 
            current_server_folder = server_folder_path_excluded_current_folder[len(server_folder_path_excluded_current_folder) - 1]
            if(current_server_folder not in ftps.nlst()):
                if(folder_name == current_server_folder):
                    html_str += f"<li>{folder_name}</li>"
                    folder_counter += 1
                    
                #Create the folders or sub folders if they don't exist
                ftps.mkd(server_folder_path)
                #Setting the current working directory to created directory above
                ftps.cwd(server_folder_path)

                selected_folder = get_folder_name(server_folder_path)
                for file_n in f_names:
                    complete_file_path = os.path.join(root,file_n)
                    filesize = int(os.path.getsize(complete_file_path))
                    TheFile = open(complete_file_path, 'rb')
                    with tqdm(unit = 'blocks', unit_scale = True, leave = False, miniters = 1, desc = f'Uploading {selected_folder} {file_n}......', total = filesize) as tqdm_instance:
                        ftps.storbinary(f'STOR {file_n}', TheFile , 2048, callback = lambda sent: tqdm_instance.update(len(sent)))

            
    html_str += "</ol>" 			
    if(folder_counter == 0):
        html_str = "No Folders to Upload. Have a nice and wonderful day."
        
        
    print(html_str)

    '''if(os.path.exists('/opt/airflow/dags/html_content.txt')):
        os.remove('/opt/airflow/dags/html_content.txt')
    
    if(folder_counter == 0):
        html_str = "<h3>No folder(s) present to upload today.</h3>"
        
    
    with open('/opt/airflow/dags/html_content.txt', 'w') as file_content:
        file_content.write(html_str)'''

upload_files_to_ftp_server()

ftps.close()