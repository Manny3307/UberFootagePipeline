from ftplib import FTP_TLS
from tqdm import tqdm
import os, time
from datetime import datetime, date

ftps = FTP_TLS()
ftps.connect("192.168.0.3",2100)
ftps.login(user='admin', passwd = 'Angel@1980')


files = []

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

            if(date_difference.days <= 7):
                files_last_week.append(f)

    return files_last_week

test = get_number_days("/home/manny/Footage")
print(test)

ftps.close()
ftps = None