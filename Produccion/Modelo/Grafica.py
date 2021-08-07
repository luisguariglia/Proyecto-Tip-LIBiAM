from Modelo.Filtro import Filtro

class Grafica:
    def __init__(self,nombre_columna_grafica, nombre_columna_tiempo,archivo):
        self.__nombre_columna_grafica = nombre_columna_grafica
        self.__nombre_columna_tiempo = nombre_columna_tiempo
        self.__archivo = archivo
        self.__filtro = Filtro()
        self.__recorte = [0,0]
        self.__offset= [0.25,2,True]
        self.__valores_pico = None

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

    def get_filtro(self):
        return self.__filtro

    def set_filtro(self, filtro):
        self.__filtro = filtro

    def get_recorte(self):
        return self.__recorte

    def set_recorte(self, recorte):
        self.__recorte = recorte

    def get_offset(self):
        return self.__offset

    def set_offset(self, off):
        self.__offset = off

    def get_valores_picos(self):
        return self.__valores_pico

    def set_valores_picos(self, valores_picos):
        self.__valores_pico = valores_picos