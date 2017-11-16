import sys
import os
import logging

import struct
import numpy as np
import zlib

def usage():
    print(
        """
        Usage: python read_hr2.py /path/to/input_file.hr2 /path/to/output_file.img

        Output file is a binary file of single-precision floating point values.

        Copyright (c) John Hoffman 2017
        """
    )
    sys.exit()


def read_hr2(filepath):

    hr2_dict={}

    with open(filepath,'rb') as f:

        # Ensure we have an HR2 file
        magic_number=f.read(3)
        if magic_number!=b"HR2":
            print("File is not an hr2 file. Exiting")
            sys.exit(1)

        # Read the file into memory
        while True:
            # Get tag
            chunk_tag_size=int.from_bytes(f.read(1),byteorder='little')            
            chunk_tag=f.read(chunk_tag_size)
            print(str(chunk_tag,'utf-8'))

            # Get value
            # Handle all tags *except* image data (size=uint16)
            if chunk_tag!=b'ImageData':
                chunk_val_size=int.from_bytes(f.read(2),byteorder='little')
                chunk_val=f.read(chunk_val_size)
                hr2_dict[str(chunk_tag,'utf-8')]=str(chunk_val,'utf-8')
            # Handle image data tag (size=uint32)
            else:
                chunk_val_size=int.from_bytes(f.read(4),byteorder='little')
                chunk_val=f.read(chunk_val_size)
                hr2_dict[str(chunk_tag,'utf-8')]=chunk_val
                break

        # Decompress the image data using zlib
        if hr2_dict['Compression']=="ZLib":
            hr2_dict['ImageData']=zlib.decompress(hr2_dict['ImageData'])

        # Parse image data byte string into numpy array
        hr2_dict['Size']=[int(x) for x in hr2_dict['Size'].split(' ')]
        hr2_dict['ImageData']=np.fromstring(hr2_dict['ImageData'],dtype='int16')
        hr2_dict['ImageData']=hr2_dict['ImageData'].reshape(hr2_dict['Size'][2],hr2_dict['Size'][1],hr2_dict['Size'][0])
            
        return hr2_dict

    pass

def main(argc,argv):

    # Parse CLI inputs
    if argc<3:
        usage()
        sys.exit(1)
    
    input_filepath  = argv[1]
    output_filepath = argv[2]

    # Read the HR2 file into a dictionary
    hr2_dict=read_hr2(input_filepath)

    # Write image data to disk
    hr2_dict['ImageData'].astype('float32').tofile(output_filepath);
    
    print('Done converting HR2 to binary file of floats')
    
if __name__=="__main__":
    main(len(sys.argv),sys.argv)
