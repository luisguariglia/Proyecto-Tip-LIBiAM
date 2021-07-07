import matplotlib.pyplot as plt
import pandas as p
from scipy.signal import filtfilt
import scipy
import numpy as np

def butterFilter(signal,datosFiltrado):
    signal= np.nan_to_num(signal, copy=False)
    if(datosFiltrado.Analog=="True"):
        analogVal=True
    else:
        analogVal=False
    datosFiltrado.mostrar()
    print(analogVal)
    b, a = scipy.signal.butter(datosFiltrado.order, [datosFiltrado.arrayA,datosFiltrado.arrayB], datosFiltrado.Type, analog=analogVal)
    y = scipy.signal.filtfilt(a,b,signal,axis=0)
    ret = abs(y)
    return ret
def butterFilterDos(signal):
    #envelopamento (envolvente) pasa-bajo
    signal = np.nan_to_num(signal, copy=False)
    b, a = scipy.signal.butter(4, [0.1,0.11], 'bandpass', analog=True)
    y = scipy.signal.filtfilt(a, b, signal)
    ret = abs(y)
    return ret

def RMS(y):
    rms = np.sqrt(np.mean(y ** 2))
    return y