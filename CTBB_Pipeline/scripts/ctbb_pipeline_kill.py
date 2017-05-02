import sys
import os

import tempfile

from subprocess import Popen, PIPE, STDOUT, call

if __name__=="__main__":

    pipeline_processes=['ctbb_simdose','ctbb_recon','ctbb_pipeline_daemon.py','ctbb_queue_item.py']
    
    fid=tempfile.TemporaryFile()
    
    # Get process list
    p=call(['ps','aux'],stdout=fid,stderr=fid,env={'LANG':'C'});    
    fid.seek(0,0);
    output=fid.read()

    # Scan output killing processes as found
    for line in output.splitlines():
        for process_name in pipeline_processes:
            if process_name in line:
                pid=line.split()[1]
                print("Killing process %d" % int(pid))
                call(['kill',pid])
                
    fid.close()
