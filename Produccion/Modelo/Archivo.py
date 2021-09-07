from Modelo.EMG import EMG
from Modelo.Grafica import Grafica
from PyQt5 import QtWidgets
import funciones


class Archivo:
    def __init__(self, nombre_archivo, archivo):
        self.__nombre_archivo = nombre_archivo
        self.__archivo = archivo
        self.__electromiografias = []

    def get_nombre_archivo(self):
        return self.__nombre_archivo

    def set_nombre_archivo(self, nuevo_nombre):
        self.__nombre_archivo = nuevo_nombre

    def get_archivo(self):
        return self.__archivo

    def set_archivo(self, nuevo_archivo):
        self.__archivo = nuevo_archivo

    def get_tree_archivo(self):
        return self.__tree_archivo

    def set_tree_archivo(self, nuevo_tree):
        self.__tree_archivo = nuevo_tree

    def get_electromiografias(self):
        return self.__electromiografias

    def agregar_electromiografias(self, data_frame):
        listaEMG = funciones.listar_emg(data_frame)

        for i in range(len(listaEMG)):
            emg = EMG(listaEMG[i], "EMG " + str(i + 1))
            graficas_emg = funciones.listar_emg_especifica(str(i + 1), data_frame)

            for j in range(1, len(graficas_emg), 2):
                grafica = Grafica(graficas_emg[j], graficas_emg[j - 1], data_frame)
                emg.agregar_grafica(grafica)

            self.__electromiografias.append(emg)

    def agregar_electromiografias2(self, tree : QtWidgets.QTreeWidget):

        for i in range(tree.topLevelItemCount()):
            top_item = tree.topLevelItem(i)
            if isinstance(top_item, QtWidgets.QTreeWidgetItem):
                nombre_dir = top_item.text(0)
                emg = EMG(nombre_dir, nombre_dir)
                hijos_top_item = top_item.childCount()

                for j in range(hijos_top_item):
                    nombre = top_item.child(j).text(0)
                    index_xs = self.__archivo.columns.get_loc(nombre) - 1
                    nom_col = self.__archivo.columns[index_xs]
                    grafica = Grafica(nombre, nom_col, self.__archivo)
                    emg.agregar_grafica(grafica)

                self.__electromiografias.append(emg)



