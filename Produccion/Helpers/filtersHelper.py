from scipy.signal import filtfilt
import scipy
import numpy as np
from Modelo.Filtro import Filtro
import pandas as pd

# ------->archivo para tod0 lo relacionado a los filtros
def butterFilter(signal, datosFiltrado: Filtro):
    signal = np.nan_to_num(signal, copy=False)
    b, a = scipy.signal.butter(datosFiltrado.get_order(), [datosFiltrado.get_array_A(),
           datosFiltrado.get_array_B()], datosFiltrado.get_type(),analog=datosFiltrado.get_analog())
    y = scipy.signal.filtfilt(a, b, signal, axis=0)

    ret = abs(y)
    return ret

def butterFilterDos(signal):
    # envelopamento (envolvente) pasa-bajo
    signal = np.nan_to_num(signal, copy=False)
    b, a = scipy.signal.butter(4, [0.1, 0.11], 'bandpass', analog=True)
    y = scipy.signal.filtfilt(a, b, signal)
    ret = abs(y)
    return ret


def RMS(y):
    rms = np.sqrt(np.mean(y ** 2))
    return y


class datosButter():
    # valores por defecto
    def __init__(self):
        self.order = 3
        self.arrayA = 0.02
        self.arrayB = 0.4
        self.Type = "bandpass"
        self.Analog = "True"

    def mostrar(self):
        print("----------")
        print(self.order)
        print(self.arrayA)
        print(self.arrayB)
        print(self.Type)
        print(self.Analog)
        print("----------")

def recortarGrafico(signal,tiempo, datosRecorte):

    if datosRecorte[0]==0 and datosRecorte[1]==0:
        return [signal,tiempo]
    else:
        df = pd.DataFrame()
        df[tiempo.name] = tiempo
        df[signal.name] = signal

        df = df.loc[(df[tiempo.name] > datosRecorte[0]) & (df[tiempo.name] < datosRecorte[1])]

        return [df[signal.name],df[tiempo.name]]
















