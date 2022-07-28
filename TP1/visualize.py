#!python3
import numpy as np
import matplotlib.pyplot as plt
from   matplotlib.animation import FuncAnimation
import os
import io
import serial
from fxpmath import Fxp

STREAM_FILE=("/dev/ttyUSB1","serial")
#STREAM_FILE=("log.bin","file")

header = {  "head": b"head", "id": 0, "N": 1024, "fs": 50000, 
            "maxADC":0, "minADC":0, "rmsADC":0,
            "maxDAC":0, "minDAC":0, "rmsDAC":0,
            "tail":b"tail" }
fig    = plt.figure ( 1 )

adcAxe      = fig.add_subplot ( 2,1,1                                   )
adcLn,      = plt.plot        ( [],[], 'r-', linewidth=4                )
maxadcLn, = plt.plot          ( [],[], 'g--', linewidth = 2, alpha = 1  )
minadcLn, = plt.plot          ( [],[], 'g--', linewidth = 2, alpha = 1  )
rmsadcLn, = plt.plot          ( [],[], 'g--', linewidth = 2, alpha = 1   )
adcAxe.grid                   ( True                                    )
adcAxe.set_ylim               ( -2 , 2                                  )

dacAxe      = fig.add_subplot ( 2,1,2                                   )
dacLn,      = plt.plot        ( [],[], 'b-', linewidth=4                )
maxdacLn, = plt.plot          ( [],[], 'y--', linewidth = 2, alpha = 1  )
mindacLn, = plt.plot          ( [],[], 'y--', linewidth = 2, alpha = 1  )
rmsdacLn, = plt.plot          ( [],[], 'y--', linewidth = 2, alpha = 1   )
dacAxe.grid                   ( True                                    )
dacAxe.set_ylim               ( -50 ,2**10 + 50                         )

def findHeader(f,h):
    find=False
    while(not find):
        data=bytearray(len(h["head"]))
        while data!=h["head"]:
            data+=f.read(1)
            data[:]=data[-4:]

        h["id"]       = readInt4File(f,4)
        h["N" ]       = readInt4File(f)
        h["fs"]       = readInt4File(f)
        h["maxADC"] = (readInt4File(f,sign = True)/2**14) # Se normaliza el valor del adc/2¹⁴  
        h["minADC"] = ((readInt4File(f,sign = True))*1.65)/(2**6*512)
        h["rmsADC"] = ((readInt4File(f,sign = True))*1.65)/(2**6*512)
        h["maxDAC"] = ((readInt4File(f,sign = True))*1.65)/(2**6*512)   
        h["minDAC"] = ((readInt4File(f,sign = True))*1.65)/(2**6*512)
        h["rmsDAC"] = ((readInt4File(f,sign = True))*1.65)/(2**6*512)

        data=bytearray(b'1234')
        for i in range(4):
            data+=f.read(1)
            data[:]=data[-4:]
        find = data==h["tail"]

    print({k:round(v,2) if isinstance(v,float) else v for k,v in h.items()})
    return h["id"],h["N"],h["fs"],h["maxADC"],h["minADC"],h["rmsADC"],h["maxDAC"],h["minDAC"],h["rmsDAC"] 

def readInt4File(f,size=2,sign=False):
    raw=f.read(1)
    while( len(raw) < size):
        raw+=f.read(1)
    return (int.from_bytes(raw,"little",signed=sign))

def flushStream(f,h):
    if(STREAM_FILE[1]=="serial"): #pregunto si estoy usando la bibioteca pyserial o un file
        f.flushInput()
    else:
        f.seek ( 2*h["N"],io.SEEK_END)

def readSamples(adc,dac,N,trigger=False,th=0):
    state="waitLow" if trigger else "sampling"
    i=0
    for t in range(N):
        sample_dac = (readInt4File(streamFile,sign = True)*1)/(1)
        sample     = (readInt4File(streamFile,sign = True)*1.65)/(2**6*512)
        state,nextI= {
                "waitLow" : lambda sample,i: ("waitHigh",0) if sample<th else ("waitLow" ,0),
                "waitHigh": lambda sample,i: ("sampling",0) if sample>th else ("waitHigh",0),
                "sampling": lambda sample,i: ("sampling",i+1)
                }[state](sample,i)
        adc[i] = sample
        dac[i] = sample_dac
        i=nextI

def update(t):
    global header
#    flushStream ( streamFile,header )
    id,N,fs,maxADC,minADC,rmsADC,maxDAC,minDAC,rmsDAC = findHeader ( streamFile,header )  
    adc     = np.zeros(N)
    dac     = np.zeros(N).astype(complex)
    time    = np.arange(0,N/fs,1/fs)
    
    readSamples(adc,dac,N,False,0)

    adcAxe.set_xlim   ( 0    , N/fs   )
    adcLn.set_data    ( time , adc    )
    maxadcLn.set_data ( time , maxADC )
    minadcLn.set_data ( time , minADC )
    rmsadcLn.set_data ( time , rmsADC )

    dacAxe.set_xlim ( 0    ,N/fs )
    dacLn.set_data  ( time ,dac  )
    maxdacLn.set_data ( time , maxDAC )
    mindacLn.set_data ( time , minDAC )
    rmsdacLn.set_data ( time , rmsDAC )


    return adcLn, maxadcLn, minadcLn, rmsadcLn, dacLn, maxdacLn, mindacLn, rmsdacLn, 

#seleccionar si usar la biblioteca pyserial o leer desde un archivo log.bin
if(STREAM_FILE[1]=="serial"):
    streamFile = serial.Serial(port=STREAM_FILE[0],baudrate=460800,timeout=None)
else:
    streamFile=open(STREAM_FILE[0],"rb",0)

ani=FuncAnimation(fig,update,10000,init_func=None,blit=True,interval=1,repeat=True)
plt.draw()
#plt.get_current_fig_manager().window.showMaximized() #para QT5
plt.show()
streamFile.close()