class Filtro:
    def __init__(self, order=3, array_A=0.02, array_B=0.4, type="bandpass", analog=True):
        self.__order = order
        self.__array_A = array_A
        self.__array_B = array_B
        self.__type = type
        self.__analog = analog

    def get_order(self):
        return self.__order

    def set_order(self, order):
        self.__order = order

    def get_array_A(self):
        return self.__array_A

    def set_array_A(self, array_A):
        self.__array_A = array_A

    def get_array_B(self):
        return self.__array_B

    def set_array_B(self, array_B):
        self.__array_B = array_B

    def get_type(self):
        return self.__type

    def set_type(self, type):
        self.__type = type

    def get_analog(self):
        return self.__analog

    def set_analog(self, analog):
        self.__analog = analog