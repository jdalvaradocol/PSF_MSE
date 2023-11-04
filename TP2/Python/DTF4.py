import numpy as np
import matplotlib.pyplot as plt

class return_values_FFT:
    def __init__(self, fft,fft_fs):
        self.fft = fft
        self.fft_fs = fft_fs

def FFT(x,fs):
    fft = np.abs(np.fft.fftshift(np.fft.fft(x)/len(x)))
    fft_fs = np.fft.fftshift(np.fft.fftfreq(len(x), 1/fs))
    y = return_values_FFT(fft,fft_fs) 
    return y

fs = 8000
signal = np.load('chapu_noise.npy')
time = np.arange(len(signal)) * 1 / fs

plt.figure(1)
plt.plot(time, signal)
plt.grid()
plt.ylabel('Amplitude')
plt.xlabel('Time [Sec]')
plt.title('Chapunoise in time domain')

fft = FFT(signal, fs)
plt.figure(2)
plt.xlabel('Frequencies [Hz]')
plt.ylabel('Magnitude')
plt.plot(fft.fft_fs, fft.fft)

plt.figure(3)
plt.title('Chapunoise Spectrogram')
plt.specgram(signal, Fs=fs, cmap="rainbow")
plt.xlabel('Time [Sec]')
plt.ylabel('Frequency [Hz]')

## Validación del filtro relizado en 

coe_filter = np.array(np.load('filtro.npy').astype(float))
coe_filter = np.ravel(coe_filter.T)
filter = np.convolve(coe_filter,signal)

plt.figure(4)
plt.plot(filter)
plt.grid()
plt.ylabel('Amplitude')
plt.xlabel('Time [Sec]')
plt.title('Chapunoise in time domain')

fft = FFT(filter, fs)
plt.figure(5)
plt.xlabel('Frequencies [Hz]')
plt.ylabel('Magnitude')
plt.plot(fft.fft_fs, fft.fft)

plt.figure(6)
plt.title('Chapunoise Spectrogram')
plt.specgram(filter, Fs=fs, cmap="rainbow")
plt.xlabel('Time [Sec]')
plt.ylabel('Frequency [Hz]')
plt.show()

# 4) Reproduzca el audio antes y después del filtro
import sounddevice as sd

sd.default.samplerate = 44100
wav_wave = np.load('chapu_noise.npy')

while True:
    sd.play(wav_wave, blocking=True)
    sd.play(filter, blocking=True)
