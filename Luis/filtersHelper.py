from scipy.signal import filtfilt
import scipy
import numpy as np

#------->archivo para tod0 lo relacionado a los filtros
def butterFilter(signal,datosFiltrado):
    signal= np.nan_to_num(signal, copy=False)
    if(datosFiltrado.Analog=="True"):
        analogVal=True
    else:
        analogVal=False
    b, a = scipy.signal.butter(datosFiltrado.order, [datosFiltrado.arrayA,datosFiltrado.arrayB], datosFiltrado.Type, analog=analogVal)
    y = scipy.signal.filtfilt(a,b,signal,axis=0)
    ret = abs(y)
    #ret = y
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

class datosButter():
    #valores por defecto
    def __init__(self):
        self.order = 3
        self.arrayA = 0.02
        self.arrayB = 0.4
        self.Type= "bandpass"
        self.Analog="True"
    def mostrar(self):
        print("----------")
        print(self.order)
        print(self.arrayA)
        print(self.arrayB)
        print(self.Type)
        print(self.Analog)
        print("----------")
