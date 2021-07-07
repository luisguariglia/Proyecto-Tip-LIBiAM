import matplotlib.pyplot as plt
import pandas as p
from scipy.signal import filtfilt
import scipy
import numpy as np

def leerCSV():
    # skiprows=788
    ARCHIVO_CSV = p.read_csv("C:/Users/Luis/Desktop/PROYECTO/archivos/TRX_AB1.csv", skiprows=788,encoding = "ISO-8859-1")
    aux = ARCHIVO_CSV
    tiempo = aux['X [s]']
    emg = aux['GLd: EMG 1 (IM) [V]']
    return [tiempo,emg]
