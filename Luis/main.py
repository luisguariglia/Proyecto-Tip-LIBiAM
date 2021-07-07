from PyQt5 import QtWidgets, uic
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
import filters
import csvHelper
class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('grafica.ui', self) # Load the .ui file

        self.show() # Show the GUI

        self.ventanaConfig = graphConfig(self)
        self.button = self.findChild(QtWidgets.QPushButton, 'boton1')
        self.button.clicked.connect(self.ventanaConfig.mostrar)
        self.pintarGrafica()
        #self.ventanaConfig.aceptar.clicked.connect(self.pintarGrafica)

    def pintarGrafica(self):
        self.grafica = self.findChild(QtWidgets.QWidget, 'grafica')

        self.matplotlibwidget = MatplotlibWidget(self.ventanaConfig)
        self.matplotlibwidget.leerDatos()
        self.matplotlibwidget.setFiltros(self.ventanaConfig.datos)

        self.matplotlibwidget.graficar()
        self.layoutvertical = QVBoxLayout(self.grafica)
        self.layoutvertical.addWidget(self.matplotlibwidget)


class graphConfig(QtWidgets.QMainWindow):
    def __init__(self,padre):
        super(graphConfig, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('graphConfig.ui', self)  # Load the .ui file
        self.aceptar=self.findChild(QtWidgets.QPushButton, 'aceptar')
        self.cancelar = self.findChild(QtWidgets.QPushButton, 'cancelar')
        self.cancelar.clicked.connect(self.close)
        self.aceptar.clicked.connect(self.modificarFiltro)
        self.datos = datosFiltrado()
        self.findChild(QtWidgets.QSpinBox, 'order').setValue(self.datos.order)
        self.findChild(QtWidgets.QDoubleSpinBox, 'numA').setValue(self.datos.arrayA)
        self.findChild(QtWidgets.QDoubleSpinBox, 'numB').setValue(self.datos.arrayB)

        #‘lowpass’, ‘highpass’, ‘bandpass’, ‘bandstop’
        self.findChild(QtWidgets.QComboBox, 'comboBoxType').addItems(["lowpass","highpass","bandpass","bandstop"])
        self.findChild(QtWidgets.QComboBox, 'comboBoxAnalog').addItems(["True","False"])

        index = self.findChild(QtWidgets.QComboBox, 'comboBoxType').findText(self.datos.Type)

        if index >= 0:
            self.findChild(QtWidgets.QComboBox, 'comboBoxType').setCurrentIndex(index)

        index = self.findChild(QtWidgets.QComboBox, 'comboBoxAnalog').findText(self.datos.Analog)
        if index >= 0:
            self.findChild(QtWidgets.QComboBox, 'comboBoxAnalog').setCurrentIndex(index)

        self.padre=padre

    def mostrar(self):
        self.show()  # Show the GUI
    def modificarFiltro(self):
        # variantes de filtro
        self.datos.order = self.findChild(QtWidgets.QSpinBox, 'order').value()
        self.datos.arrayA = self.findChild(QtWidgets.QDoubleSpinBox, 'numA').value()
        self.datos.arrayB = self.findChild(QtWidgets.QDoubleSpinBox, 'numB').value()

        self.datos.Type = self.findChild(QtWidgets.QComboBox, 'comboBoxType').currentText()
        self.datos.Analog = self.findChild(QtWidgets.QComboBox, 'comboBoxAnalog').currentText()

        self.padre.pintarGrafica()
        self.close()
class datosFiltrado():
    def __init__(self):
        self.order = 3
        self.arrayA = 0.02
        self.arrayB = 0.4
        self.Type= "bandpass"
        self.Analog="True"
    def mostrar(self):
        print("----------")
        print(self.order)
        print(self.arrayA)
        print(self.arrayB)
        print(self.Type)
        print(self.Analog)
        print("----------")

class MatplotlibWidget(QWidget):
    def __init__(self,parent = None):
        super(MatplotlibWidget,self).__init__(parent)

    def leerDatos(self):
        self.datos = csvHelper.leerCSV()
    def setFiltros(self,datosFiltrado):
        filter_signal = filters.butterFilter(self.datos[1],datosFiltrado)
        filter_signal = filters.butterFilterDos(filter_signal)
        filter_signal = filters.RMS(filter_signal)
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


app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui() # Create an instance of our class
app.exec_() # Start the application