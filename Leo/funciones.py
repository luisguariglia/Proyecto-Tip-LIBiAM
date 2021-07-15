import pandas as pd

def listar_emg_especifica(emg_seleccionada, archivo_csv):
    """
    Busca solamente las columnas especificas a una EMG seleccionada previamente.

    :param emg_seleccionada: Es el nombre de la electromiografía seleccionada, por ejemplo "EMG 1" (String)
    :archivo_csv: Un archivo con extensión ".csv"
    :return: Retorna una lista con todas las columnas relacionadas a la EMG seleccionada previamente.
    """
    emg = emg_seleccionada
    datos = archivo_csv
    columnas = datos.columns
    encontrado = False
    lista = []
    for i in range(len(columnas)):  # SALTEARSE LA COLUMNA X[S]
        cadena = columnas[i]

        if encontrado:  # AGREGA LAS COLUMNAS DE CADA DATO DE LA EMG A LA LISTA HASTA ENCONTRAR LA SIGUIENTE
            if cadena.find('EMG') != -1:
                lista.pop()
                break
            else:
                lista.append(cadena)

        if cadena.find(emg) > -1:  # BUSCA LA COLUMNA DE LA EMG SOLICITADA
            encontrado = True
            lista.append(columnas[i - 1])
            lista.append(columnas[i])

    return lista


def listar_emg(archivo_csv):
    """
    Busca en cada columna la palabra EMG y la agrega a una lista.

    :param archivo_csv: Un archivo con extensión ".csv"
    :return: Retorna una lista con todas las columnas que contienen la palabra EMG.
    """

    datos = archivo_csv
    columnas = datos.columns
    lista = []
    for i in range(1, len(columnas), 2):  # SALTEARSE LA COLUMNA X[S]
        cadena = columnas[i]
        if cadena.find('EMG') > -1:
            lista.append(cadena)

    return lista
