#!/usr/bin/env python
import sys
import os
import logging
from subprocess import call
from time import strftime
from PyQt4 import QtGui, QtCore, uic
import shutil

import yaml
import tempfile
import traceback

from ctbb_pipeline_library import ctbb_pipeline_library as ctbb_plib
from ctbb_pipeline_library import mutex
from pypeline import load_config

class update_thread(QtCore.QThread):
    received = QtCore.pyqtSignal([str],[unicode]);
    def run(self):
        while True:
            self.sleep(5)
            self.received.emit('update')

class MyWindow(QtGui.QMainWindow):

    ui=None;
    current_cases=None; # Python list of raw data filepaths
    current_library=None; # Path to currently loaded library
    current_case_list_path=None;
    test_cases=None;
    test_library=None;
    update_thread=None;
    run_dir=None;

    def __init__(self,config_dict={}):
        logging.getLogger("PyQt4").setLevel(logging.WARNING)
        
        logging.info('GUI Initialization initiated')
        
        super(MyWindow,self).__init__()
        self.run_dir=os.path.dirname(os.path.abspath(__file__))
        self.ui=uic.loadUi(os.path.join(self.run_dir,'ctbb_pipeline.ui'),self)
        self.show()
        
        # Connect Callbacks
        self.ui.selectCases_pushButton.clicked.connect(self.select_cases_callback)
        self.ui.selectLibrary_pushButton.clicked.connect(self.select_library_callback);
        self.ui.queueNormal_pushButton.clicked.connect(self.queue_normal_callback);
        self.ui.queueHighPriority_pushButton.clicked.connect(self.queue_high_priority_callback);
        
        self.ui.actionSaveStudy.triggered.connect(self.save_config_file_callback);
        self.ui.actionOpenStudy.triggered.connect(self.open_config_file_callback);
        self.ui.actionExit.triggered.connect(self.close_application_callback);
        
        # Dispatch update thread
        #self.update_thread=update_thread()
        #self.update_thread.received.connect(self.refresh_gui)
        #self.update_thread.start()
        
        logging.info('GUI Initialization finished')
        
        if config_dict:
            self.set_gui_from_config(config_dict)

    def refresh_gui(self):
        print('Refreshing temporarily disabled')
        #self.refresh_library_tab()
        #self.refresh_active_jobs_tab()

    def set_gui_from_config(self,config_dict):
        # Set case list and library
        self.select_cases_callback(config_dict)
        self.select_library_callback(config_dict)

        # Set dose checkboxes
        for d in config_dict['doses']:
            if d==100:
                self.ui.dose100_checkBox.setCheckState(True);
            elif d==75:
                self.ui.dose75_checkBox.setCheckState(True);                
            elif d==50:
                self.ui.dose50_checkBox.setCheckState(True);
            elif d==25:
                self.ui.dose25_checkBox.setCheckState(True);
            elif d==10:
                self.ui.dose10_checkBox.setCheckState(True);
            elif d==5:
                self.ui.dose5_checkBox.setCheckState(True);
            else:
                logging.info('Non-GUI dose requested. Ignoring.')
                
        # Set slice thickness checkboxes
        print(config_dict)
        for sts in config_dict['slice_thicknesses']:
            if sts==0.6:
                self.ui.sliceThickness0p6_checkBox.setCheckState(True);
            elif sts==1.0:
                self.ui.sliceThickness1_checkBox.setCheckState(True);
            elif sts==1.5:
                self.ui.sliceThickness1p5_checkBox.setCheckState(True);
            elif sts==2.0:
                self.ui.sliceThickness2_checkBox.setCheckState(True);
            elif sts==3.0:
                self.ui.sliceThickness3_checkBox.setCheckState(True);
            elif sts==5.0:
                self.ui.sliceThickness5_checkBox.setCheckState(True);
            else:
                logging.info("Non-GUI slice thickness requested. Ignoring.")

        # Set kernel checkboxes
        for k in config_dict['kernels']:
            if k==1:            
                self.ui.kernel1_checkBox.setCheckState(True);
            elif k==2:            
                self.ui.kernel2_checkBox.setCheckState(True);
            elif k==3:            
                self.ui.kernel3_checkBox.setCheckState(True);
            else:
                logging.info('Non-GUI kernel requested. Ignoring.')
                        
    def testCallback(self):
        print('Test worked!');

    def select_cases_callback(self,config_dict={}):
        try:
            logging.info('Select cases callback active')
            
            accepted_filetypes=['.ctd','.ptr','.ima','.txt']
            
            # File selection dialog
            if not config_dict:
                fname=QtGui.QFileDialog.getOpenFileName(self,'Open file','/home');
            else:
                fname=config_dict['case_list']
            
            # Return if user cancelled
            if not fname:
                return;
            else:
                fname=str(fname)
            
            # Get file type and open accordingly
            ext=os.path.splitext(fname)
            ext=ext[1].lower();
            
            logging.info('Detected file extension: ' + ext)
            
            case_list=[];
            
            if (ext in accepted_filetypes):
                logging.info('File extension accepted')
                
                if ext == '.txt':
                    self.current_case_list_path=fname
                    with open(fname,'r') as f:
                        case_list=f.read().splitlines()
                else:
                    case_list.append(fname)
            else:
                self.error_dialog('Unrecognized filetype.  Accepted filetypes are IMA, PTR, CTD, and TXT')
                logging.error('User tried to load an unrecognized filetype:' + fname)
                return;
            
            # Set lineEdit string to file path
            self.ui.selectCases_edit.setText(fname)
            
            # If text file, load into memory and display in box
            # Run ctbb_info to generate base parameter files
            prmb_string=get_base_parameter_files(case_list)
            
            for i in range(0,len(prmb_string)):
                self.ui.PRMEditor_textEdit.insertPlainText('#####! DO NOT EDIT THIS LINE !#####\n');
                self.ui.PRMEditor_textEdit.insertPlainText('%%% Edit below for file: ' + case_list[i] + ' %%%\n\n');
                self.ui.PRMEditor_textEdit.insertPlainText(prmb_string[i]);
                self.ui.PRMEditor_textEdit.insertPlainText('\n\n');
            
            self.current_cases=case_list;
        except NameError:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.info(''.join('ERROR TRACEBACK: ' + line for line in lines))
            
            
    def select_library_callback(self,config_dict={}):
        try:
            logging.info('Select library callback active')
            
            if not config_dict:
                dirname=QtGui.QFileDialog.getExistingDirectory(self,'Open Directory','/home');
            else:
                dirname=config_dict['library']
            
            if not dirname:
                return;
            else:
                dirname=str(dirname)
            
            pipeline_lib=ctbb_plib(dirname)
                
            self.ui.selectLibrary_edit.setText(dirname)
            self.current_library=pipeline_lib
            
            print('Refresh currently disabled')
            #self.refresh_library_tab()
            #self.refresh_active_jobs_tab()
        except NameError:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.info(''.join('ERROR TRACEBACK: ' + line for line in lines))
        

    def queue_normal_callback(self):
        try:
            logging.info('Queue normal callback active')        
            self.flush_prmbs()
            ds,sts,ks=self.gather_run_parameters()
            config_file=self.generate_config_file(ds,sts,ks)
            self.launch_pipeline(config_file)
        except NameError:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.info(''.join('ERROR TRACEBACK: ' + line for line in lines))
            

    def queue_high_priority_callback(self):
        try:
            logging.info('Queue high priority callback active')
            self.flush_prmbs()
            ds,sts,ks=self.gather_run_parameters()
            config_file=self.generate_config_file(ds,sts,ks)
            self.launch_pipeline(config_file)
        except NameError:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.info(''.join('ERROR TRACEBACK: ' + line for line in lines))
            

    def keyPressEvent(self,e):
        if e.matches(QtGui.QKeySequence.Close) or e.matches(QtGui.QKeySequence.Quit):
            logging.info('User quit via keystroke')
            sys.exit()

    def close_application_callback(self):
        try:
            sys.exit()
        except NameError:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.info(''.join('ERROR TRACEBACK: ' + line for line in lines))
        
            
    def save_config_file_callback(self):
        try:        
            fname=QtGui.QFileDialog.getSaveFileName(self,'Open file','/home')
            if not fname:
                return
            else:
                ds,sts,ks=self.gather_run_parameters()
                config_file=self.generate_config_file(ds,sts,ks)
                shutil.copy(config_file.name,fname)
        except NameError:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.info(''.join('ERROR TRACEBACK: ' + line for line in lines))
                

    def open_config_file_callback(self):
        try:
            fname=QtGui.QFileDialog.getOpenFileName(self,'Open file','/home')
            if not fname:
                return
            else:
                config_dict=load_config(fname)
                self.set_gui_from_config(config_dict)
        except NameError:
            exc_type, exc_value, exc_traceback = sys.exc_info()     
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            logging.info(''.join('ERROR TRACEBACK: ' + line for line in lines))
                

    def generate_config_file(self,doses,slice_thicknesses,kernels):
        f=tempfile.NamedTemporaryFile()

        case_string   = "case_list: %s\n" % self.current_case_list_path
        lib_string    = "library: %s\n" % self.current_library.path
        dose_string   = "doses: %s\n" % str([float(d) for d in doses])
        sts_string    = "slice_thickness: %s\n" % str([float(s) for s in slice_thicknesses])
        kernel_string = "kernels: %s\n" % str([int(k) for k in kernels])

        # Write required info
        f.write(case_string)
        f.write(lib_string)

        # Write optional info if specified by user
        if doses:
            f.write(dose_string)
        if slice_thicknesses:
            f.write(sts_string)
        if kernels:
            f.write(kernel_string)

        f.seek(0,0)
            
        return f

    def launch_pipeline(self,config_file):
        # Test code:
        #print('')
        print(config_file.name)
        print(config_file.read())
                    
    def error_dialog(self,s):
        msg = QtGui.QMessageBox();
        msg.setIcon(QtGui.QMessageBox.Critical)
        msg.setInformativeText(s)
        msg.setWindowTitle('Error')
        msg.setStandardButtons(QtGui.QMessageBox.Close)
        msg.exec_()

    def flush_prmbs(self):
        raw_prm_text=str(self.ui.PRMEditor_textEdit.toPlainText())
        prmb_text=raw_prm_text.split('#####! DO NOT EDIT THIS LINE !#####\n')
        for i in range(1,len(prmb_text)):

            output_file_name=os.path.basename(self.current_cases[i-1])+'.prmb'
            output_dir_name=os.path.join(self.current_library.path,'raw')
            output_fullpath=os.path.join(output_dir_name,output_file_name);
            
            with open(output_fullpath,'w') as f:
                f.write(prmb_text[i])
        
    def gather_run_parameters(self):

        doses=[];
        slice_thicknesses=[];
        kernels=[];
        
        # Dose
        if self.ui.dose100_checkBox.checkState():
            doses.append('100')
        if self.ui.dose75_checkBox.checkState():
            doses.append('75')
        if self.ui.dose50_checkBox.checkState():
            doses.append('50')
        if self.ui.dose25_checkBox.checkState():
            doses.append('25')
        if self.ui.dose10_checkBox.checkState():
            doses.append('10')
        if self.ui.dose5_checkBox.checkState():
            doses.append('5')

        # Slice thickness
        if self.ui.sliceThickness0p6_checkBox.checkState():
            slice_thicknesses.append('0.6')
        if self.ui.sliceThickness1_checkBox.checkState():
            slice_thicknesses.append('1.0')
        if self.ui.sliceThickness1p5_checkBox.checkState():
            slice_thicknesses.append('1.5')
        if self.ui.sliceThickness2_checkBox.checkState():
            slice_thicknesses.append('2.0')
        if self.ui.sliceThickness3_checkBox.checkState():
            slice_thicknesses.append('3.0')
        if self.ui.sliceThickness5_checkBox.checkState():
            slice_thicknesses.append('5.0')
            
        # kernel
        if self.ui.kernel1_checkBox.checkState():
            kernels.append('1')
        if self.ui.kernel2_checkBox.checkState():
            kernels.append('2')
        if self.ui.kernel3_checkBox.checkState():
            kernels.append('3')

        logging.debug('            Doses checked: ' + str(doses))
        logging.debug('Slice thicknesses checked: ' + str(slice_thicknesses))
        logging.debug('          Kernels checked: ' + str(kernels))

        return doses,slice_thicknesses,kernels

    def refresh_library_tab(self):
        logging.info('Refreshing library tab')
        self.current_library.refresh_recon_list()
        with open(os.path.join(self.current_library.path,'recons.csv'),'r') as f:
            recon_list=f.read().splitlines();
            
        for i in range(len(recon_list)):
            recon_list[i]=recon_list[i].split(',')

        table_model=MyTableModel(recon_list)
        self.ui.library_tableView.setModel(table_model)

    def refresh_active_jobs_tab(self):
        logging.info('Refreshing active jobs tab')
        # Empty Contents
        self.ui.activeQueue_listWidget.clear()
        self.ui.completed_listWidget.clear()
        self.ui.error_listWidget.clear()
        
        # Repopulate contents
        proc_dir=os.path.join(self.current_library.path,'.proc')

        with open(os.path.join(proc_dir,'queue'),'r') as f:
            queue_list=f.read().splitlines()

        with open(os.path.join(proc_dir,'done'),'r') as f:
            done_list=f.read().splitlines()
            
        with open(os.path.join(proc_dir,'error'),'r') as f:
            error_list=f.read().splitlines()

        done_list.reverse()

        if queue_list:
            self.ui.activeQueue_listWidget.addItems(queue_list)

        if done_list:
            self.ui.completed_listWidget.addItems(done_list)

        if error_list:
            self.ui.error_listWidget.addItems(error_list)

class MyTableModel(QtCore.QAbstractTableModel):
    header_labels=['File','Case ID','Dose','Kernel','Slice Thickness','Recon Path']
    
    def __init__(self, datain, parent=None, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self,section,orientation,role=QtCore.Qt.DisplayRole):

        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.header_labels[section]
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

    def sort(self, Ncol, order):
        import operator
        self.emit(QtCore.SIGNAL("layouAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == QtCore.Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))

def get_base_parameter_files(file_list):
    logging.info('Generating parameter files and reading into pipeline');

    prmbs=[];
    
    for f in file_list:

        if not f:
            continue
        
        # Generate the parameter file
        devnull=open(os.devnull,'w')
        call(['ctbb_info','-b',f],stdout=devnull,stderr=devnull);

        # Open the parameter file and read into pipeline
        with open(f+'.prmb') as f_prmb:
            prmbs.append(f_prmb.read());

    return prmbs

if __name__ == '__main__':
    try:
        app = QtGui.QApplication(sys.argv)
        
        config_dict={}
    
        if (len(sys.argv)>1) and (sys.argv[1]=='--debug'):
            # Debug testing (dumps logging info to shell)
            logging.basicConfig(format=('%(asctime)s %(message)s'), level=logging.DEBUG)
        elif (len(sys.argv)>1) and os.path.exists(sys.argv[1]):
            config_dict=load_config(sys.argv[1])        
        else:        
            logdir=tempfile.gettempdir()
            logfile=os.path.join(logdir,('%s_interface.log' % strftime('%y%m%d_%H%M%S')))
    
            if not os.path.isdir(logdir):
                os.mkdir(logdir);
    
            logging.basicConfig(format=('%(asctime)s %(message)s'),filename=logfile, level=logging.INFO)
    
        window = MyWindow(config_dict)
    
        status=app.exec_()
        if window.current_library:
            if not os.path.isdir(os.path.join(window.current_library.path,'log')):
                os.mkdir(os.path.join(window.current_library.path,'log'))                             
            shutil.copyfile(logfile,os.path.join(window.current_library.path,'log',os.path.basename(logfile)))
        sys.exit(status)

    except NameError:
        exc_type, exc_value, exc_traceback = sys.exc_info()     
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        logging.info(''.join('ERROR TRACEBACK: ' + line for line in lines))
