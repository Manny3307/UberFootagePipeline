import json
import os, ntpath, sys, traceback
from shutil import copyfile
import glob
import shutil

UberLogString = []

HTMLDirName = ""
CSVDirName = ""


class FolderFunction:

    def __init__(self):
        # Load the Config JSON file from the config folder and read the respective values
        try:
            global FolderConfigJSON, CreateBasePath
            FolderConfigJSON = open('./config/folder_config.json')
            #CreateBasePath = "/NAS_Public/Backup/Uber_Footage/"
            CreateBasePath = "./contr"
        except:
            pass
            #objUberExceptionLogging.UberLogException(ExceptionMessages["Exceptions"]["folder_config"], True, True)

        #UberLogString.append(SuccessMessages["Messages"]["folder_config"])    

    #Create Folder Structure for the New Cleaning Record Fortnight
    #Create Folder in "Uber Cleaning Record" directory for the given fortnight in the date format.
    def Folder_walk(self,folderDict, path):
        '''Function to create the folder structure recursively'''
        paths = []
        
        # we only continue if the value is not None
        if folderDict:
            for folder, subDict in folderDict.items():

                # making sure the path will have forward slashes
                # especially necessary on windows
                
                pathTemp = os.path.normpath(os.path.join(path, folder))
                pathTemp = pathTemp.replace("\\", "/")
                
                #add the current found path to the list
                paths.append(pathTemp)
                
                # we call the the function again to go deeper
                # in the dictionary
                paths.extend(self.Folder_walk(subDict, pathTemp))

        print(paths)
        return paths

    #Check if all the folders are created properly or not.
    def checkFolderStructure(self, folderPaths):
        foldernotcreated = []
        
        for folder in folderPaths:
            if os.path.exists(folder) == False:
                foldernotcreated.append(folder) 
        
        return foldernotcreated

    #Create Folder Structure for the New Cleaning Record Fortnight
    #Create Folder in "Uber Cleaning Record" directory for the given fortnight in the date format.
    def create_folder_structure(self, folderName):
        '''Create the folder structure according the JSON from Config folder.'''
        #Delete the folder structure if already exists. 
        #self.delete_folder_structure(folderName)
        
        
        try:
            path = "./config/FolderStructure.json"
            folders = {}
            replaced_folder = {}
            with open(path, 'r') as f:
                folders = json.load(f)

            
            replaced_folder[folderName] = folders["folder_name"]
            folderPaths = self.Folder_walk(replaced_folder, "./contr")
            print(folderPaths)
            for folder_name in folderPaths:
                if not (os.path.exists(folder_name)):
                    os.makedirs(folder_name)
                    print(f"Folder {ntpath.basename(folder_name)} created successfully!!!")
                else:
                    print(f"Folder {ntpath.basename(folder_name)} already exists!!!")

            folderlist = self.checkFolderStructure(folderPaths)
            

            if not folderlist:
                print("Folder Structure Created Successfully!!!")
            else:
                check_for_error = True
                print("Folder Structure failed the configuration!!!")
                print("Following Folder(s) not present in the folder structure!!!")
                print("==========================================================")
                print(folderlist)
                print("ERROR: Folder structure cannot be created.")
                print("Exiting the Program!!!")
                UberLogString.append("Folder Structure failed the configuration!!!")
                sys.exit()

        except:
            pass
            #objUberExceptionLogging.UberLogException("ERROR: Folder structure cannot be created.", True, True)

        
        return UberLogString

    #Funtion to copy the template files in the respective folders
    def copy_files_to_dest_folder(self, Templatefiles_src, DirName):
        try:
            if Templatefiles_src != None:
                for temp_files in Templatefiles_src:
                    src_files = temp_files
                    dest_files = os.path.join(DirName, ntpath.basename(temp_files))
                    if not os.path.exists(dest_files):
                        copyfile(src_files, dest_files)
                        print("File " , dest_files ,  " copied successfully!!!")
                    else:
                        print("File " , dest_files ,  " already exists")
        except:
            pass
            #objUberExceptionLogging.UberLogException("ERROR: File(s) cannot be copied in required folders.", True, True)
    
    '''#Delete the folder structure of the provided folder.
    def delete_folder_structure(self, folderName):
        try:
            shutil.rmtree(f"{CreateBasePath}/{folderName}")
            print(f"{folderName} deleted successfully!!!!")
        except:
            print(f"No folder named {folderName} found.")'''