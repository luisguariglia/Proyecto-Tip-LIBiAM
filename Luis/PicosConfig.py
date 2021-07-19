from PyQt5 import QtWidgets, uic
import filtersHelper

#------->ventana de configuracion de picos
class picosConfigClass(QtWidgets.QMainWindow):
    def __init__(self,padre):
        super(picosConfigClass, self).__init__()
        uic.loadUi('uiFiles/picosConfig.ui', self)
        self.aceptar=self.findChild(QtWidgets.QPushButton, 'aceptar_btn')
        self.cancelar = self.findChild(QtWidgets.QPushButton, 'cancelar_btn')
        self.cancelar.clicked.connect(self.close)
        self.aceptar.clicked.connect(self.modificarFiltro)

        self.datos = datosPicos()

        self.findChild(QtWidgets.QDoubleSpinBox, 'campo1').setValue(self.datos.campo1)
        self.findChild(QtWidgets.QDoubleSpinBox, 'campo2').setValue(self.datos.campo2)
        self.findChild(QtWidgets.QDoubleSpinBox, 'campo3').setValue(self.datos.campo3)
        self.findChild(QtWidgets.QAbstractButton, 'checkBoxMostrarPicos').setChecked(True)


        self.padre=padre

    def mostrar(self):
        self.show()

    #sto se llama cuando se le da click en aceptar
    def modificarFiltro(self):
        # variantes de filtro
        self.datos.checkbox = self.findChild(QtWidgets.QAbstractButton, 'checkBoxMostrarPicos').isChecked()
        self.datos.campo1 = self.findChild(QtWidgets.QDoubleSpinBox, 'campo1').value()
        self.datos.campo2 = self.findChild(QtWidgets.QDoubleSpinBox, 'campo2').value()
        self.datos.campo3 = self.findChild(QtWidgets.QDoubleSpinBox, 'campo3').value()

        if(self.datos.checkbox):
            self.padre.actualizarGrafico(True)
        else:
            self.padre.actualizarGrafico(False)
        self.close()


class datosPicos():
    #valores por defecto
    def __init__(self):
        self.checkbox = False
        self.campo1 = 2
        self.campo2 = 1
        self.campo3 = 400