#import ctypes
import struct
import threading
import binascii
import time
import math

import PyOctaveBand
import matplotlib.pyplot as plt
import numpy as np
import scipy.fftpack
from scipy import integrate
from ctypes import *

from concurrent.futures import ThreadPoolExecutor


class DAQ:
    ch1 = []
    ch2 = []
    ch3 = []
    ch4 = []
    ch1f = []
    ch2f = []
    ch3f = []
    ch4f = []
    sampling_target_size = 5000
    sampling_interval = 5
    status = 0
    sampling_per_sec = 1000
    method = 'ONE_THRID'
    ch1_int_cal = ''
    ch2_int_cal = ''
    ch3_int_cal = ''
    ch4_int_cal = ''

    def __init__(self, root):
        self.sampling_target_size = 5000
        self.sampling_interval = 5
        self.status = 0
        self.root = root
        self.executor = ThreadPoolExecutor(5)
        self.method = 'ONE_THRID'
    
    def initialize(self, sampling_target_size):
        self.sampling_target_size = sampling_target_size
        #######################################################
        #please must use DLL with 64bit version
        #debug was OK by python 3.7.4 64bit vesion
        #debug date : 2021-12-25
        #Edit by: andy jiang
        ########################################################
        self.vk70xnhdll = cdll.LoadLibrary('VK70xNMC_DAQ2.dll') ## cdll.LoadLibrary('./VK70xNMC_DAQ2.dll'),In version 3.10,

        ret=self.vk70xnhdll.Server_TCPOpen(8234)#open Server port
        connectedclientnum=c_long(0)
        self.keepLoopRunning=c_long(0)

        if ret >= 0:
            self.status=1 # Server Port Opened
            print('Waiting...')
            self.keepLoopRunning=1
            while self.keepLoopRunning:
                time.sleep(0.5)#delay 500ms
                ret=self.vk70xnhdll.Server_Get_ConnectedClientNumbers(byref(connectedclientnum))
                #if ret < 0:
                #    self.keepLoopRunning=0
                #    connectedclientnum=0#fault or error
                print('Number of DAQ device connected to the current server:',connectedclientnum.value)
                if connectedclientnum.value>0:
                    self.keepLoopRunning=0#fault or error
                    self.status=2 # DAQ device connected
            #------------------------
            time.sleep(0.5)#delay 0.5s
            
            if connectedclientnum.value>0:
                print('Ready to install the DAQ -',connectedclientnum.value)
                self.keepLoopRunning=1
                time.sleep(0.1)#delay 100ms
                para = (c_long * 16)()
                for i in range(0,15):#Initialize the daq device configuration
                    para[i]=0
                #---------------------------
                # initialize VK701NSD and VK701N
                # refvol=4.0V, bit mode=24bit, sample rate = 1000HZ, ch1~4 voltage range = -10V ~ +10V
                # More daq device's configure please refer to the <VK70xNMC DAQ DLL Function Operating Instruction_V6.xx> document
                #---------------------------
                ret=self.vk70xnhdll.VK70xNMC_Initialize(0,4,1, self.sampling_per_sec,0,0,0,0)
                #----------------------------       
                if ret < 0:
                    self.keepLoopRunning=0
                    print('Setup failed！',ret)
                    #connectedclientnum[0]=0#fault or error
                else:
                    print('Setup successfully！',ret)                
                #---------------------------
                time.sleep(0.1)#delay 100ms
                ret=self.vk70xnhdll.VK70xNMC_StartSampling(0)
                if ret < 0:
                    self.keepLoopRunning=0
                    #connectedclientnum[0]=0#fault or error
                    print('Open failed！',ret)
                else:
                    print('Open successfully！',ret)                
                #---------------------------
                
                
            ######################################## 
            adcbuf = (c_double * 10000)()# 1000 sample points * 10 channels
            sample_pool = 0
            retry = 0
            while self.keepLoopRunning:
            ########################################
                # ts = time.time()
                print(time.time())
                time.sleep(0.99) ##0.1 seconds
                #----------------------
                if retry:
                    rdlen = self.vk70xnhdll.VK70xNMC_GetOneChannel(0,1,adcbuf,1000)#read channel-1 for VK701NSD,VK701N and VK702N
                else:
                    rdlen = self.vk70xnhdll.VK70xNMC_GetFourChannel(0,adcbuf,1000)#read all channels for VK701NSD and VK701N; read four channels for VK702N
                #---------------------- 
                print('Read [',rdlen,'] sample!')
                if rdlen==0:
                    retry = 1
                    # self.keepLoopRunning=0
                else:
                   retry = 0
                    
                if rdlen>0 and rdlen == self.sampling_per_sec:
                    self.getSamplings(rdlen, adcbuf)
                    sample_pool += rdlen

                if sample_pool >= sampling_target_size :
                    self.processingSamples(sample_pool, self.sampling_per_sec)
                    # future = self.executor.submit(self.processingSamples, (sample_pool, self.sampling_per_sec))
                    print('sample_pool = ', sample_pool)
                    sample_pool = 0
                    
                    
                    # print('Sample[',i,']=',adcbuf[4*i],adcbuf[4*i+1],adcbuf[4*i+2],adcbuf[4*i+3])

                    #print('############################################')
                    #self.keepLoopRunning=0# exit the main loop
                    # print(ch1)
                    
                    

                    
                    # ch1f = scipy.fftpack.fft(ch1) # return array of complex number
                    # ch2f = scipy.fftpack.fft(ch2) # return array of complex number
                    # ch3f = scipy.fftpack.fft(ch3) # return array of complex number
                    # ch4f = scipy.fftpack.fft(ch4) # return array of complex number
                    
                    # print( len(ch1) )
                    # print( ch1f )
                    
                    # self.oneThrid(rdlen, ch1_int, ch2_int, ch3_int, ch4_int)
                    
                    print(time.time())
                    # print("---- 1/3 Completed ----")
            ########################################
            time.sleep(0.2)##0.2 seconds
            ret=self.vk70xnhdll.VK70xNMC_StopSampling(0)
            time.sleep(0.2)##0.2 seconds
            ret=self.vk70xnhdll.Server_TCPClose(8234)
            time.sleep(0.5)##0.5 seconds
            #=========================================
            print('Close the Server port!')
            #cdll.unLoadLibrary('VK70xNMC_DAQ2.dll')  
        else:
            print('Unable to open the server. The Server port may be occupied！')
            #cdll.unLoadLibrary('VK70xNMC_DAQ2.dll')     
        #####################################################################

    def oneThrid(self, rdlen, ch1_int, ch2_int, ch3_int, ch4_int):    
        print("Start oneThrid...")
        Fs = self.sampling_per_sec #sampling freq
        N = rdlen
        # sample spacing(sample time interval)
        tstep = ( self.sampling_interval / Fs ) * self.sampling_interval
        t = np.linspace(0.0, (N-1)*tstep, N) # time steps
        fstep = Fs / N
        f = np.linspace(0.0, (N-1)*fstep, N) # freq steps
        
        # Filter (only octave spectra)
        # spl_1, freq1 = PyOctaveBand.octavefilter(ch1_int, fs=Fs, fraction=3, order=6, limits=[1, 500], show=0)
        spl_1, freq1 = PyOctaveBand.octavefilter(ch1_int, fs=Fs, fraction=3, order=16, limits=[1, 500], show=0)
        spl_2, freq2 = PyOctaveBand.octavefilter(ch2_int, fs=Fs, fraction=3, order=16, limits=[1, 500], show=0)
        spl_3, freq3 = PyOctaveBand.octavefilter(ch3_int, fs=Fs, fraction=3, order=16, limits=[1, 500], show=0)
        spl_4, freq4 = PyOctaveBand.octavefilter(ch4_int, fs=Fs, fraction=3, order=16, limits=[1, 500], show=0)
        
        print("Start dataWriter...")
        self.dataWriter('test.txt', spl_1)
        
    def ppv(self, rdlen, ch1_int, ch2_int, ch3_int, ch4_int):
        print("Start PPV...")
        maxPpv = 0
        # print( rdlen )
        # print( len ( ch1_int ) )
        rdlen = min( rdlen, len ( ch1_int ), len ( ch2_int ), len ( ch3_int ) )
        for i in range(rdlen):
            ppv = math.sqrt( ch1_int[i]**2 + ch2_int[i]**2 + ch3_int[i]**2 )
            # print( ppv )
            if ppv > maxPpv:
                maxPpv = ppv
        self.dataSimpleWriter('ppv.txt', maxPpv)

    def rms(self, rdlen, ch1_int, ch2_int, ch3_int, ch4_int):
        print("Start RMS...")
        maxPpv = 0
        # print( rdlen )
        # print( len ( ch1_int ) )
        rdlen = min( rdlen, len ( ch1_int ), len ( ch2_int ), len ( ch3_int ) )
        for i in range(rdlen):
            ppv = math.sqrt( ch1_int[i]**2 + ch2_int[i]**2 + ch3_int[i]**2 )
            # print( ppv )
            if ppv > maxPpv:
                maxPpv = ppv
        self.dataSimpleWriter('rms.txt', maxPpv)

    def getSamplings(self, rdlen, adcbuf):
        # self.ch1=[]
        # self.ch2=[]
        # self.ch3=[]
        # self.ch4=[]
        # 4 channels
        for i in range(rdlen):
            self.ch1.append(abs(adcbuf[4*i]))
            self.ch2.append(abs(adcbuf[4*i+1]))
            self.ch3.append(abs(adcbuf[4*i+2]))
            self.ch4.append(abs(adcbuf[4*i+3]))
            
    def dataWriter(self, filename, data_arr):
        f = open(filename, 'w')
        # write elements of list
        for item in data_arr:
            # f.write('%s\n' % "{:.8f}".format( number ))
            f.write("{:.8f}\n".format( item ))
        # print("File written successfully")
        # print("{:.8f}".format( number ));
        # # freq: wirte start at 1.6hz. while list start at 1hz
        # # close the file
        f.close()
        
    def dataSimpleWriter(self, filename, data):
        f = open(filename, 'w')
        f.write("{:.8f}\n".format( data ))
        f.close()
    
    def processingSamples(self, sample_pool, rdlen):
        print("Start Processing now..")
        print(time.time())
        self.ch1f=[]
        self.ch2f=[]
        self.ch3f=[]
        self.ch4f=[]
        
        Fs = self.sampling_per_sec #sampling freq
        # N = rdlen * self.sampling_interval
        N = sample_pool
        # sample spacing(sample time interval)
        tstep = ( 1 / Fs )
        t = np.linspace(0.0, (N-1)*tstep, N) # time steps
        fstep = Fs / N
        f = np.linspace(0.0, (N-1)*fstep, N) # freq steps
        
        # print( tstep )
        
        # --- Integrate ---
        # ch1_accel = np.array(ch1)
        # ch1_accel = ch1_accel * 9.80665 # convert from g to m/s2 e.g. 50mv/ms-2
        # print( self.ch1 )
        ch1_accel = np.array(self.ch1) / 20 # <- Sensitivity Multiplier
        ch2_accel = np.array(self.ch2) / 20 # 
        ch3_accel = np.array(self.ch3) / 20 # 
        ch4_accel = np.array(self.ch4) / 20 # 
        
        self.ch1=[]
        self.ch2=[]
        self.ch3=[]
        self.ch4=[]
        # print( ch1_accel )
        
        # print( len (t) )
        # print( len (ch1_accel) )
        ch1_int = integrate.cumtrapz(t, ch1_accel)
        ch2_int = integrate.cumtrapz(t, ch2_accel)
        ch3_int = integrate.cumtrapz(t, ch3_accel)
        ch4_int = integrate.cumtrapz(t, ch4_accel)
        # print( ch1_int )
        
        print( len (t) )
        print( len (ch1_int) )
        
        t2 = np.linspace(0.0, (N-1)*tstep, N-1) # time steps
        if self.ch1_int_cal == 'DOUBLE':
            ch1_int = integrate.cumtrapz(t2, ch1_int)
        if self.ch2_int_cal == 'DOUBLE':
            ch2_int = integrate.cumtrapz(t2, ch2_int)
        if self.ch3_int_cal == 'DOUBLE':
            ch3_int = integrate.cumtrapz(t2, ch3_int)
        if self.ch4_int_cal == 'DOUBLE':
            ch4_int = integrate.cumtrapz(t2, ch4_int)
        # print( ch1_int )
        
        # if self.method == 'ONE_THRID':
        self.oneThrid(rdlen, ch1_int, ch2_int, ch3_int, ch4_int)
            
        # if self.method == 'PPV':
        self.ppv(N, ch1_int, ch2_int, ch3_int, ch4_int)
            
        # if self.method == 'RMS':
        self.rms(N, ch1_int, ch2_int, ch3_int, ch4_int)
