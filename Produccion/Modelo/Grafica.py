from Modelo.Filtro import Filtro

class Grafica:
    def __init__(self, nombre_columna_grafica, nombre_columna_tiempo, archivo, tree_item=None, id=None,
                 nombre_columna_grafica_vista=None, numero_grafica=None, numero_archivo=None):
        self.__nombre_columna_grafica = nombre_columna_grafica
        self.__nombre_columna_tiempo = nombre_columna_tiempo
        self.__archivo = archivo
        self.__tree_item = tree_item
        self.__id = id
        self.__nombre_columna_grafica_vista = nombre_columna_grafica_vista
        self.__filtro = Filtro()
        self.__recorte = [0, 0]
        self.__offset = [0.25, 2, True]  # [valor,valor,si se muestra o no]
        self.__valores_pico = None
        self.__integral = [0, 0, False]  # [valor,valor,si se muestra o no]
        self.__numero_grafica = numero_grafica
        self.__numero_archivo = numero_archivo
        self.__exponente = None
        self.__valores_pico_para_exportar = None
        self.__valor_integral_para_exportar = None
        self.__rms = None  # valor rms
        self.__rmsLimites = [0, 0, False]  # [valor,valor,si se muestra o no]
        self.__recortandoConClick = 0
        self.__fastfouriertransform = None


    def get_nombre_columna_grafica(self):
        return self.__nombre_columna_grafica

    def set_nombre_columna_grafica(self, nuevo_nombre):
        self.__nombre_columna_grafica = nuevo_nombre

    def get_nombre_columna_tiempo(self):
        return self.__nombre_columna_tiempo

    def set_nombre_columna_tiempo(self, nuevo_nombre):
        self.__nombre_columna_tiempo = nuevo_nombre

    def get_archivo(self):
        return self.__archivo

    def set_archivo(self, archivo):
        self.__archivo = archivo

    def get_tree_item(self):
        return self.__tree_item

    def set_tree_item(self, tree_item):
        self.__tree_item = tree_item

    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def get_nombre_columna_grafica_vista(self):
        return self.__nombre_columna_grafica_vista

    def set_nombre_columna_grafica_vista(self, nombre_columna_grafica_vista):
        self.__nombre_columna_grafica_vista = nombre_columna_grafica_vista

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

    def get_integral(self):
        return self.__integral

    def set_integral(self, num):
        self.__integral = num

    def get_numero_grafica(self):
        return self.__numero_grafica

    def set_numero_grafica(self, numero_grafica):
        self.__numero_grafica = numero_grafica

    def get_numero_archivo(self):
        return self.__numero_archivo

    def set_numero_archivo(self, numero_archivo):
        self.__numero_archivo = numero_archivo

    def get_exponente(self):
        return self.__exponente

    def set_exponente(self, exponente):
        self.__exponente = exponente

    def get_valores_pico_para_exportar(self):
        return self.__valores_pico_para_exportar

    def set_valores_pico_para_exportar(self, valores_pico_para_exportar):
        self.__valores_pico_para_exportar = valores_pico_para_exportar

    def get_valor_integral_para_exportar(self):
        return self.__valor_integral_para_exportar

    def set_valor_integral_para_exportar(self, valor_integral_para_exportar):
        self.__valor_integral_para_exportar = valor_integral_para_exportar

    def get_rmsLimites(self):
        return self.__rmsLimites

    def set_rmsLimites(self, limites):
        self.__rmsLimites = limites

    def get_rms(self):
        return self.__rms

    def set_rms(self, rms):
        self.__rms = rms

    def get_recortandoConClick(self):
        return self.__recortandoConClick

    def set_recortandoConClick(self, valor):
        self.__recortandoConClick = valor

    def aplicarValoresBrutos(self):
        self.__filtro = None
        self.__recorte = [0, 0]
        self.__offset = [0, 0, True]  # [valor,valor,si se muestra o no]
        self.__valores_pico = None
        self.__integral = [0, 0, False]  # [valor,valor,si se muestra o no]
        self.__valores_pico_para_exportar = None
        self.__valor_integral_para_exportar = None
        self.__rms = None
        self.__rmsLimites = [0, 0, False]  # [valor,valor,si se muestra o no]
        self.__fastfouriertransform = None

    def set_fastfouriertransform(self, fft):
        self.__fastfouriertransform = fft

    def get_fastfouriertransform(self):
        return self.__fastfouriertransform

    def borrarIntegralYRMS(self):
        self.__integral = [0, 0, False]
        self.__rms = None
        self.__rmsLimites = [0, 0, False]

    def getlimitesTiempo(self):
        if self.__recorte != [0, 0]:
            return self.__recorte
        else:
            return [0,self.__nombre_columna_tiempo.iloc[-1]] #ultimo elemento

