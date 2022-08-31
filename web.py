# live_plot_sensor.py
import struct
import threading
import binascii
import datetime
import time

import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import scipy.fftpack

from ctypes import *

# animation function
def animate(i, data_lst, ser):  # ser is the serial object

    # Add x and y to lists

    # Limit the data list to 100 values
    data_lst = data_lst[-100:]
    # clear the last frame and draw the next frame
    ax.clear()
    ax.plot(data_lst)
    # Format plot
    ax.set_ylim([0, 1050])
    ax.set_title("Potentiometer Reading Live Plot")
    ax.set_ylabel("Potentiometer Reading")

vk70xnhdll = cdll.LoadLibrary(r'C:\Users\New staff\Desktop\peter\Measuring826\VK70xNMC_DAQ2.dll') ## cdll.LoadLibrary('./VK70xNMC_DAQ2.dll'),In version 3.10,
ret=vk70xnhdll.Server_TCPOpen(8234)#open Server port
connectedclientnum=c_long(0)
keepLoopRunning=c_long(0)
# create empty list to store data
# create figure and axes objects
data_lst = []
fig, ax = plt.subplots()
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
# set up the serial line
ret=vk70xnhdll.VK70xNMC_Initialize(0,4,1,1000,0,0,0,0)
adcbuf = (c_double * 10000)()# 1000 sample points * 10 channels
ch1=[]
rdlen = vk70xnhdll.VK70xNMC_GetFourChannel(0,adcbuf,1000)#r
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
ser=ch1
time.sleep(2)
print(ser.name)
print(ser.readline())
# run the animation and show the figure
# ani = animation.FuncAnimation(
#     fig, animate, frames=100, fargs=(data_lst, ser), interval=100
# )
plt.show()

# after the window is closed, close the ser.ial line
ser.close()
print("Serial line closed")