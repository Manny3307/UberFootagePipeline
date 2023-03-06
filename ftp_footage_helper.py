from ftplib import FTP_TLS
from tqdm import tqdm
import os
from dotenv import load_dotenv
from pathlib import Path

class ftp_helpers:
    
    def __init__(self):
        global folder_path, folder_dict, ftps
        dotenv_path = Path('.env')
        load_dotenv(dotenv_path=dotenv_path)
        folder_path = os.getenv("FTP_folder_path")
        ftps = FTP_TLS()

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
        try:
            print("Attempting  to login to Thecus NAS")
            ftps.connect(os.getenv("FTP_server"),int(os.getenv("FTP_server_port")))
            ftps.login(user=os.getenv("FTP_server_login"), passwd = os.getenv("FTP_server_password"))
            print("Successfully logged in to Thecus NAS")
        except:
            print("Login Failed!!!!")

    def FTP_create_folder_structure(self, folder_name):
        try:
            if folder_name not in ftps.nlst():
                print(f"Attempting to create the folder structure for {folder_name}")
                ftps.cwd('/NAS_Public/Backup/Uber_Footage/')
                ftps.mkd(f'/NAS_Public/Backup/Uber_Footage/{folder_name}')
                ftps.mkd(f'/NAS_Public/Backup/Uber_Footage/{folder_name}/F')
                ftps.mkd(f'/NAS_Public/Backup/Uber_Footage/{folder_name}/R')
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

    def FTP_upload_files(self, selected_folder, footage_front, footage_rear, Total_Count):
        print("+++++++++++++++ Start uploading the Front Footage Folder ++++++++++++++++++")
        ftps.cwd(f'/NAS_Public/Backup/Uber_Footage/{selected_folder}/F')
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
                with tqdm(unit = 'blocks', unit_scale = True, leave = False, miniters = 1, desc = f'Uploading {filename_without_path}......', total = filesize) as tqdm_instance:
                    ftps.storbinary(f'STOR {filename_without_path}', TheFile , 2048, callback = lambda sent: tqdm_instance.update(len(sent)))
                    file_counter += 1

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
        ftps.cwd(f'/NAS_Public/Backup/Uber_Footage/{selected_folder}/R')
        for filename in os.listdir(footage_rear):
            file_to_upload = os.path.join(footage_rear, filename)
            # checking if it is a file
            if os.path.isfile(file_to_upload):
                footage_rear_file = file_to_upload
                filename_without_path = self.strip_folder_name(file_to_upload)
                print(f"{filename_without_path} -- {file_counter} of {Total_Count}")
                filesize = int(os.path.getsize(footage_rear_file))
                TheFile = open(footage_rear_file, 'rb')
                with tqdm(unit = 'blocks', unit_scale = True, leave = False, miniters = 1, desc = f'Uploading {filename_without_path}......', total = filesize) as tqdm_instance:
                    ftps.storbinary(f'STOR {filename_without_path}', TheFile , 2048, callback = lambda sent: tqdm_instance.update(len(sent)))
                    file_counter += 1

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
    
    def FTP_close_connection(self):
        ftps.close()
        ftps = None