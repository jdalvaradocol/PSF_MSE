# Reproducción de audio.

import numpy as np
import sounddevice as sd

sd.default.samplerate = 44100
wav_wave = np.load('chapu_noise.npy')

while True:
    sd.play(wav_wave, blocking=True)

