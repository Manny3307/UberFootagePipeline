import ftplib
from ftplib import FTP_TLS
from tqdm import tqdm
from dotenv import load_dotenv
from pathlib import Path
import os, time
from datetime import datetime, date
import pandas as pd
import numpy as np
import random
import string

upload_queue_dataset = pd.DataFrame()
ftps = FTP_TLS()

class ftp_helpers:
    
    def __init__(self):
        global folder_path, ftps, filesList, nameList, filesizeList, upload_queue_dataset
        dotenv_path = Path('/opt/airflow/dags/.env')
        load_dotenv(dotenv_path=dotenv_path)
        folder_path = os.getenv("FTP_folder_path")
        
        #ftps = ftplib.FTP()
        filesList= []
        nameList= []
        filesizeList= []
        

    def count_files(self, path):
        count = 0
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                count += 1
        return count
    
    def strip_folder_name(self, complete_path):
        folder_name = complete_path.split("/")

        return folder_name[len(folder_name) - 1]

    def get_folder_name(self, folder_dict, counter):
        folder_name = ""
        for folder_name_counter in folder_dict:
            for folder_values in folder_name_counter.items():
                if str(folder_values[0]) == counter:
                    folder_name = folder_values[1]

        return folder_name
    
    def create_folder_dict(self, path):
        folder_dict = []
        counter = 1
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            folder_dct = {counter: self.strip_folder_name(item_path)}
            folder_dict.append(folder_dct)
            counter += 1
        return folder_dict

    def connect_ftp_server(self):
        global ftps
        try:
            print(f"Attempting  to login to {os.getenv('FTP_server_name')}")
            #ftps.context.set_ciphers('DEFAULT@SECLEVEL=1')
            ftps = ftplib.FTP(os.getenv("FTP_server"), os.getenv("FTP_server_login"), os.getenv("FTP_server_password"))
            #ftps.connect(os.getenv("FTP_server"),int(os.getenv("FTP_server_port")))
            #ftps.login(user = os.getenv("FTP_server_login"), passwd = os.getenv("FTP_server_password"))
            print(f"Successfully logged in to {os.getenv('FTP_server_name')}")
        except Exception as e: 
            print(e)
            print("Login Failed!!!!")
            

    def FTP_create_folder_structure(self, folder_name):
        try:
            if folder_name not in ftps.nlst():
                print(f"Attempting to create the folder structure for {folder_name}")
                ftps.cwd(os.getenv("FTP_server_folder_path"))
                ftps.mkd(f'{os.getenv("FTP_server_folder_path")}{folder_name}')
                ftps.mkd(f'{os.getenv("FTP_server_folder_path")}{folder_name}/F')
                ftps.mkd(f'{os.getenv("FTP_server_folder_path")}{folder_name}/R')
                print(f"Folder structure for {folder_name} created successfully!!!!")
            else:
                print(f"folder {folder_name} already exists!!!")
        except:
            print(f"Folder structure for {folder_name} can't be created!!!!")
    
    def chk_file_FTP(self, filename, fileswithsize):
        chk_file = False
        for temp in fileswithsize:
            for temp1 in temp:
                if(temp1 == filename):
                    chk_file = True

        return chk_file
    
    def chk_file_upload_for_batch(self, foldername, files, front_or_rear):
        ftps.cwd(f'{os.getenv("FTP_server_folder_path")}{foldername}/{front_or_rear}')
        fileswithsize = []
        filewithsize = {}
        fcount = 0

        for f in files:
            fcount += 1
            filewithsize = {}
            for t, q in f[1].items():
                if (t == "size"):
                    filewithsize[f[0]] = q
                    #print(filewithsize)
            fileswithsize.append(filewithsize)        
            filewithsize = ""


        fileswithsize = fileswithsize[2:]

        filesize = 0
        local_fileswithsize = []
        local_filewithsize = {}
        total = 0

        footage_path = f"{os.getenv('FTP_folder_path')}/{foldername}/{front_or_rear}"
        footage_files = os.scandir(footage_path)
        for ff in footage_files:
            local_filewithsize = {}
            total += 1
            if(ff.is_file()):
                filesize = ff.stat().st_size
                local_filewithsize[ff.name] = filesize
                #print(f"{ff.name} {filesize}")
                local_fileswithsize.append(local_filewithsize)
                local_filewithsize = ""

        #Check if any files got misssed in the batch
        files_not_uploaded = []
        for check_files in local_fileswithsize:
            for mkey in check_files:
                if self.chk_file_FTP(mkey, fileswithsize) == False:
                    files_not_uploaded.append(mkey)
                    
        return files_not_uploaded
    
    def getsubdir(self, file_path):
        subdir = str(file_path).split("/")
        return subdir[len(subdir) - 1]

    def generate_upload_queue(self, folder_list):
        for folder_name in folder_list:
            upload_path = os.path.abspath(folder_name)
            for path, subdirs, files in os.walk(upload_path):
                for name in files:
                    filesList.append(path)
                    nameList.append(name)
                    file_stats = os.stat(os.path.join(path, name))
                    filesizeList.append(f"{round(file_stats.st_size / (1024 * 1024),2)} MB")

        upload_queue_dataset = pd.DataFrame({'file_path': filesList,  'file_name':nameList, 'filesize': filesizeList })
        upload_queue_dataset["front_or_rear_folder"] = upload_queue_dataset["file_path"].apply(lambda x: self.getsubdir(x))
        upload_queue_dataset["file_uploaded"] = False

    def get_random_string(self, length):
        # choose from all lowercase letter
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        
        return result_str

    def FTP_upload_files(self, selected_folder, footage_front, footage_rear, Total_Count):
        batch_id = self.get_random_string(10)
        print("+++++++++++++++ Start uploading the Front Footage Folder ++++++++++++++++++")
        try:
            ftps.cwd(f'{os.getenv("FTP_server_folder_path")}{selected_folder}/F')
            file_counter = 1
            for filename in os.listdir(footage_front):
                file_to_upload = os.path.join(footage_front, filename)
                # checking if it is a file
                if os.path.isfile(file_to_upload):
                    footage_front_file = file_to_upload
                    filename_without_path = self.strip_folder_name(file_to_upload)
                    print(f"{filename_without_path} -- {file_counter} of {Total_Count}")
                    filesize = int(os.path.getsize(footage_front_file))
                    TheFile = open(footage_front_file, 'rb')
                    if(footage_front_file not in ftps.nlst()):
                        with tqdm(unit = 'blocks', unit_scale = True, leave = False, miniters = 1, desc = f'Uploading {selected_folder} {filename_without_path}......', total = filesize) as tqdm_instance:
                            ftps.storbinary(f'STOR {filename_without_path}', TheFile , 2048, callback = lambda sent: tqdm_instance.update(len(sent)))
                            upload_queue_dataset["file_uploaded"] = np.where(upload_queue_dataset["file_name"] == filename, True, False)
                            file_counter += 1
                    else:
                        file_counter += 1

        except Exception as e:
            upload_queue_dataset["file_uploaded"] = np.where(upload_queue_dataset["file_name"] == filename, "Error", False)
            upload_queue_dataset.to_csv(f"file_listing_{batch_id}.csv")
            print(e)


        front_files = []
        try:
            front_files = ftps.mlsd()
        except FTP_TLS.error_perm as resp:
            if str(resp) == "550 No files found":
                print ("No files in this directory")
            else:
                raise

        files_not_uploaded_front = self.chk_file_upload_for_batch(selected_folder, front_files, "F")

        print("+++++++++++++++ Start uploading the Rear Footage Folder ++++++++++++++++++")
        try:
            ftps.cwd(f'{os.getenv("FTP_server_folder_path")}{selected_folder}/R')
            for filename in os.listdir(footage_rear):
                file_to_upload = os.path.join(footage_rear, filename)
                # checking if it is a file
                if os.path.isfile(file_to_upload):
                    footage_rear_file = file_to_upload
                    filename_without_path = self.strip_folder_name(file_to_upload)
                    print(f"{filename_without_path} -- {file_counter} of {Total_Count}")
                    filesize = int(os.path.getsize(footage_rear_file))
                    TheFile = open(footage_rear_file, 'rb')
                    if(footage_front_file not in ftps.nlst()):
                        with tqdm(unit = 'blocks', unit_scale = True, leave = False, miniters = 1, desc = f'Uploading {selected_folder} {filename_without_path}......', total = filesize) as tqdm_instance:
                            ftps.storbinary(f'STOR {filename_without_path}', TheFile , 2048, callback = lambda sent: tqdm_instance.update(len(sent)))
                            upload_queue_dataset["file_uploaded"] = np.where(upload_queue_dataset["file_name"] == filename, True, False)
                            file_counter += 1
                    else:
                        file_counter += 1

        except Exception as e:
            upload_queue_dataset["file_uploaded"] = np.where(upload_queue_dataset["file_name"] == filename, "Error", False)
            upload_queue_dataset.to_csv(f"file_listing_{batch_id}.csv")
            print(e)

        rear_files = []
        try:
            rear_files = ftps.mlsd()
        except FTP_TLS.error_perm as resp:
            if str(resp) == "550 No files found":
                print ("No files in this directory")
            else:
                raise

        files_not_uploaded_rear = self.chk_file_upload_for_batch(selected_folder, rear_files, "R")

        if files_not_uploaded_front == "" or files_not_uploaded_rear == "":
            print("+++++++++++++++ Following files are not uploaded in this batch. Please try again ++++++++++++++++++")

        if files_not_uploaded_front == "":
            print("Front Camera Footage Files")
            print(files_not_uploaded_front)
        elif files_not_uploaded_rear == "":
            print("Rear Camera Footage Files")
            print(files_not_uploaded_rear)

        print(f"All {Total_Count} files for {selected_folder} uploaded successfully!!!")
        print("Writing the Batch File.....")
        upload_queue_dataset.to_csv(f"file_listing_{batch_id}.csv")

    def get_number_days(self, path):
        files = os.listdir(path)
        today = date.today()
        files_last_week = []
        for f in files:
            complete_path = f"{path}/{f}"
            if(os.path.isdir(complete_path)):
                st_time = os.path.getctime(complete_path)
                dt = datetime.fromtimestamp(st_time)
                created_date = dt.date()
                date_difference = today - created_date

                if(date_difference.days <= 7):
                    files_last_week.append(f)

        
        return files_last_week
    
    def chk_folder_present(self, folder_name):
        folder_present = False
        if(ftps == None):
            self.connect_ftp_server()

        ftps.cwd(os.getenv("FTP_server_folder_path"))
        if(folder_name in ftps.nlst()):
            folder_present = True

        return folder_present
    
    def FTP_close_connection(self):
        global ftps
        ftps.close()
        ftps = None
        print("Successfully logged out of Thecus NAS")