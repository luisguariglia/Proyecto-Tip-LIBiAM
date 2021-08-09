class Pico:
    def __init__(self, min_height, threshold, distance):
        self.__min_height = min_height
        self.__threshold = threshold
        self.__distance = distance

    def get_min_height(self):
        return self.__min_height

    def set_min_height(self, min_height):
        self.__min_height = min_height

    def get_treshold(self):
        return self.__threshold

    def set_threshold(self, threshold):
        self.__threshold = threshold

    def get_distance(self):
        return self.__distance

    def set_distance(self, distance):
        self.__distance = distance
