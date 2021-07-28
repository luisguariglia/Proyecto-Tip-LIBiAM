import pandas as p

#------->Archivo para tod0 lo relacionado a los csv
def leerCSV():
    ARCHIVO_CSV = p.read_csv(r"C:\Users\Luis\Desktop\PROYECTO\archivos\TRX_AB1.csv", skiprows=788,encoding = "ISO-8859-1")
    # ARCHIVO_CSV = ARCHIVO_CSV.loc[(ARCHIVO_CSV['X [s]'] > 5.4) & (ARCHIVO_CSV['X [s]'] < 5.85)]
    aux = rectificarGrafico(ARCHIVO_CSV)
    tiempo = aux['X [s]']
    emg = aux['GLd: EMG 1 (IM) [V]']
    return [tiempo,emg]

def rectificarGrafico(ARCHIVO_CSV):
    aux = ARCHIVO_CSV.loc[(ARCHIVO_CSV['X [s]'] > 0.25) & (ARCHIVO_CSV['X [s]'] < 2)]
    mean_df = ARCHIVO_CSV['GLd: EMG 1 (IM) [V]'].mean()

    if(mean_df<0):
        mean_df= abs(mean_df)
    ARCHIVO_CSV['GLd: EMG 1 (IM) [V]'] = ARCHIVO_CSV['GLd: EMG 1 (IM) [V]'].apply(lambda x: x + mean_df)

    return ARCHIVO_CSV
