import struct
import threading
import binascii
import datetime
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import scipy.fftpack

from ctypes import *

vk70xnhdll = cdll.LoadLibrary(r'C:\Users\New staff\Desktop\peter\Measuring826\VK70xNMC_DAQ2.dll') ## cdll.LoadLibrary('./VK70xNMC_DAQ2.dll'),In version 3.10,
ret=vk70xnhdll.Server_TCPOpen(8234)#open Server port
connectedclientnum=c_long(0)
keepLoopRunning=c_long(0)
ch1=[]
ch2=[]
ch3=[]
ch4=[]
ch1f=[]
ch2f=[]
ch3f=[]
ch4f=[]
if ret >= 0:
    print('Waiting...')
    keepLoopRunning=1
    while keepLoopRunning:
        time.sleep(0.5)#delay 500ms
        ret=vk70xnhdll.Server_Get_ConnectedClientNumbers(byref(connectedclientnum))
        #if ret < 0:
        #    keepLoopRunning=0
        #    connectedclientnum=0#fault or error
        print('Number of DAQ device connected to the current server:',connectedclientnum.value)
        if connectedclientnum.value>0:
            keepLoopRunning=0#fault or error
    #------------------------
    time.sleep(0.5)#delay 0.5s
    if connectedclientnum.value>0:
        print('Ready to install the DAQ -',connectedclientnum.value)
        keepLoopRunning=1
        time.sleep(0.1)#delay 100ms
        para = (c_long * 16)()
        for i in range(0,15):#Initialize the daq device configuration
            para[i]=0
        #---------------------------
        # initialize VK701NSD and VK701N
        # refvol=4.0V, bit mode=24bit, sample rate = 1000HZ, ch1~4 voltage range = -10V ~ +10V
        # More daq device's configure please refer to the <VK70xNMC DAQ DLL Function Operating Instruction_V6.xx> document
        #---------------------------
        # ret=vk70xnhdll.VK70xNMC_Initialize(0,4,24,1000,0,0,0,0)
        ret=vk70xnhdll.VK70xNMC_Initialize(0,4,1,1000,0,0,0,0)
        #---------------------------
        # initialize VK702N
        #refvol=2.442V, bit mode=24bit, sample rate = 1000HZ, ch1~4 voltage range = -10V ~ +10V
        #---------------------------
        # ret=vk70xnhdll.VK70xNMC_Initialize(0,0,24,1000,0,0,0,0)
        #----------------------------       
        if ret < 0:
            keepLoopRunning=0
            print('Setup failed！',ret)
            #connectedclientnum[0]=0#fault or error
        else:
            print('Setup successfully！',ret)                
        #---------------------------
        time.sleep(0.1)#delay 100ms
        ret=vk70xnhdll.VK70xNMC_StartSampling(0)
        if ret < 0:
            keepLoopRunning=0
            #connectedclientnum[0]=0#fault or error
            print('Open failed！',ret)
        else:
            print('Open successfully！',ret)                
        #---------------------------
    ######################################## 
    # plt.ion()
    adcbuf = (c_double * 10000)()# 1000 sample points * 10 channels
    def animate(data_lst):
        now=datetime.datetime.now()
        print(now.time()) 
        time.sleep(0.99)##0.1 seconds
        #----------------------
        #rdlen = vk70xnhdll.VK70xNMC_GetOneChannel(0,1,adcbuf,1000)#read channel-1 for VK701NSD,VK701N and VK702N
        rdlen = vk70xnhdll.VK70xNMC_GetFourChannel(0,adcbuf,1000)#read all channels for VK701NSD and VK701N; read four channels for VK702N
        # rdlen = vk70xnhdll.VK70xNMC_GetAllChannel(0,adcbuf,1000)#read all channels for VK702N
        #----------------------
        #rdlen = vk70xnhdll.VK70xNMC_GetOneChannel_WithIOStatus(0,1,adcbuf,1000,3)#read channel-1 + IO2+IO3 for VK701NSD,VK701N and VK702N
        #rdlen = vk70xnhdll.VK70xNMC_GetFourChannel_WithIOStatus(0,adcbuf,1000,2)#read all channels + IO3 for VK701NSD and VK701N; read four channels + IO2 for VK702N
        #rdlen = vk70xnhdll.VK70xNMC_GetAllChannel_WithIOStatus(0,adcbuf,1000,1)#read all channels + IO2 for VK702N
        #---------------------- 
        print(rdlen)
        if rdlen>0:
            
            print('Read [',rdlen,'] sample!')
            ch1=[]
            ch2=[]
            ch3=[]
            ch4=[]
            #please add the print result according to call the different functions in here
            # the array of result please refer to the <VK70xNMC DAQ DLL Function Operating Instruction_V6.xx> document
            
            #print('############################################')
            #-----------------------
            # 1 channels
            #for i in range(rdlen):                
            #     print('Sample[',i,']=',adcbuf[i])   
            #-----------------------
            # 4 channels
            for i in range(rdlen):
                ch1.append(abs(adcbuf[4*i]))
                ch2.append(abs(adcbuf[4*i+1]))
                ch3.append(abs(adcbuf[4*i+2]))
                ch4.append(abs(adcbuf[4*i+3]))
                #print('Sample[',i,']=',adcbuf[4*i],adcbuf[4*i+1],adcbuf[4*i+2],adcbuf[4*i+3])                 
            #-----------------------
            # 8 channels
            # for i in range(rdlen):
               # print('Sample[',i,']=',adcbuf[8*i],adcbuf[8*i+1],adcbuf[8*i+2],adcbuf[8*i+3],adcbuf[8*i+4],adcbuf[8*i+5],adcbuf[8*i+6],adcbuf[8*i+7])                 
            #----------------------
            # 1 channels + IO2 + IO3
            #for i in range(rdlen):                
            #     print('Sample[',i,']=',adcbuf[3*i],adcbuf[3*i+1],adcbuf[3*i+2])   
            #-----------------------
            # 4 channels + IO3
            #for i in range(rdlen):                
            #     print('Sample[',i,']=',adcbuf[5*i],adcbuf[5*i+1],adcbuf[5*i+2],adcbuf[5*i+3],adcbuf[5*i+4])                 
            #-----------------------
            # 8 channels + IO2
            #for i in range(rdlen):                
            #     print('Sample[',i,']=',adcbuf[9*i],adcbuf[9*i+1],adcbuf[9*i+2],adcbuf[9*i+3],adcbuf[9*i+4],adcbuf[9*i+5],adcbuf[9*i+6],adcbuf[9*i+7],adcbuf[9*i+8])                 
            #----------------------
            #print('############################################')
            #keepLoopRunning=0# exit the main loop
            # print(ch1)
            print("Start FFT now..")
            print(now.time())
            ch1f=[]
            ch2f=[]
            ch3f=[]
            ch4f=[]
            ch1f = scipy.fftpack.fft(ch1) # return array of complex number
            ch2f = scipy.fftpack.fft(ch2) # return array of complex number
            ch3f = scipy.fftpack.fft(ch3) # return array of complex number
            ch4f = scipy.fftpack.fft(ch4) # return array of complex number
            
            # print( len(ch1) )
            # print( ch1f )
            Fs = 1000 #sampling freq
            N = rdlen
            # sample spacing(sample time interval)
            tstep = 1.0 / Fs
            t = np.linspace(0.0, (N-1)*tstep, N) # time steps
            fstep = Fs / N
            f = np.linspace(0.0, (N-1)*fstep, N) # freq steps
            # Perform FFT
            # x = scipy.fftpack.fft(y) # return array of complex number
            X1_mag = np.abs(ch1f) / N # N = len(y)
            f_plot = f[0:int(N/2+1)]

            X1_mag_plot = 2 * X1_mag[0:int(N/2+1)]
            X1_mag_plot[0] = X1_mag_plot[0] / 2 # DC component dopes not need to multiply by 2
            
            
            # clear the last frame and draw the next frame
            ax.clear()
            ax.plot(ch1)
            # Format plot
            ax.set_title("Potentiometer Reading Live Plot")
            ax.set_ylabel("Potentiometer Reading")
            ax.set_ylim([-5,5])
            
            print(time.time())
            print("---- FFT Completed ----")
        

fig,ax=plt.subplots()


if(keepLoopRunning):
    ani=animation.FuncAnimation(
        fig,animate,frames=100,interval=100
    )
    
plt.show()