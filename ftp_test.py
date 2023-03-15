#from ftplib import FTP_TLS
import ftplib
from tqdm import tqdm
import os, time
from datetime import datetime, date
from ftp_footage_helper import ftp_helpers
import pandas as pd
import numpy as np

ftps = ftplib.FTP()
ftps.connect("mannyangel.tplinkdns.com",21)
ftps.login(user='admin', passwd = 'Mallory@486')
ftps.cwd("/G/Backup")
print(ftps.nlst())


'''files = []

try:
    files = ftps.mlsd()
except FTP_TLS.error_perm as resp:
    if str(resp) == "550 No files found":
        print ("No files in this directory")
    else:
        raise

def chk_file_FTP(filename, fileswithsize):
    chk_file = False
    for temp in fileswithsize:
        for temp1 in temp:
            if(temp1 == filename):
                chk_file = True

    return chk_file


def chk_file_upload_for_batch(foldername):
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

    footage_path = f"/home/manny/Footage/{foldername}/F"
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
            if chk_file_FTP(mkey, fileswithsize) == False:
                files_not_uploaded.append(mkey)
                
                
    return files_not_uploaded


def get_number_days(path):
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

            if(date_difference.days <= 1):
                files_last_week.append(f)

    return files_last_week

#test = get_number_days("/home/manny/Footage")
#print(test)

obj_ftp = ftp_helpers()'''

#test = obj_ftp.get_number_days("/home/manny/footage_test")

#print(test)

'''def getsubdir(file_path):
    subdir = str(file_path).split("/")
    return subdir[len(subdir) - 1]

filesList= []
nameList= []
filesizeList= []
subdir_list = []
folders_list = next(os.walk("/home/manny/Footage"))[1]

for temp in folders_list:
    subfolders = [f.path for f in os.scandir(os.path.join("/home/manny/Footage",temp)) if f.is_dir()]
    for sub_fldr in subfolders:
        subdir_list.append(sub_fldr)
    
    subfolders = ""

print(subdir_list)

def generate_upload_queue(folder_list):
    for folder_name in folder_list:
        upload_path = os.path.abspath(folder_name)
        for path, subdirs, files in os.walk(upload_path):
            for name in files:
                filesList.append(path)
                nameList.append(name)
                file_stats = os.stat(os.path.join(path, name))
                filesizeList.append(f"{round(file_stats.st_size / (1024 * 1024),2)} MB")    

files_lst = generate_upload_queue(subdir_list)

upload_queue_dataset = pd.DataFrame({'file_path': filesList,  'file_name':nameList, 'filesize': filesizeList })
upload_queue_dataset["front_or_rear_folder"] = upload_queue_dataset["file_path"].apply(lambda x: getsubdir(x))
upload_queue_dataset["file_uploaded"] = False
upload_queue_dataset["file_uploaded"] = np.where(upload_queue_dataset["file_name"] == 'FILE230226-012048F.NMEA', True, False)
print(upload_queue_dataset.head(10))
upload_queue_dataset.to_csv("file_listing.csv")

'''
#FILE230226-012048F.NMEA 


'''def resume_upload(folder_name):
    if(folder_name in ftps.nlst()):
        pass


    return True    
'''


'''ftps.close()
ftps = None'''