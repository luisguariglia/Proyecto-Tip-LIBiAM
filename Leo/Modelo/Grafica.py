class Grafica:
    def __init__(self,nombre_columna_grafica, nombre_columna_tiempo,archivo):
        self.__nombre_columna_grafica = nombre_columna_grafica
        self.__nombre_columna_tiempo = nombre_columna_tiempo
        self.__archivo = archivo

    def get_nombre_columna_grafica(self):
        return self.__nombre_columna_grafica

    def set_nombre_columna_grafica(self,nuevo_nombre):
        self.__nombre_columna_grafica = nuevo_nombre

    def get_nombre_columna_tiempo(self):
        return self.__nombre_columna_tiempo

    def set_nombre_columna_tiempo(self,nuevo_nombre):
        self.__nombre_columna_tiempo = nuevo_nombre

    def get_archivo(self):
        return self.__archivo

    def set_archivo(self,archivo):
        self.__archivo = archivo