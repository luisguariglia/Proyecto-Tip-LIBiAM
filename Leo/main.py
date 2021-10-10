import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
import scipy.signal
import pandas as p
aux = p.read_csv(r"C:\Users\Leo\Desktop\\carmenCUELLO1(1).csv", skiprows=0,
                 encoding="ISO-8859-1")
# ARCHIVO_CSV = ARCHIVO_CSV.loc[(ARCHIVO_CSV['X [s]'] > 5.4) & (ARCHIVO_CSV['X [s]'] < 5.85)]

tiempo = aux['X [s]']
emg = aux['GLd: EMG 1 (IM) [V]']
emg2 = np.nan_to_num(emg, copy=False)

magnitud = np.fft.fft(a=emg2)
frecuencia = np.fft.fftfreq(tiempo.size, d=0.001)
real = magnitud.real
img = magnitud.imag

plt.ylabel("Y")

plt.xlabel("f")
plt.plot(magnitud, real)
plt.plot(magnitud, img)
plt.show()