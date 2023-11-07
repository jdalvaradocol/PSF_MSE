#!python3
import numpy as np
import matplotlib.pyplot as plt
from   matplotlib.animation import FuncAnimation
import os
import io
import serial
from scipy.signal import find_peaks

class return_values_FFT:
    def __init__(self, fft,fft_fs):
        self.fft = fft
        self.fft_fs = fft_fs

def FFT(x,fs):
    fft = np.abs(np.fft.fftshift(np.fft.fft(x)/len(x)))
    fft_fs = np.fft.fftshift(np.fft.fftfreq(len(x), 1/fs))
    y = return_values_FFT(fft,fft_fs) 
    return y

STREAM_FILE=("COM5","serial")
#STREAM_FILE=("log.bin","file")

header = { "pre": b"*header*", "id": 0, "N": 0, "fs": 0, "M":0,"pos":b"end*" }
fig    = plt.figure ( 1 )
fig.suptitle('ECG STM32 NUCLEO-H7A3ZI', fontsize=16)

#--------------------------ADC--------------------------
adcAxe = fig.add_subplot ( 3,2,1 )
adcAxe.set_title("adc",rotation=0,fontsize=10,va="center")
adcLn, = plt.plot        ( [],[],'r',linewidth = 1, alpha = 1 ,label = "adc")
adcLg  = adcAxe.legend()
adcAxe.grid     ( True      )
adcAxe.set_ylim ( 0.2 , 1.0 )

#----------------------h--------------------------
hAxe     = fig.add_subplot ( 3,2,3 )
hAxe.set_title("respuesta al impulso h",rotation=0,fontsize=10,va="center")
hLn, = plt.plot ( [] ,[] ,'r-o' ,linewidth = 12  ,alpha = 0.3 ,label = "h")
hLg  = hAxe.legend()
hAxe.grid     (True)
#hAxe.set_ylim (-5.0 ,5.0)

#----------------------ciaaConv--------------------------
ciaaConvAxe        = fig.add_subplot ( 3,2,5 )
ciaaConvAxe.set_title("STM32 Conv",rotation = 0,fontsize = 10,va = "center")
ciaaConvLn,     = plt.plot ( [] ,[] ,'r' ,linewidth = 1  ,alpha = 1 ,label = "ciaaConv" )
ciaaConvLg      = ciaaConvAxe.legend()
ciaaConvAxe.grid     ( True)
ciaaConvAxe.set_ylim ( -0.5 , 0.6 )

#--------------------------FFT ADC--X-----------------------
XAxe = fig.add_subplot ( 3,2,2 )
XAxe.set_title("FFT(adc)",rotation=0,fontsize=10,va="center")
XLn, = plt.plot        ( [],[],'b-o',linewidth = 5, alpha = 0.3 ,label = "X")
XLg  = XAxe.legend()
XAxe.grid     ( True)
XAxe.set_ylim ( 0.0 , 1.0 )

#----------------------FFT h----H---------------------
HAxe     = fig.add_subplot ( 3,2,4 )
HAxe.set_title("FFT(h) respuesta al impulso",rotation=0,fontsize=10,va="center")
HLn, = plt.plot ( [] ,[] ,'b-o' ,linewidth = 5  ,alpha = 0.3 ,label = "H")
HLg  = HAxe.legend()
HAxe.grid     ( True  )
#HAxe.set_ylim ( -0.2 ,0.5 )

#----------------------FFT(conv)---Y-----------------------
YAxe        = fig.add_subplot ( 3,2,6 )
YAxe.set_title("FFT(conv)",rotation = 0,fontsize = 10,va = "center")
YLn, = plt.plot ( [] ,[] ,'b-o' ,linewidth = 5  ,alpha = 0.3 ,label = "Y" )
YLg  = YAxe.legend()
YAxe.set_ylim ( 0,0.002 )

def findHeader(f,h):
    data=bytearray(b'12345678')
    while data!=h["pre"]:
        data+=f.read(1)
        if len(data)>len(h["pre"]):
            del data[0]
    h["id"]      = readInt4File(f,4)
    h["N" ]      = readInt4File(f)
    h["fs"]      = readInt4File(f)
    h["M"] = readInt4File(f)
    data=bytearray(b'1234')
    while data!=h["pos"]:
        data+=f.read(1)
        if len(data)>len(h["pos"]):
            del data[0]
    print({k:round(v,2) if isinstance(v,float) else v for k,v in h.items()})
    return h["id"],h["N"],h["fs"],h["M"]

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

def readSamples(adc,h,conv,N,trigger=False,th=0):
    state="waitLow" if trigger else "sampling"
    i=0
    for t in range(N):
        sample    = (readInt4File(streamFile,sign = True)*1.65)/((2**16)/2)
        ciaaH     = (readInt4File(streamFile,sign = True)/2**15)
        ciaaConv  = (readInt4File(streamFile,sign = True)*1.65)/((2**16)/2)
        state,nextI= {
                "waitLow" : lambda sample,i: ("waitHigh",0) if sample<th else ("waitLow" ,0),
                "waitHigh": lambda sample,i: ("sampling",0) if sample>th else ("waitHigh",0),
                "sampling": lambda sample,i: ("sampling",i+1)
                }[state](sample,i)
        adc [ i ] = sample
        h   [ i ] = ciaaH
        conv[ i ] = ciaaConv
        i=nextI

def update(t):
    global header
    flushStream ( streamFile,header )
    id,N,fs,M=findHeader ( streamFile,header )
    nData    = np.arange(0,N+M-1,1) #arranco con numeros enteros para evitar errores de float
    adc      = np.zeros(N+M-1)
    h        = np.zeros(N+M-1)
    ciaaConv = np.zeros(N+M-1)
    tData    = nData/fs
    readSamples(adc,h,ciaaConv,N+M-1,False,0)
    adcAxe.set_xlim ( 0     ,(N+M-1)/fs )
    adcLn.set_data  ( tData ,adc  )

    hAxe.set_xlim ( 0     ,(N+M-1)/fs )
    hAxe.set_ylim ( min(h    ),max(h))
    hLn.set_data  ( tData ,h )

    # print(" Media" , np.mean(ciaaConv), np.std(ciaaConv), len(ciaaConv))   

    p           = 0
    p_old       = 0
    contador    = 0
    pulsos      = 0
    estado      = False

    for i in range(len(ciaaConv)):

        p_old = p

        if ciaaConv[i] > np.mean(ciaaConv) + (1.5 * np.std(ciaaConv)):
            #ciaaConv[i] = np.mean(ciaaConv) + (1.5 * np.std(ciaaConv))
            p = 1
        else: 
            p = 0

        if (p == 1) and (p_old == 0):
            estado = True
            contador = 0
        elif (estado == True) and (p == 0):
            estado = False
            contador = 0
        elif  (estado == True) and (p == 1):
            contador  = contador + 1
            if contador  > 150:
                pulsos = pulsos + 1;
                contador = 0

    print(" Pulsos = " , pulsos," Frecuencia Cardiaca = " , pulsos * 6)   

    ciaaConvAxe.set_xlim ( 0     ,(N+M-1 )/fs     )
    ciaaConvLn.set_data ( tData ,ciaaConv )
#
    l = len(adc)
    signal = np.concatenate((adc, np.zeros(l*4)))
    fft = FFT(signal,fs)
    fData = fft.fft_fs
    XAxe.set_xlim (-fs/10,fs/10-fs/N)
    XAbs =  fft.fft 
    XLn.set_data (fData ,XAbs)
    XAxe.set_ylim ( 0,np.max(XAbs) if np.max(XAbs)>0.01 else 0.01)

    #fData=nData[0:N]*fs/N-fs/2
    #XAxe.set_xlim (-fs/2,fs/2-fs/N)
    #XAbs=np.abs(np.fft.fftshift(np.fft.fft(adc[:N]))/N)**2
    #XLn.set_data (fData ,XAbs)
    #XAxe.set_ylim ( 0,np.max(XAbs) if np.max(XAbs)>0.01 else 0.01)

    fData=nData[0:M]*fs/M-fs/2
    H=np.abs(np.fft.fftshift(np.fft.fft(h[:M]))/M)**2
    HAxe.set_xlim ( -fs/2,fs/2-fs/M )
    HAxe.set_ylim ( min(H ),max(H))
    HLn.set_data  ( fData ,H   )

    fData=nData*fs/(N+M-1)-fs/2
    ciaaConvAbs=np.abs(np.fft.fftshift(np.fft.fft(ciaaConv))/N)**2
    YLn.set_data (fData ,ciaaConvAbs)
    YAxe.set_xlim (-fs/2,fs/2-fs/(N+M-1))
    #auto escala el eje y, pero no tan bajo
    #YAxe.set_ylim ( 0,np.clip(np.max(ciaaConvAbs),0.01,100))

    return adcLn, ciaaConvLn, hLn, XLn, HLn, YLn

#seleccionar si usar la biblioteca pyserial o leer desde un archivo log.bin
if(STREAM_FILE[1]=="serial"):
    streamFile = serial.Serial(port=STREAM_FILE[0],baudrate=460800,timeout=None)
else:
    streamFile=open(STREAM_FILE[0],"rb",0)

ani=FuncAnimation(fig,update,10000,init_func=None,blit=True,interval=1,repeat=True)
plt.get_current_fig_manager().window.showMaximized() #para QT5
plt.show()
streamFile.close()
