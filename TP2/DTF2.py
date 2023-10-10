import numpy as np
import scipy.signal as sc
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
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

#--------------------------------------
fs = 200
#--------------------------------------

#------------SIGNAL--------------------------

file = 'resolucion_espectral.txt'

with open(file) as Data:
    signalData = np.array(eval(Data.read()))
    time = np.arange(len(signalData)) * 1/fs

print("data",signalData)

# Opcion 1 con FTT
## Deteccion frecuencia con FFT.

fft      = FFT(signalData,fs)
fft_data = fft.fft
fft_frec = fft.fft_fs

peaks_ind, peaks = find_peaks(fft_data, height=0.15)
Frec = [ fft_frec[peaks_ind[0]], fft_frec[peaks_ind[1]] ]
print(" Frecuencia de la señal",Frec)

# Opcion 2 con cero Padding
# Deteccion frecuencia con FFT.

l = len(fft_data)
signal_p = np.concatenate((signalData, np.zeros(l*2)))
fft_p = FFT(signal_p,fs)
fft_p_data = fft_p.fft
fft_p_frec = fft_p.fft_fs

peaks_p_ind, peaks_p = find_peaks(fft_p_data, height=0.03)
Frec_p = [ fft_p_frec[peaks_p_ind[0]], fft_p_frec[peaks_p_ind[1]], fft_p_frec[peaks_p_ind[2]], fft_p_frec[peaks_p_ind[3]]]
print(" Frecuencia de la señal con padding",Frec_p)

## Figura 1
plt.subplot(3,1,1)
plt.plot(time,signalData)
plt.title("Amplitud")
plt.grid()
# Grafica de la FFT 1
plt.subplot(3,1,2)
plt.plot(fft_frec,fft_data)
plt.title( "Frecuencia FFT")
plt.grid(True)
# Grafica de la FFT 2 Padding
plt.subplot(3,1,3)
plt.plot(fft_p_frec,fft_p_data)
plt.title( "Frecuencia FTT Padding")
plt.grid(True)
plt.show()
#--------------------------------------

