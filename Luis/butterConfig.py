from PyQt5 import QtWidgets, uic
import filtersHelper

#------->ventana de configuracion de filtro butter
class butterConfigClass(QtWidgets.QMainWindow):
    def __init__(self,padre):
        super(butterConfigClass, self).__init__()
        uic.loadUi('uiFiles/graphConfig.ui', self)
        self.aceptar=self.findChild(QtWidgets.QPushButton, 'aceptar')
        self.cancelar = self.findChild(QtWidgets.QPushButton, 'cancelar')
        self.cancelar.clicked.connect(self.close)
        self.aceptar.clicked.connect(self.modificarFiltro)
        self.datos = filtersHelper.datosButter()
        self.findChild(QtWidgets.QSpinBox, 'order').setValue(self.datos.order)
        self.findChild(QtWidgets.QDoubleSpinBox, 'numA').setValue(self.datos.arrayA)
        self.findChild(QtWidgets.QDoubleSpinBox, 'numB').setValue(self.datos.arrayB)

        #seteo los valores iniciales en la UI
        self.findChild(QtWidgets.QComboBox, 'comboBoxType').addItems(["lowpass","highpass","bandpass","bandstop"])
        self.findChild(QtWidgets.QComboBox, 'comboBoxAnalog').addItems(["True","False"])

        index = self.findChild(QtWidgets.QComboBox, 'comboBoxType').findText(self.datos.Type)

        #indico en que pocision estan los combobox
        if index >= 0:
            self.findChild(QtWidgets.QComboBox, 'comboBoxType').setCurrentIndex(index)

        index = self.findChild(QtWidgets.QComboBox, 'comboBoxAnalog').findText(self.datos.Analog)
        if index >= 0:
            self.findChild(QtWidgets.QComboBox, 'comboBoxAnalog').setCurrentIndex(index)

        self.padre=padre

    def mostrar(self):
        self.show()
    #esto se llama cuando se le da click en aceptar
    def modificarFiltro(self):
        # variantes de filtro
        self.datos.order = self.findChild(QtWidgets.QSpinBox, 'order').value()
        self.datos.arrayA = self.findChild(QtWidgets.QDoubleSpinBox, 'numA').value()
        self.datos.arrayB = self.findChild(QtWidgets.QDoubleSpinBox, 'numB').value()

        self.datos.Type = self.findChild(QtWidgets.QComboBox, 'comboBoxType').currentText()
        self.datos.Analog = self.findChild(QtWidgets.QComboBox, 'comboBoxAnalog').currentText()

        self.padre.pintarGrafica()
        self.close()
