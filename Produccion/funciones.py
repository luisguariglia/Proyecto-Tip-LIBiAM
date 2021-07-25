def listar_emg_especifica(emg_seleccionada, archivo_csv):
    """
        Busca solamente las columnas especificas a una EMG seleccionada previamente.
    :param
        emg_seleccionada: Es el nombre de la electromiografía seleccionada
        archivo_csv: Un archivo con extensión ".csv"
    :return:
        Retorna una lista con todas las columnas relacionadas a la EMG seleccionada previamente.
    """

    emg = "EMG " + emg_seleccionada
    encontrado = False
    lista = []
    for i in range(len(archivo_csv.columns)):
        cadena = archivo_csv.columns[i]

        if encontrado:  # AGREGA LAS COLUMNAS DE CADA DATO DE LA EMG A LA LISTA HASTA ENCONTRAR LA SIGUIENTE
            if cadena.find('EMG') != -1:
                lista.pop()
                break
            else:
                lista.append(cadena)

        if cadena.find(emg) > -1 and not encontrado :  # BUSCA LA COLUMNA DE LA EMG SOLICITADA
            encontrado = True
            lista.append(archivo_csv.columns[i - 1])
            lista.append(archivo_csv.columns[i])

    return lista


def listar_emg(archivo_csv):
    """
        Busca en cada columna la palabra EMG y la agrega a una lista.
    :param
        archivo_csv: Un archivo con extensión ".csv"
    :return:
        Retorna una lista con todas las columnas que contienen la palabra EMG.
    """

    columnas = archivo_csv.columns
    lista = []
    for i in range(1, len(columnas), 2):  # SALTEARSE LAS COLUMNAS X[S]
        cadena = columnas[i]
        if cadena.find('EMG') > -1:
            lista.append(cadena)
    return lista

def get_nombre_csv(path):
    indice = path.rfind("/") + 1
    nombre: str = ""
    for i in range(len(path) - indice):
        nombre += path[indice]
        indice += 1
    return nombre

