import numpy as np
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from matplotlib.patches import Polygon
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from scipy.signal import find_peaks
import matplotlib.dates as mdates
import filtersHelper
import csvHelper
from PicosConfig import picosConfigClass
from butterConfig import butterConfigClass
import pandas as pd
import sys
import matplotlib
matplotlib.use('Qt5Agg')
import sympy as sy
import scipy
from numpy import exp

from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('uiFiles/grafica.ui', self)

        self.show()
        #filtros
        self.ventanaConfig = butterConfigClass(self)
        self.button = self.findChild(QtWidgets.QPushButton, 'boton1')
        self.button.clicked.connect(self.ventanaConfig.mostrar)
        #picos
        self.picosConfig = picosConfigClass(self)
        self.buttonPícos = self.findChild(QtWidgets.QPushButton, 'pushButtonPicos')
        self.buttonPícos.clicked.connect(self.picosConfig.mostrar)

        self.grafica = self.findChild(QtWidgets.QWidget, 'grafica')
        self.matplotlibwidget = MatplotlibWidget(self.ventanaConfig)


        self.actualizarGrafico()

        self.layoutvertical = QVBoxLayout(self.grafica)
        self.layoutvertical.addWidget(self.matplotlibwidget)

    def actualizarGrafico(self):
        self.matplotlibwidget.setFiltros(self.ventanaConfig.datos)
        if(self.picosConfig.datos.checkbox):
            self.matplotlibwidget.updateGraph(self.picosConfig.datos)
        else:
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
        print("")
        self.leerDatos() #esto hay que hacerlo mas eficiente
        filter_signal = filtersHelper.butterFilter(self.datosOriginales[1],datosFiltrado)
        filter_signal = filtersHelper.butterFilterDos(filter_signal)
        filter_signal = filtersHelper.RMS(filter_signal)
        self.datos[1]=filter_signal


    def updateGraph(self,datosPicos=None):
        self.ax.clear()

        # Only show ticks on the left and bottom spines
        self.ax.yaxis.set_ticks_position('left')
        self.ax.xaxis.set_ticks_position('bottom')

        self.ax.plot(self.datos[0], self.datos[1])
        self.ax.set(xlabel='time (s)', ylabel='voltage (mV)',
                    title='Grafico 1')

        if datosPicos is not None:
            print("")
            self.mostrarPicos(datosPicos)

        #------------------------------------- Aspecto
        self.ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        self.ax.xaxis.set_major_locator(MultipleLocator(1))
        self.ax.tick_params(which='minor', length=5, width=1.5, color='r')
        self.ax.set_xmargin(0)
        self.ax.grid()
        # -------------------------------------

        #self.ax.autoscale_view()
        self.mostrarIntegral()

        self.canvas.draw()
        self.figure.tight_layout()
        self.canvas.flush_events()

    def mostrarPicos(self,datosPicos):
        peaks = find_peaks(self.datos[1], height=(datosPicos.campo1*pow(10, 15)), threshold=datosPicos.campo2, distance=datosPicos.campo3)
        height = peaks[1]['peak_heights']  # list of the heights of the peaks
        peak_pos = self.datos[0][peaks[0]]  # list of the peaks positions

        tiempo=[0]                                          #odio python
        for pos in peak_pos:
            tiempo.append(pos)

        for i in range(0, height.size):
            numeroAMostrar = str("{:.2f}".format(height[i]/(pow(10,15))))
            self.ax.annotate(numeroAMostrar +"x10e15",xy=(tiempo[i+1], height[i]))


        self.ax.scatter(peak_pos, height, color='r', s=15, marker='o', label='Picos')
        self.ax.legend()

    def mostrarIntegral(self):
        a, b = 5.5, 5.7  # integral limits
        aux=self.datos[0].values

        # [0] tiempo [1]emg
        iy = []
        ix = []
        for i in range(0, aux.size):
            if(aux[i]>a and aux[i]<b):
                iy.append(self.datos[1][i])
                ix.append(aux[i])


        verts = [(a, 0), *zip(ix, iy), (b, 0)]
        poly = Polygon(verts, facecolor='0.9', edgecolor='0.5')
        self.ax.add_patch(poly)

        self.ax.set_xticks((a, b))
        self.ax.set_xticklabels(('$a$', '$b$'))
        self.ax.set_yticks([])

        self.ax.annotate('local max', xy=((a+b)/2, 0), xytext=((a+b)/2, 0))



        def getVoltajeAPartirDeUnTiempo(x):
            ret=0
            for i in range(0, aux.size):
                if (aux[i] >= x):
                    ret = self.datos[1][i]
                    break
            return int(ret)


        intr, err = scipy.integrate.quad(getVoltajeAPartirDeUnTiempo,1,1.25, limit=1000, epsabs = 10000)
        print(intr)
        #
        # f = lambda x: getVoltajeAPartirDeUnTiempo(x)
        # i = scipy.integrate.quad(f, 0, 1)
        # print(i)



        # for i in range(0, tiempo.size):
        #     print(tiempo[i])
        #     if (tiempo[i] >= num):
        #         ret = voltaje[i]
        #         break
        # return ret

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()