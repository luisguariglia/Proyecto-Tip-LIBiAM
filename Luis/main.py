from PyQt5 import QtWidgets, uic
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import filtersHelper
import csvHelper
from butterConfig import butterConfigClass


class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('uiFiles/grafica.ui', self)

        self.show()

        self.ventanaConfig = butterConfigClass(self)
        self.button = self.findChild(QtWidgets.QPushButton, 'boton1')
        self.button.clicked.connect(self.ventanaConfig.mostrar)
        self.pintarGrafica()
        self.grafica = self.findChild(QtWidgets.QWidget, 'grafica')

    def pintarGrafica(self):

        self.matplotlibwidget = MatplotlibWidget(self.ventanaConfig)
        self.matplotlibwidget.leerDatos()
        self.matplotlibwidget.setFiltros(self.ventanaConfig.datos)

        self.matplotlibwidget.graficar()
        self.layoutvertical = QVBoxLayout(self.grafica)
        self.layoutvertical.addWidget(self.matplotlibwidget)

    def pintarGraficaSegundaVez(self):

        self.layoutvertical.removeWidget(self.matplotlibwidget)

        self.matplotlibwidget = MatplotlibWidget(self.ventanaConfig)
        self.matplotlibwidget.leerDatos()
        self.matplotlibwidget.setFiltros(self.ventanaConfig.datos)

        self.matplotlibwidget.graficarSegundaVez(self.layoutvertical)
        #self.layoutvertical = QVBoxLayout(self.grafica)

        #self.layoutvertical.addWidget(self.matplotlibwidget)



#widget de matplotlib
class MatplotlibWidget(QWidget):

    def __init__(self,parent = None):
        super(MatplotlibWidget,self).__init__(parent)
    def leerDatos(self):
        self.datos = csvHelper.leerCSV()
    def setFiltros(self,datosFiltrado):

        filter_signal = filtersHelper.butterFilter(self.datos[1],datosFiltrado)
        filter_signal = filtersHelper.butterFilterDos(filter_signal)
        filter_signal = filtersHelper.RMS(filter_signal)
        self.datos[1]=filter_signal

    def graficar(self):

        self.figure = Figure()

        self.canvas = FigureCanvasQTAgg(self.figure)

        self.layoutvertical = QVBoxLayout(self)
        self.layoutvertical.addWidget(self.canvas)

        self.ax = self.figure.subplots()
        self.ax.plot(self.datos[0], self.datos[1])
        self.ax.set(xlabel='time (s)', ylabel='voltage (mV)',
               title='Grafico 1')
        self.ax.grid()
    def graficarSegundaVez(self,parametroLayout):
        #parametroLayout.removeWidget(parametroLayout.findChild(FigureCanvasQTAgg, 'canvas'))
        #parametroLayout.removeWidget(self.matplotlibwidget)
        self.figure = Figure()


        self.canvas = FigureCanvasQTAgg(self.figure)

        #parametroLayout = QVBoxLayout(self)
        #parametroLayout.
        parametroLayout.addWidget(self.canvas)

        self.ax = self.figure.subplots()
        self.ax.plot(self.datos[0], self.datos[1])
        self.ax.set(xlabel='time (s)', ylabel='voltage (mV)',
                    title='Grafico 1')
        self.ax.grid()
        self.canvas.draw()
        parametroLayout.update()



app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()