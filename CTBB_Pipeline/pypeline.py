# Pypeline.py: Class library for items common to multiple pipeline tools

import sys
import os
import time

import logging
import yaml

from subprocess import call

import numpy as np

path_file="\\\skynet\cvib\PechinTest2\scripts\paths.yml"

def test_func():
    print("pypeline successfully loaded")

def touch(path):
    with open(path,'a'):
        os.utime(path,None);

def load_paths():
    try:    
        with open('paths.yml','r') as f:
            path_dict=yaml.load(f)
    except:
        with open(path_file,'r') as f:
            path_dict=yaml.load(f)
        
    return path_dict

def load_config(filepath):

    logging.info('Loading configuration file: %s' % filepath)

    # Load pipeline run from YAML configuration file 
    with open(filepath,'r') as f:
        yml_string=f.read();

    config_dict=yaml.load(yml_string)

    # We only require that a case list and output library be defined
    if ('case_list' not in config_dict.keys()) or ('library' not in config_dict.keys()):
        logging.error('"case_list" and "library" are required fields in ctbb_pipeline configuration file and one or the other was not found. Exiting."')
        config_dict={}

    else:
        # Check for optional fields. Set to defaults as needed.
        # Doses
        if ('doses' not in config_dict.keys()):
            config_dict['doses']=[100,10]
        
        # Slice Thickness
        if ('slice_thicknesses' not in config_dict.keys()):
            config_dict['slice_thicknesses']=[0.6,5.0]

        # Kernel
        if ('kernels' not in config_dict.keys()):
            config_dict['kernels']=[1,3]

        if not os.path.isdir(config_dict['library']):
            os.makedirs(config_dict['library'])
            logging.warning('Library directory does not exist, creating.')
            
        # Verify that the case list and library directory exist
        if not os.path.exists(config_dict['case_list']):
            logging.error('Specified case_list does not exist.')
            #config_dict={}
            
    return config_dict
        

class mutex:
    name=None;
    mutex_dir=None;
    mutex_file=None;

    def __enter__(self,name,mutex_dir):
        self.name=name
        self.mutex_dir=mutex_dir
        self.mutex_file=os.path.join(mutex_dir,name)
        self.lock()

    def __exit__(self):
        os.remove(self.mutex_file)
        
    def __init__(self,name,mutex_dir):
        self.name=name
        self.mutex_dir=mutex_dir
        self.mutex_file=os.path.join(mutex_dir,name)
        
    def lock(self):
        # If mutex alread locked, wait for other process to unlock
        while os.path.exists(self.mutex_file):
            logging.debug('Mutex ' + self.name  + ' locked. Sleeping and trying again')
            time.sleep(5)
        touch(self.mutex_file)

    def unlock(self):
        os.remove(self.mutex_file)

    def check_state(self):
        state=os.path.exists(self.mutex_file)

        if state==True:
            logging.debug('Mutex file: %s LOCKED' % str(self.mutex_file))
        else:
            logging.debug('Mutex file: %s UNLOCKED' % str(self.mutex_file))

        return state

class case_list:
    filepath=None;
    case_list=None;
    prmbs=[];
    prmbs_raw=[];

    def __init__(self,filepath):
        self.filepath=filepath
        accepted_filetypes=['.ctd','.ptr','.ima','.txt']
        # Get file type and open accordingly
        ext=os.path.splitext(self.filepath)
        ext=ext[1].lower();

        logging.info('Detected file extension: ' + ext)

        self.case_list=[];
        
        if (ext in accepted_filetypes):
            logging.info('File extension accepted')
            
            if ext == '.txt':
                with open(self.filepath,'r') as f:
                    self.case_list=f.read().splitlines()
            else:
                self.case_list.append(self.filepath)
        else:
            self.error_dialog('Unrecognized filetype.  Accepted filetypes are IMA, PTR, CTD, and TXT')
            logging.error('User tried to load an unrecognized filetype:' + self.filepath)
            return;
        
    def get_prmbs(self):
        logging.info('Generating parameter files and reading into pipeline');

        prmbs=[];

        for f in self.case_list:
    
            if not f:
                continue
            
            # Generate the parameter file
            devnull=open(os.devnull,'w')
            call(['ctbb_info','-b',f],stdout=devnull,stderr=devnull);
    
            # Open the parameter file and read into pipeline
            with open(f+'.prmb') as f_prmb:
                self.prmbs_raw.append(f_prmb.read())
                prmbs.append(f_prmb.read())

        # Sanitize and parse into dictionaries
        for s in prmbs:
            s=s.replace('\t','  ')
            s=s.replace('%','#')
            self.prmbs.append(yaml.load(s))


class study_directory:
    path=None
    log_dir=None;
    img_dir=None;
    
    def __init__(self,path):
        self.path=path
        self.log_dir=os.path.join(self.path,'log')
        self.img_dir=os.path.join(self.path,'img')
        
        if not self.is_study():
            self.initialize_new_study()
        else:
            if not self.is_valid():
                self.repair()

            self.load()

    def initialize_new_study(self):
        touch(os.path.join(self.path,'.ctbb_pipeline_study'))
        os.mkdir(os.path.join(self.path,'img'))
        os.mkdir(os.path.join(self.path,'seg'))
        os.mkdir(os.path.join(self.path,'log'))
        os.mkdir(os.path.join(self.path,'qi_raw'))
        os.mkdir(os.path.join(self.path,'ref'))
        os.mkdir(os.path.join(self.path,'eval'))
        os.mkdir(os.path.join(self.path,'qa'))

    def is_study(self):
        if os.path.exists(os.path.join(self.path,'.ctbb_pipeline_study')):
            tf=True
        else:
            tf=False
        return tf

    def is_valid(self):
        tf=True

        tf = tf and os.path.isdir(os.path.join(self.path,'img'))
        tf = tf and os.path.isdir(os.path.join(self.path,'seg'))
        tf = tf and os.path.isdir(os.path.join(self.path,'log'))
        tf = tf and os.path.isdir(os.path.join(self.path,'qi_raw'))
        tf = tf and os.path.isdir(os.path.join(self.path,'ref'))
        tf = tf and os.path.isdir(os.path.join(self.path,'eval'))
        tf = tf and os.path.isdir(os.path.join(self.path,'qa'))

        return tf;


    def repair(self):
        if not os.path.isdir(os.path.join(self.path,'img')):
            os.mkdir(os.path.join(self.path,'img'))
        if not os.path.isdir(os.path.join(self.path,'seg')):
            os.mkdir(os.path.join(self.path,'seg'))
        if not os.path.isdir(os.path.join(self.path,'log')):
            os.mkdir(os.path.join(self.path,'log'))
        if not os.path.isdir(os.path.join(self.path,'qi_raw')):
            os.mkdir(os.path.join(self.path,'qi_raw'))
        if not os.path.isdir(os.path.join(self.path,'ref')):
            os.mkdir(os.path.join(self.path,'ref'))
        if not os.path.isdir(os.path.join(self.path,'eval')):
            os.mkdir(os.path.join(self.path,'eval'))
        if not os.path.isdir(os.path.join(self.path,'qa')):
            os.mkdir(os.path.join(self.path,'qa'))

    def load(self):
        logging.info("Nothing to be done to load study_directory")
            
#    def descriptions(self):
#        def printout(d,f,s):
#            with open(os.path.join(self.path,f),'w') as fid:
#                fid.write(s);

class pipeline_img_series:
    from collections import namedtuple    
    fields=('StartPos'
            ' EndPos'
            ' DataCollectionDiameter'
            ' ReconstructionDiameter'
            ' Width'
            ' Height'
            ' ConvolutionKernel'
            ' ImagePositionPatient'
            ' ImageOrientationPatient'
            ' DataCollectionCenterPatient'
            ' ReconstructionTargetCenterPatient'
            ' SliceThickness'
            ' SpiralPitchFactor'
            ' TableFeedPerRotation'
            ' SingleCollimationWidth'
            ' TotalCollimationWidth'
            ' NoOfSlices'
    )    
    header=namedtuple('header',fields)
    img_filepath=None
    prm_filepath=None
    stack=None
    
    def __init__(self,img_filepath,prm_filepath):
        ### Constructor reads PRM file and loads metadata. Note that image data is NOT
        ### loaded by default. This is done through the to_memory() method.

        # Copy our filepaths into the object
        self.img_filepath=img_filepath
        self.prm_filepath=prm_filepath
        
        # Load up the "header" information
        # I.E. Map the parameter file dictionary over to our headers structure
        # Note: naming conventions are those given in MATLAB where applicable
        # The MATLAB naming conventions follow the DICOM standard.
        with open(self.prm_filepath,'r',encoding='utf8') as f:
            #print(os.path.abspath(self.prm_filepath))
            logging.error(self.prm_filepath)
            string=f.read()
            string=string.replace('\t',' ') # Pull out the tabs in case we're using old CTBangBang stuff
            prm=yaml.load(string)

        self.header.Width                             = prm['Nx']
        self.header.Height                            = prm['Ny']            
        self.header.StartPos                          = prm['StartPos']
        self.header.EndPos                            = prm['EndPos']
        self.header.DataCollectionDiameter            = prm['AcqFOV']
        self.header.ReconstructionDiameter            = prm['ReconFOV']
        self.header.ConvolutionKernel                 = prm['ReconKernel']
        self.header.ImagePositionPatient              = None
        self.header.ImageOrientationPatient           = prm['ImageOrientationPatient']
        self.header.DataCollectionCenterPatient       = None
        self.header.ReconstructionTargetCenterPatient = (prm['Xorigin'],prm['Yorigin'],prm['StartPos'])
        self.header.SliceThickness                    = prm['SliceThickness']
        self.header.TableFeedPerRotation              = prm['PitchValue']
        self.header.SingleCollimationWidth            = prm['CollSlicewidth']
        self.header.TotalCollimationWidth             = float(prm['Nrows'])*prm['CollSlicewidth']
        self.header.SpiralPitchFactor                 = self.header.TableFeedPerRotation/self.header.TotalCollimationWidth

        # Determine the number of slices in the image
        with open(self.img_filepath,'r') as f:
            f.seek(0,os.SEEK_END)
            eof=f.tell()
            n_pixels=eof/4 # Pixels are single-precision floats (4 bytes)
            self.header.NoOfSlices=int(int(n_pixels)/(int(self.header.Width)*int(self.header.Height)))

        # Print a copy of the mapped metadata
        self.fields=self.fields.split(' ')
        for f in self.fields:
            print('{}: {}'.format(f,eval('self.header.{}'.format(f))))
        
    def to_memory(self):
        ### Method to load the image stack into memory (as a numpy array)
        with open(self.img_filepath,'r') as f:
            f.seek(0,os.SEEK_SET);
            self.stack=np.fromfile(f,'float32')
        
        #self.stack=np.fromfile(filepath,'float32');
        self.stack=self.stack.reshape(self.stack.size/(self.header.Width*self.header.Height),self.header.Width,self.header.Height);
        self.stack=1000*(self.stack-0.01926)/(0.01926) # Convert to HU
        self.stack=np.transpose(self.stack,(0,2,1)) # Images from CTBangBang are transposed, this corrects it

    def to_hr2(self,outpath):
        ### Method to convert img file to hr2
        ## Attempt to load the QIA toolbox, raise error if it doesn't work
        try:
            path_dict=load_paths()
            sys.path.append(path_dict['qia_module'])            
            import qia.common.img.image as qimage
            VALUE_TYPE = qimage.Type.short            
        except Exception as e:            
            logging.error("Could not load QIA module from which HR2 file format is derived.")
            raise(e)
            sys.exit("Exiting.")

        ## Translate PRM data into data appropriate for file conversion
        # Calculate our spacing vector for hr2 conversion
        Spacing_hr2=(self.header.ReconstructionDiameter/self.header.Width,
                     self.header.ReconstructionDiameter/self.header.Height,
                     self.header.SliceThickness)
        
        # Calculate hr2 appropriate orientation vector
        x,y=self.header.ImageOrientationPatient
        z=[ x[1]*y[2]-x[2]*y[1] ,
            x[2]*y[0]-x[0]*y[2] ,
            x[0]*y[1]-x[1]*y[0] ]
        Orientation_hr2=(  x[0], y[0], z[0],
                           x[1], y[1], z[1],
                           x[2], y[2], z[2] )
        
        # Data Collection Center Patient
        Origin_hr2 = self.header.ReconstructionTargetCenterPatient

        # Image object dimensions
        minp = (0, 0, 1)
        maxp = (self.header.Width-1, self.header.Height-1, self.header.NoOfSlices)

        print("Spacing_hr2     : {}".format(Spacing_hr2))
        print("Orientation_hr2 : {}".format(Orientation_hr2))
        print("Origin_hr2      : {}".format(Origin_hr2))
        print("minp/maxp       : {} {}".format(minp,maxp))

        ## Instantiate our qimage object (which has our hr2-saving methods)
        converted_qimg = qimage.new(VALUE_TYPE, minp, maxp, spacing=Spacing_hr2, origin=Origin_hr2, orientation=Orientation_hr2, fillval=0)

        ## Fill our image object slice-by-slice (to go easy on memory)
        size_slice=self.header.Width*self.header.Height*4 # IMG files are single-precision floating point => 4 bytes per pixel
        with open(self.img_filepath,'rb') as f:
            for slice_idx in range(self.header.NoOfSlices):
                print("{}/{}".format(slice_idx+1,self.header.NoOfSlices))
                # Seek to the current slice (ultimately unnecessary, but nice for debugging the loop)
                f.seek(size_slice*slice_idx)
                # Read the slice into a numpy array
                slice=f.read(size_slice)
                slice=np.fromstring(slice,dtype=np.float32)                
                slice=slice.reshape(self.header.Width,self.header.Height)
                slice=slice.transpose() # Data from FreeCT is transposed
                # Convert the slice to HU
                slice=1000.0*(slice-0.01926)/0.01926
                # Clamp off any values below -1024 like how DICOM does
                # We may want to remove this in the future
                slice[slice<-1024]=-1024

                # Map the data into our qimage
                # set_value(tuple of voxel indices, value to set to)
                for x_idx in range(self.header.Width):
                    for y_idx in range(self.header.Height):
                        #converted_qimg.set_value((x_idx,y_idx,slice_idx+1),slice[x_idx,y_idx])
                        converted_qimg.set_value((x_idx,y_idx,slice_idx+1),slice[y_idx,x_idx])

                #import matplotlib.pyplot as plt
                #plt.imshow(slice,cmap='gray',imlim=[-1400,400])
                #plt.show()

        # Save the hr2 file to disk
        hr2_out_filepath=outpath
        print('Saving to {}'.format(hr2_out_filepath))
        converted_qimg.write(hr2_out_filepath)
        
        print("Finished your stupid test you dummy")

    def to_DICOM(self,outpath):
        ### Method to convert img file stack into individual DICOM images
        pass
