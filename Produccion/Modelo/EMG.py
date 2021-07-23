class EMG:
    def __init__(self, nombre_emg, nombre_corto):
        self.__nombre_emg = nombre_emg
        self.__nombre_corto = nombre_corto
        self.__graficas = []

    def get_nombre_emg(self):
        return self.__nombre_emg

    def set_nombre_emg(self,nuevo_nombre_emg):
        self.__nombre_emg = nuevo_nombre_emg

    def get_nombre_corto(self):
        return self.__nombre_corto

    def set_nombre_corto(self,nuevo_nombre_corto):
        self.__nombre_corto = nuevo_nombre_corto

    def get_graficas(self):
        return self.__graficas

    def agregar_grafica(self,nuev_grafica):
        self.__graficas.append(nuev_grafica)