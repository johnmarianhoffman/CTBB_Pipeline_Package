# CTBB_Pipeline_Package is GPU Queuing Software
# Copyright (C) 2017 John Hoffman

# ctbb_pipeline_library.py (this file) is part of CTBB_Pipeline and CTBB_Pipeline_Package.
# 
# CTBB_Pipeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# CTBB_Pipeline and CTBB_Pipeline_Package is distributed in the hope
# that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with CTBB_Pipeline and CTBB_Pipeline_Package.  If not, see
# <http://www.gnu.org/licenses/>.

import sys
import os
import shutil
import logging
from subprocess import call
import time
from time import strftime
from glob import glob

import random
import tempfile
from hashlib import md5

import traceback

#import pypeline as pype
#from pypeline import mutex
from CTBB_Pipeline import pypeline as pype
from CTBB_Pipeline.pypeline import mutex

class ctbb_pipeline_library:
    path=None;
    mutex_dir=None;    
    raw_dir=None;
    recon_dir=None;
    log_dir=None;

    def __init__(self,path):
        self.path=path;
        self.mutex_dir=os.path.join(path,'.proc','mutex');
        self.raw_dir=os.path.join(path,'raw');
        self.recon_dir=os.path.join(path,'recon');
        self.log_dir=os.path.join(path,'log');
        
        if not self.is_library():
            self.initialize_new_library()
        else:
            if not self.is_valid():
                self.repair()
        
            self.load()

    def initialize_new_library(self):
        touch(os.path.join(self.path,'.ctbb_pipeline_lib'))
        touch(os.path.join(self.path,'case_list.txt'))
        touch(os.path.join(self.path,'recons.csv'))
        touch(os.path.join(self.path,'README.txt'))
        os.mkdir(os.path.join(self.path,'raw'))
        os.mkdir(os.path.join(self.path,'recon'))
        os.mkdir(os.path.join(self.path,'log'))
        os.mkdir(os.path.join(self.path,'qa'))
        os.mkdir(os.path.join(self.path,'eval'))
        os.mkdir(os.path.join(self.path,'.proc'))
        os.mkdir(os.path.join(self.path,'.proc','mutex'))
        touch(os.path.join(self.path,'.proc','queue'))
        touch(os.path.join(self.path,'.proc','active'))        
        touch(os.path.join(self.path,'.proc','done'))
        touch(os.path.join(self.path,'.proc','error'))
        
    def is_library(self):
        if os.path.exists(os.path.join(self.path,'.ctbb_pipeline_lib')):
            tf=True
        else:
            tf=False            
        return tf

    def is_valid(self):

        tf = True;

        tf = tf and os.path.exists(os.path.join(self.path,'.ctbb_pipeline'))
        tf = tf and os.path.exists(os.path.join(self.path,'case_list.txt'))
        tf = tf and os.path.exists(os.path.join(self.path,'recons.csv'))
        tf = tf and os.path.exists(os.path.join(self.path,'README.txt'))
        tf = tf and os.path.isdir(os.path.join(self.path,'raw'))
        tf = tf and os.path.isdir(os.path.join(self.path,'recon'))
        tf = tf and os.path.isdir(os.path.join(self.path,'log'))
        tf = tf and os.path.isdir(os.path.join(self.path,'qa'))
        tf = tf and os.path.isdir(os.path.join(self.path,'eval'))        
        tf = tf and os.path.isdir(os.path.join(self.path,'.proc'))
        tf = tf and os.path.isdir(os.path.join(self.path,'.proc','mutex'))        
        tf = tf and os.path.exists(os.path.join(self.path,'.proc','queue'))
        tf = tf and os.path.exists(os.path.join(self.path,'.proc','active'))        
        tf = tf and os.path.exists(os.path.join(self.path,'.proc','done'))
        tf = tf and os.path.exists(os.path.join(self.path,'.proc','error'))

        return tf;

    def load(self):
        logging.debug('Nothing to be done to load library currently')
        # Check the case list vs raw data files present?

        # Update recon list from files present?
                                                           
    def repair(self):
        touch(os.path.join(self.path,'.ctbb_pipeline_lib'))
        touch(os.path.join(self.path,'case_list.txt'))
        touch(os.path.join(self.path,'recons.csv'))
        touch(os.path.join(self.path,'README.txt'))
        
        if not os.path.isdir(os.path.join(self.path,'raw')):
            os.mkdir(os.path.join(self.path,'raw'))
        if not os.path.isdir(os.path.join(self.path,'recon')):            
            os.mkdir(os.path.join(self.path,'recon'))
        if not os.path.isdir(os.path.join(self.path,'log')):
            os.mkdir(os.path.join(self.path,'log'))
        if not os.path.isdir(os.path.join(self.path,'qa')):
            os.mkdir(os.path.join(self.path,'qa'))
        if not os.path.isdir(os.path.join(self.path,'eval')):
            os.mkdir(os.path.join(self.path,'eval'))                                 
        if not os.path.isdir(os.path.join(self.path,'.proc')):            
            os.mkdir(os.path.join(self.path,'.proc'))
        if not os.path.isdir(os.path.join(self.path,'.proc','mutex')):            
            os.mkdir(os.path.join(self.path,'.proc','mutex'))
            
        touch(os.path.join(self.path,'.proc','queue'))
        touch(os.path.join(self.path,'.proc','active'))        
        touch(os.path.join(self.path,'.proc','done'))
        touch(os.path.join(self.path,'.proc','error'))

    def locate_raw_data(self,filepath):
        case_list_mutex=mutex('case_list',self.mutex_dir)
        case_list_mutex.lock()
        
        # Returns either a hash value (of raw file) or "False" if raw data unavailable
        case_list=self.__get_case_list__()

        # Check if we already have file in library
        if filepath in case_list.keys():
            logging.info('File %s (%s) found case library' % (filepath,case_list[filepath]))
            case_id=case_list[filepath]
        else:
            if os.path.exists(filepath):
                local_file_info=self.__get_local_file_hash__(filepath)

                digest=local_file_info[0]
                tmp_path=local_file_info[1]
                if not (digest in case_list.keys()):
                    logging.info('Adding raw data file to library')
                    self.__add_raw_data__(filepath,tmp_path,digest)
                case_id=digest;
            else:
                # Requested file does not exist
                logging.info('Requested raw data file does not exist')
                case_id=False

        case_list_mutex.unlock();
        
        return case_id

    def locate_reduced_dose_data(self,filepath,dose):
        logging.info('Checking for reduced dose data')

        exit_status=0

        case_list_mutex=mutex('case_list',self.mutex_dir)
        case_list_mutex.lock()

        case_list=self.__get_case_list__()

        case_id=case_list[filepath]
        logging.info('Case ID for current case is %s' % case_id)
        full_dose_filepath=os.path.join(self.raw_dir,'100',case_id)
        reduced_dose_filepath=os.path.join(self.raw_dir,str(dose),case_id)

        # If reduction dir doesn't exist, create it.
        if not os.path.isdir(os.path.join(self.raw_dir,str(dose))):
            os.mkdir(os.path.join(self.raw_dir,str(dose)))
        
        if os.path.exists(reduced_dose_filepath):
            logging.info('Reduced dose data found')
        else:
            logging.info('Reduced dose data not found.  Running dose reduction tool.')
            system_call="ctbb_simdose %s %s %s" % ( full_dose_filepath,str(dose),reduced_dose_filepath )
            logging.info('Sending the following call to system: %s' % system_call);
            exit_status=self.__child_process__(system_call)
            logging.info('Dose reduction job exited with exit status %s' % str(exit_status))
            
        case_list_mutex.unlock()

        return exit_status

    def get_recon_list(self):
        # Returns a list of dictionaries
        import csv
        csv_filepath=os.path.join(self.path,'recons.csv')

        # CSV reader method
        # Create a list of dictionaries
        recon_list=[]
        with open(csv_filepath,'r') as f:            
            reader=csv.DictReader(f);
            for row in reader:
                recon_list.append(row)

        return recon_list
                
    def refresh_recon_list(self):
        case_list=self.__get_case_list__()
        
        # Get list of all IMG files in recon directory
        #paths=glob(os.path.join(self.path,'recon','*/*/*.img'))
        print("Searching for IMG files...")
        paths=glob(os.path.join(self.path,'recon','*','*','*','*.img'))

        if not paths:
            print("Searching for HR2 files...")
            paths=glob(os.path.join(self.path,'recon','*','*','*','*.hr2'))
        
        # Parse paths into sensible things:
        filenames=[]
        csv_entries=[]
        
        for p in paths:
            curr_file=os.path.basename(p)
            curr_file=os.path.splitext(curr_file)[0]
            csv_entries.append(curr_file.split('_'))

        for i in range(len(csv_entries)):
            curr_item=csv_entries[i]
            # Clean up dose kernel and slice thickness entries
            curr_item[1]=curr_item[1].strip('d')  # dose
            curr_item[2]=curr_item[2].strip('k')  # kernel
            curr_item[3]=curr_item[3].strip('st') # slice thickness
            
            curr_item.insert(0,case_list[curr_item[0]]) # inserts the original case filepath at beginning of list
            curr_item.append(paths[i]) # appends full path to reconstruction at end of list

            csv_entries[i]=curr_item

        import csv        
        with open(os.path.join(self.path,'recons.csv'),'w',newline='') as f:
        #with open(os.path.join(self.path,'recons.csv'),'w') as f:            
            wr=csv.writer(f,quoting=csv.QUOTE_MINIMAL,lineterminator=os.linesep)
            wr.writerow(['org_raw_filepath','pipeline_id','dose','kernel','slice_thickness','img_series_filepath'])
            for c in csv_entries:
                wr.writerow(c)
            
    def __add_raw_data__(self,filepath_org,filepath_tmp,digest):
        out_dir=os.path.join(self.path,'raw','100')
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        
        #os.rename(filepath_tmp,os.path.join(out_dir,digest))
        shutil.move(filepath_tmp,os.path.join(out_dir,digest))
        self.__add_to_case_list__(filepath_org,digest)

    def __add_to_case_list__(self,filepath,digest):
        logging.info("Adding %s:%s to case list" % (digest,filepath))
        with open(os.path.join(self.path,'case_list.txt'),'a') as f:
            f.write("%s,%s\n" % (filepath,digest))
        
    def __get_case_list__(self):
        # Returns current case list as dictionary with filepaths as keys and file hashes as values
        case_list_dict={}

        #print(os.path.abspath(self.path))
        
        with open(os.path.join(self.path,'case_list.txt'),'r') as f:
            case_list=f.read().splitlines()
            for i in range(len(case_list)):
                if case_list:
                    curr_case=case_list[i].split(',')
                    digest=curr_case[1]
                    filepath=curr_case[0]
                    case_list_dict[digest]=filepath;
                    case_list_dict[filepath]=digest;

        return case_list_dict

    def __get_local_file_hash__(self,filepath):
        # Copy file to temporary location
        tmp_filepath=os.path.join(tempfile.mkdtemp(),str(random.getrandbits(128)))
        logging.debug('Temporary path to file: %s' % tmp_filepath)
        shutil.copy(filepath,tmp_filepath)
        logging.info("Computing hash of %s" % filepath)
        
        with open(tmp_filepath,'rb') as f:
            digest=md5(f.read()).hexdigest()

        return (digest,tmp_filepath)

    def __child_process__(self,c):
        import subprocess
        exit_code=0
        devnull=open('/dev/null','w')        
        exit_code=os.system("%s > /dev/null 2>&1" % c); # Blocking call? // 
        #subprocess.Popen(c.split(' '),stderr=devnull,stdout=devnull) # non-blocking
        logging.debug('System call exited with status %s' % str(exit_code))
        return exit_code
                  
def touch(path):
    with open(path,'a'):
        os.utime(path,None);

if __name__=="__main__":
    lib_path=sys.argv[1]
    ctbb_lib=ctbb_pipeline_library(lib_path)
    ctbb_lib.refresh_recon_list()
