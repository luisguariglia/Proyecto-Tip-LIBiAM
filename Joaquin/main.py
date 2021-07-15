from PyQt5 import QtWidgets, QtCore
from matplotlib import pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import funciones

class ScrollableWindow(QtWidgets.QMainWindow):
    def button_clicked(self):
        """
        Función para seleccionar archivo .csv, carga este archivo y luego
        genera 1 checkbox por cada electromiografía encontrada.

        :return:
        """

        options = QtWidgets.QFileDialog.Options()
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccione un archivo", "",
                                                         "Archivos CSV (*.csv);", options=options)

        # Si se cancela la ventana emergente al seleccionar un archivo .csv
        # se debe chequear si existe un archivo seleccionado o no.
        if not filepath[0]:
            return

        self.myInput.setText("")
        self.myInput.setText(filepath[0])

        # Se lee el archivo .csv para interactuar con él a futuro.
        archivo = pd.read_csv(filepath[0], encoding='cp1252', skiprows=788)
        # Con esta función se traen todas las electromiografías del archivo seleccionado.
        listaEMG = funciones.listar_emg(archivo)

        def mostrar_grafica(_self):
            """
                    Función que es asignada a cada checkbox.
                    Lista la gráfica correspondiente a cada checkbox seleccionado.

                    :return:
            """
            cant_checkboxs_checkeados = 0
            lista_checkbox_checkeados = []
            for j in range(_self.grid_checkbox.count()):
                _self.current_checkbox = getattr(_self.grid_checkbox, f"EMG {j + 1}")
                if _self.current_checkbox.isChecked():
                    lista_checkbox_checkeados.append(_self.current_checkbox)
                    cant_checkboxs_checkeados = cant_checkboxs_checkeados + 1

            _self.checkboxs = cant_checkboxs_checkeados

            if _self.checkboxs > 0:
                fig, axes = plt.subplots(nrows=cant_checkboxs_checkeados,
                                         ncols=1, figsize=(18, 4 * cant_checkboxs_checkeados))
                plt.close(fig)
                fig.tight_layout()

                _self.widget.layout().removeWidget(_self.canvas)
                _self.widget.layout().removeWidget(_self.scroll)
                _self.widget.layout().removeWidget(_self.nav)

                _self.fig = fig
                _self.canvas = FigureCanvas(_self.fig)
                _self.canvas.draw()
                _self.scroll = QtWidgets.QScrollArea(_self.widget)
                _self.scroll.setWidget(_self.canvas)
                _self.nav = NavigationToolbar(_self.canvas, _self.widget)
                _self.widget.layout().addWidget(_self.nav)
                _self.widget.layout().addWidget(_self.scroll)
                _self.widget.layout().update()

                # Si la cantidad de checkbox que se chequearon es 1, entonces solamente hay un eje y se inserta
                # la señal en ese eje.
                if  len(lista_checkbox_checkeados) == 1:
                    emg_completo = funciones.listar_emg_especifica(lista_checkbox_checkeados[0].text(), archivo)
                    axes.plot(archivo[emg_completo[0]], archivo[emg_completo[1]], linewidth=0.3,
                              label=f"Electromiografía {lista_checkbox_checkeados[0].text()}")
                    axes.set_xlabel("s")
                    axes.set_ylabel("v")
                    axes.legend()
                # En cambio si la cantidad de checkbox chequeados es mayor a 1, entonces se
                # insertan las señales en sus respectivos ejes.
                else:
                    for x in range(len(lista_checkbox_checkeados)):
                        emg_completo = funciones.listar_emg_especifica(lista_checkbox_checkeados[x].text(), archivo)
                        axes[x].plot(archivo[emg_completo[0]], archivo[emg_completo[1]], linewidth=0.3,
                                     label=f"Electromiografía {lista_checkbox_checkeados[x].text()} ")
                        axes[x].set_xlabel("s")
                        axes[x].set_ylabel("v")
                        axes[x].legend()
            else:
                _self.widget.layout().removeWidget(_self.canvas)
                _self.widget.layout().removeWidget(_self.scroll)

                _self.canvas = FigureCanvas()
                _self.canvas.draw()
                _self.scroll = QtWidgets.QScrollArea(_self.widget)
                _self.scroll.setWidget(_self.canvas)
                _self.widget.layout().addWidget(_self.scroll)
                _self.widget.layout().update()

        # Si todavía no se generó ningún checkbox es porque es la primera vez que se selecciona un archivo .csv,
        # por lo tanto se crean los checkbox normalmente.
        if self.grid_checkbox.count() == 0:
            for i in range(len(listaEMG)):
                checkBoxA = QtWidgets.QCheckBox(self)
                checkBoxA.setText(f"EMG {i + 1}")
                self.grid_checkbox.addWidget(checkBoxA, i, 1)
                setattr(self.grid_checkbox, f"EMG {i + 1}", checkBoxA)

                self.var = self.var + 30
                checkBoxA.move(25, self.var)
                checkBoxA.toggled.connect(lambda x: mostrar_grafica(self))
                checkBoxA.show()
        # En cambio, si ya existen checkbox, es debido a que no es la primera vez que se seleccionó
        # un archivo .csv, por lo tanto hay que borrar los checkboxes anteriores y crear los nuevos.
        else:
            self.var = 90
            for j in range(self.grid_checkbox.count()):
                self.current_checkbox = getattr(self.grid_checkbox, f"EMG {j + 1}")
                self.grid_checkbox.removeWidget(self.current_checkbox)

            for i in range(len(listaEMG)):
                checkBoxA = QtWidgets.QCheckBox(self)
                checkBoxA.setText(f"EMG {i + 1}")
                self.grid_checkbox.addWidget(checkBoxA, i, 1)
                setattr(self.grid_checkbox, f"EMG {i + 1}", checkBoxA)

                self.var = self.var + 30
                checkBoxA.move(25, self.var)
                checkBoxA.toggled.connect(lambda x: mostrar_grafica(self))
                checkBoxA.show()

    def __init__(self):
        self.var = 90
        self.checkboxs = 0
        self.q_app = QtWidgets.QApplication([])
        QtWidgets.QMainWindow.__init__(self)

        # Para fijar el tamaño de la ventana.
        # self.setFixedSize(1900, 1000)

        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.setWindowTitle("Ejemplo con gráficas")

        self.grid_checkbox = QtWidgets.QGridLayout()

        # Botón donde se selecciona el archivo .csv
        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Seleccione un archivo")
        self.b1.setGeometry(100, 20, 120, 30)
        self.b1.clicked.connect(self.button_clicked)

        self.myInput = QtWidgets.QLineEdit(self)
        self.myInput.setEnabled(False)
        self.myInput.setGeometry(250, 20, 500, 30)

        self.widget.setLayout(QtWidgets.QVBoxLayout())
        self.widget.layout().setContentsMargins(100, 70, 30, 30)
        self.widget.layout().setSpacing(20)

        # Se crea el canvas, es donde se insertarán las señales a medida que se chequeen los checkbox.
        self.canvas = FigureCanvas()
        self.canvas.draw()
        self.scroll = QtWidgets.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)
        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)

        self.show()
        exit(self.q_app.exec_())


if __name__ == "__main__":
    ScrollableWindow()
