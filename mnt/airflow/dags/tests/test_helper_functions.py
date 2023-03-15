import unittest
import os, sys
from dags.ftp_footage_helper import ftp_helpers

obj_ftp = ftp_helpers()

class test_helper_functions(unittest.TestCase):

    def test_count_files(self):
        count = obj_ftp.count_files("/home/manny/Uber_Statements")
        self.assertEqual(count,11)
        
    def test_strip_folder_name(self):
        folder_name = obj_ftp.strip_folder_name("/home/manny/Uber_Statements")
        self.assertEqual(folder_name,'Uber_Statements')

    '''def test_get_folder_name(self):
        folder_name = ""
        obj_ftp.get_folder_name
        for folder_name_counter in folder_dict:
            for folder_values in folder_name_counter.items():
                if str(folder_values[0]) == counter:
                    folder_name = folder_values[1]

        return folder_name
        
'''
