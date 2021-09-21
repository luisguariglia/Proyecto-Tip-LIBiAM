class Filtro_FFT:
    def __init__(self, n, norm):
        self.__n = n
        self.__norm = norm

    def get_n(self):
        return self.__n

    def set_n(self, n):
        self.__n = n

    def get_norm(self):
        return self.__norm

    def set_norm(self, norm):
        self.__norm = norm
