# Pipeline Datasets

This document is best viewed using a MARKDOWN interpreter/compiler.  That or just (read this file on github)[]

## Intro
Pipeline datasets are intended to organize any and all relevant data.  This potentially includes raw data, image data, segmentations, annotations, and all other processing information that can be applied.  Often however, we will share only a subset of this (i.e. only image data) for either simiplicity or PHI-related reasons.

Each raw data file is assigned a unique identifier, which is used to identify the image reconstructions originating from this raw data file.  This identifier is the MD5 hash of the raw data file and looks something like "40f2dc4010e9943b59b786520bc33d0b."

## Quick Start

### 1. Get the case list (list of all studies contained in the library)
A list of all the studies contained in the pipeline library can be found in `/library/case_list.txt`


### 2. Find the image data
With the case list, the image volume datasets can be found at `library/recon/{dose_level}/{uid}_k{kernel}_st{slice_thickness}/img/{uid}_d{dose_level}_k{kernel}_st{slice_thickness}.hr2`

Replace the stuff in curly brackets with the following:

    `{uid}`             - The MD5 sum value found in case_list.txt
    
    `{dose_level}`      - The percent value of the desired dose level. E.g.,  100, 50, 25, 10, etc.
    
    `{kernel}`          - At present, 1, 2, or 3, corresponding to smooth, medium, and sharp respectively.
    
    `{slice_thickness}` - Slice thickness of the recontruction, always with one decimal place. E.g. 2.0, 1.0, 0.6, etc.

Sample full paths to image data:

```
library/recon/100/55913664e5df7c90a940c4a1c27ea655_k3_st0.6/img/55913664e5df7c90a940c4a1c27ea655_d100_k3_st0.6.hr2
library/recon/100/946643fb333a27f4ba320dc638c1a129_k2_st1.0/img/946643fb333a27f4ba320dc638c1a129_d100_k2_st1.0.hr2
library/recon/100/2b728ba0e32185c648e5f7f0a30e6dd3_k2_st0.6/img/2b728ba0e32185c648e5f7f0a30e6dd3_d100_k2_st0.6.hr2
library/recon/50/53b5200c2de2a83ace72614af53e1eab_k1_st1.0/img/53b5200c2de2a83ace72614af53e1eab_d50_k1_st1.0.hr2
library/recon/50/b2cdac23b83d87d2931fa593f6bb4a2d_k3_st2.0/img/b2cdac23b83d87d2931fa593f6bb4a2d_d50_k3_st2.0.hr2
library/recon/25/89b0dfb7e52910265200ccd75ad5eb5a_k1_st0.6/img/89b0dfb7e52910265200ccd75ad5eb5a_d25_k1_st0.6.hr2
library/recon/25/f53080cf7876dab9406983d5f8add7b8_k3_st0.6/img/f53080cf7876dab9406983d5f8add7b8_d25_k3_st0.6.hr2
library/recon/10/a2d88994d82eb030510a18b9782a4fd6_k1_st0.6/img/a2d88994d82eb030510a18b9782a4fd6_d10_k1_st0.6.hr2
```

### 3. Read the image files
Using the tips found below in the "Image files" section.  If HR2, you'll want to grab the script linked to below.  If IMG, you'll want to use the MATLAB code snippet (ported to your language of choice).

### 4. Analyze!
Deep learn, score, manipulate, denoise, renoise, damage, revert, whatever your heart desires.

## Basic Organization

### Library

The primary directory is "library" and, at most, should be one-level below the directory shared with you.

Inside of "library" you should see the following files and directories:
```
case_list.txt
README.md (this file)
recons.csv
eval/
log/
qa/
raw/
recon/
```
Briefly:

* **case_list.txt**: specifies the original raw data paths and the corresponding unique identifier
* **recons.csv**: list of all reconstructions contained in the library and their corresponding reconstruction/dose parameters.  Paths are specified as absolute and will need to be updated if this spreadsheet will be used to index across the reconstructions in the library.
* **README.md**: This file
* **eval/**: Directory containing analysis information for the entire dataset (e.g. aggregated quantitative imaging scores).  A good rule of thumb is that this directory should only contain something that you would share with a statistician.
* **log/**: logfiles for the pipeline run and any analysis desired.  (Messy at present, but hopefully will improve in the future)
* **qa/**: Quality assurance files.  This directory is typically used for "rapid review" structured HTML documents that allows us to visualize a cross section of the subject's scan.  Anything related to ensuring properly functioning pipeline can go here though.
* **raw/**: All raw data is copied into this directory and renamed to its corresponding unique identifier.  Each file is placed into a directory corresponding to its dose level.  UIDs are preserved across dose levels.
* **recon/**: Directory containing all image data for the study, as well as analysis results for that particular dataset.  This is the most important directory.

### Organization of the "recon/" directory

#### Sample directory tree

```
library/
|
+--recon/
|  |
.  +--(dose level directory, e.g., "100")/
.  |  |
.  .  +--(image set directory, e.g. "03fdf7ac1ceac345ac9060ac18f230cc_k1_st1.0")/
   .  |  |--eval/
   .  .  |--img/
      .  |  |-- 03fdf7ac1ceac345ac9060ac18f230cc_d10_k1_st1.0.hr2    <-IMAGE DATA FILE 
      .  |  +-- 03fdf7ac1ceac345ac9060ac18f230cc_d10_k1_st1.0.prm    <-PARAMETER FILE
         |
         |--log/
         |--qa/
         |--qi_raw/
         |--qa/
         |--ref/
         +--seg/
```

#### Description
Under the recon directory there are the "dose" directories.  These hold all of the image data for a given dose level.

Below the dose directory are the individual image study directories.  These are each named with the following convention: "{UID}\_k{kernel level}_st{slice thickness}."  Examples can be found in the sample directory tree above.

Inside of the study directories are several directories holding all of the image and analysis data for the current study/subject.

Briefly:

* **img/**: This directory is perhaps the most important directory.  It contains image data and configuration data (for the reconstruction).  Image data will either be in IMG or HR2 format typically.  In rare instances there will be a "dcm" directory containing DICOM image data.
* **eval/**: Unused at present
* **log/**: individual log files for the given study
* **qa/**: This directory holds image files used to build the "quick review" QA documents found in the library/qa directory.
* **qi\_raw/**: This directory holds unprocessed, quantitative imaging data computed directly from the images. 
* **ref/**: This directory holds any study-specific data that was not generated by the pipeline
* **seg/**: This directory holds any segmentation files for the study.  These are typically .roi format.

#### Image files

*Sample filenames:*
* `03fdf7ac1ceac345ac9060ac18f230cc_d10_k1_st1.0.hr2`    <-IMAGE DATA FILE 
* `03fdf7ac1ceac345ac9060ac18f230cc_d10_k1_st1.0.img`    <-IMAGE DATA FILE 
* `03fdf7ac1ceac345ac9060ac18f230cc_d10_k1_st1.0.prm`    <-PARAMETER FILE

There are two image formats currently utilized by the pipeline:

* **HR2**: This is a proprietary, in-house format.  See below for more information regarding how to read these files.

* **IMG**: Files are a binary file of floating point attenuation values (i.e. NOT Hounsfield units).  A scanner/energy specific attenuation value for water must be obtained to convert this format into HU.  The formula to convert a voxel into HU is the following 1000*(\mu-\mu\_{h2o})/\mu\_{h2o} where \mu is the attenuation value.  For the Siemens Definition AS, the \mu\_{h2o} value is 0.1926.  Dimensions for the reconstructed image are typically 512x512xN\_{slices}.  Actual dimension of the image can be found as the Nx and Ny parameters in the *.prm file contained inside of the img directory.

#### HR2 File Format

For the technologically inclined, the easiest way to understand the HR2 format is probably just to look at a script designed to read the filetype.  One of those can be found here: https://github.com/captnjohnny1618/CTBB_Pipeline_Package/blob/develop/CTBB_Pipeline/src/read_hr2.py

This will convert a .HR2 file into a binary file of floating point values, already in HU.  If this is not the desired behavior, the function "read_hr2" contained withing the file will read an HR2 file and return a Python dictionary with metadata and a NumPy array of the image data.

For those who are not technologically inclined, just run the script with something similar to:

`python read_hr2.py my_image_set.hr2 my_output_image.img`

The .IMG output file is the same as that describe above and can be read into MATLAB with something similar to:
```matlab
fid=fopen('my_output_image.img','r'); 
img_stack=fread(fid,'float32'); 
fclose(fid);
img_stack=reshape(img_stack,[Nrows Ncols n_slices])
```

This approach will "forfeit" any metadata extracted, however this can be pulled more manually from the HR2 file if needed.

## Final Thoughts

We want the pipeline data structures to be useful and reasonably easy to use!  Please let us know if you have any feedback, comments, or concerns. 

## Contact:

jmhoffman@mednet.ucla.edu or freect.project@gmail.com

<3

Copyright (c) John Hoffman 2018
