import time

from PyQt5 import QtWidgets, uic
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import filtersHelper
import csvHelper
from butterConfig import butterConfigClass
from PyQt5 import QtCore, QtGui, QtWidgets

import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('uiFiles/grafica.ui', self)

        self.show()
        self.ventanaConfig = butterConfigClass(self)
        self.button = self.findChild(QtWidgets.QPushButton, 'boton1')
        self.button.clicked.connect(self.ventanaConfig.mostrar)
        self.grafica = self.findChild(QtWidgets.QWidget, 'grafica')
        self.matplotlibwidget = MatplotlibWidget(self.ventanaConfig)


        self.actualizarGrafico()

        self.layoutvertical = QVBoxLayout(self.grafica)
        self.layoutvertical.addWidget(self.matplotlibwidget)

    def actualizarGrafico(self):
        self.matplotlibwidget.setFiltros(self.ventanaConfig.datos)
        self.matplotlibwidget.updateGraph()

#widget de matplotlib
class MatplotlibWidget(QWidget):

    def __init__(self,parent = None):
        super(MatplotlibWidget,self).__init__(parent)
        self.figure = Figure()

        self.canvas = FigureCanvasQTAgg(self.figure)

        self.layoutvertical = QVBoxLayout(self)

        # toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layoutvertical.addWidget(self.toolbar)
        # ---

        self.layoutvertical.addWidget(self.canvas)

        self.ax = self.figure.subplots()
        self.leerDatos()
        #

    def leerDatos(self):
        self.datosOriginales = csvHelper.leerCSV()
        self.datos=self.datosOriginales

    def setFiltros(self,datosFiltrado):
        self.leerDatos() #esto hay que hacerlo mas eficiente
        filter_signal = filtersHelper.butterFilter(self.datosOriginales[1],datosFiltrado)
        filter_signal = filtersHelper.butterFilterDos(filter_signal)
        filter_signal = filtersHelper.RMS(filter_signal)
        self.datos[1]=filter_signal

    def updateGraph(self):
        self.ax.clear()

        self.ax.plot(self.datos[0], self.datos[1])
        self.ax.set(xlabel='time (s)', ylabel='voltage (mV)',
                    title='Grafico 1')
        self.ax.grid()
        self.canvas.draw()
        self.canvas.flush_events()



app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()