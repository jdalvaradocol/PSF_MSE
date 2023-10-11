import numpy as np
import matplotlib.pyplot as plt


class return_values_idft_2d:
    def __init__(self, real,imag):
        self.real = real
        self.imag = imag

def idft_2d(x):
    signal = np.fft.ifft(x)
    real = np.real(signal)
    imag = np.imag(signal)
    y = return_values_idft_2d(real,imag) 
    return y

def spectrum_truncate(x, n):
    return np.concatenate((x[:n], x[len(x)-n:]))

espectro_frecuencia = np.load('fft_hjs.npy')

signal = np.abs(espectro_frecuencia)

# FFT de señal de entrada

plt.figure(1)
plt.plot(signal)
plt.grid()

# 1)    Puede estimar que representa esta señal? (tip: grafique en 2d la idft) 2)

signal_2d = idft_2d(espectro_frecuencia)

plt.figure(2)
plt.plot(signal_2d.imag,signal_2d.real)

# 2)    Hasta que punto podría limitar el ancho de banda del espectro
#       dado en el archivo y que aun se logre interpretar la señal ?

n = 40
limit_BW = np.concatenate((espectro_frecuencia[:n], espectro_frecuencia[len(espectro_frecuencia)-n:]))
signal_2d = idft_2d(limit_BW)

plt.figure(3)
plt.plot(signal_2d.imag,signal_2d.real)

n = 20
limit_BW = np.concatenate((espectro_frecuencia[:n], espectro_frecuencia[len(espectro_frecuencia)-n:]))
signal_2d = idft_2d(limit_BW)

plt.figure(4)
plt.plot(signal_2d.imag,signal_2d.real)
plt.show()