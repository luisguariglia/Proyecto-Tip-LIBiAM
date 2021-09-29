from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout
from PyQt5.QtCore import QVariant
from matplotlib import pyplot as plt

import config
from BD.Queries import Conexion
from Static.styles import estilos
from Modelo.Grafica import Grafica
from Modelo.Filtro import Filtro
from Modelo.Filtro_FFT import Filtro_FFT
from Modelo.Pico import Pico
from PyQt5.QtWidgets import QMessageBox
import numpy as np

cont = 0


class tree_widget_item_grafica(QtWidgets.QTreeWidgetItem):
    def __init__(self, text, id=None):
        super(tree_widget_item_grafica, self).__init__()
        self.setText(0, text)
        self.id = id

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id


class ventana_filtro(QtWidgets.QDialog):
    def __init__(self, parent=None, graficas=None, v=""):

        super(ventana_filtro, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Filtrado - " + v)
        self.setFixedSize(800, 420)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10, 0, 10, 10)
        self.layout().setSpacing(15)

        # PARAMETROS
        self.parent = parent
        self.graficas = graficas

        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)

        wid_izquierda = QtWidgets.QWidget()
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")
        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())
        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        wid_izquierda.setGraphicsEffect(shadow)

        wid_derecha = QtWidgets.QWidget()
        wid_derecha.setStyleSheet("background-color:white; border-radius:4px;")
        wid_derecha.setLayout(QtWidgets.QVBoxLayout())
        wid_derecha.layout().setContentsMargins(4, 14, 12, 8)
        wid_derecha.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        wid_derecha.setGraphicsEffect(shadow2)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")
        wid_izquierda.layout().addWidget(label_1, 1)

        widget_butter = QtWidgets.QWidget()
        widget_butter.setLayout(QtWidgets.QVBoxLayout())
        widget_butter.layout().setAlignment(Qt.AlignTop)
        widget_butter.layout().setContentsMargins(8, 16, 8, 0)
        widget_butter.layout().setSpacing(10)

        widget_fft = QtWidgets.QWidget()
        widget_fft.setLayout(QtWidgets.QVBoxLayout())
        widget_fft.layout().setAlignment(Qt.AlignTop)
        widget_fft.layout().setContentsMargins(8, 16, 8, 0)

        tabs = QtWidgets.QTabWidget()
        tabs.setStyleSheet(estilos.estilos_qtab_widget())
        tabs.addTab(widget_butter, "Butterworth")
        tabs.addTab(widget_fft, "FFT")

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setStyleSheet(estilos.estilos_barritas_gucci())
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id())
                item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                item.setCheckState(0, Qt.Unchecked)
                self.tree_graficas.addTopLevelItem(item)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()
        wid_btn.setStyleSheet("QWidget{margin-left:5px;")

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QVBoxLayout())
        wid_btn.layout().setAlignment(Qt.AlignLeft)
        wid_btn.layout().addWidget(btn_aplicar_a_todas)

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)

        # ORDER
        wid_label_order = QtWidgets.QWidget()
        wid_label_order.setLayout(QtWidgets.QHBoxLayout())
        wid_label_order.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_order.layout().setContentsMargins(0, 0, 0, 0)

        wid_spiner_order = QtWidgets.QWidget()
        wid_spiner_order.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_order.layout().setContentsMargins(0, 0, 0, 0)
        wid_spiner_order.layout().setAlignment(Qt.AlignRight)

        wid_label_and_tooltip_order = QtWidgets.QWidget()
        wid_label_and_tooltip_order.setLayout(QtWidgets.QHBoxLayout())
        wid_label_and_tooltip_order.layout().setContentsMargins(0, 0, 0, 0)
        wid_label_and_tooltip_order.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_and_tooltip_order.layout().setSpacing(6)

        label_order = QtWidgets.QLabel("Orden del filtro")
        label_order.setStyleSheet("padding:0px;margin:0px;")
        label_order.setFont(font)

        self.btn_tooltip_order = QtWidgets.QPushButton()
        self.btn_tooltip_order.setStyleSheet("background-color:#114980;color:white;")
        self.btn_tooltip_order.setFixedWidth(13)
        self.btn_tooltip_order.setIcon(QtGui.QIcon(":/Static/img/tooltip.png"))
        self.btn_tooltip_order.setIconSize(QtCore.QSize(13, 13))

        # descomentar si se desea agregar tooltip a futuro
        # wid_label_and_tooltip_order.layout().addWidget(self.btn_tooltip_order)
        wid_label_and_tooltip_order.layout().addWidget(label_order)

        wid_label_order.layout().addWidget(wid_label_and_tooltip_order)

        self.spin_box = QtWidgets.QSpinBox()
        self.spin_box.setFixedWidth(60)
        self.spin_box.setValue(3)
        self.spin_box.setStyleSheet(estilos.estilos_spinbox_filtros())

        wid_label_order.layout().addWidget(label_order)
        wid_spiner_order.layout().addWidget(self.spin_box)

        wid_order = QtWidgets.QWidget()
        wid_order.setLayout(QtWidgets.QHBoxLayout())
        wid_order.layout().setContentsMargins(8, 8, 8, 0)
        wid_order.layout().addWidget(wid_label_order, 5)
        wid_order.layout().addWidget(wid_spiner_order, 5)

        # ARRAY LIKE
        wid_label_array_like = QtWidgets.QWidget()
        wid_label_array_like.setLayout(QtWidgets.QHBoxLayout())
        wid_label_array_like.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_array_like.layout().setContentsMargins(0, 0, 0, 0)

        wid_spiner_array_like = QtWidgets.QWidget()
        wid_spiner_array_like.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_array_like.layout().setContentsMargins(0, 0, 0, 0)
        wid_spiner_array_like.layout().setSpacing(8)
        wid_spiner_array_like.layout().setAlignment(Qt.AlignRight)

        wid_label_and_tooltip_arrayl = QtWidgets.QWidget()
        wid_label_and_tooltip_arrayl.setLayout(QtWidgets.QHBoxLayout())
        wid_label_and_tooltip_arrayl.layout().setContentsMargins(0, 0, 0, 0)
        wid_label_and_tooltip_arrayl.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_and_tooltip_arrayl.layout().setSpacing(6)

        label_array_like = QtWidgets.QLabel("Frecuencias críticas")
        label_array_like.setStyleSheet("padding:0px;margin:0px;")
        label_array_like.setFont(font)

        self.btn_tooltip_arrayl = QtWidgets.QPushButton()
        self.btn_tooltip_arrayl.setStyleSheet("background-color:#114980;color:white;")
        self.btn_tooltip_arrayl.setFixedWidth(13)
        self.btn_tooltip_arrayl.setIcon(QtGui.QIcon(":/Static/img/tooltip.png"))
        self.btn_tooltip_arrayl.setIconSize(QtCore.QSize(13, 13))

        wid_label_and_tooltip_arrayl.layout().addWidget(self.btn_tooltip_arrayl)
        wid_label_and_tooltip_arrayl.layout().addWidget(label_array_like)

        self.spiner_array_a = QtWidgets.QSpinBox()
        self.spiner_array_a.setFixedWidth(60)
        self.spiner_array_a.setMaximum(1000)
        self.spiner_array_a.setMinimum(0)
        self.spiner_array_a.setValue(20)
        self.spiner_array_a.setStyleSheet(estilos.estilos_spinbox_filtros())

        self.spiner_array_b = QtWidgets.QSpinBox()
        self.spiner_array_b.setFixedWidth(60)
        self.spiner_array_b.setMaximum(1000)
        self.spiner_array_b.setMinimum(0)
        self.spiner_array_b.setValue(400)
        self.spiner_array_b.setStyleSheet(estilos.estilos_spinbox_filtros())

        wid_spiner_array_like.layout().addWidget(self.spiner_array_a)
        wid_spiner_array_like.layout().addWidget(self.spiner_array_b)
        wid_label_array_like.layout().addWidget(wid_label_and_tooltip_arrayl)

        wid_array_like = QtWidgets.QWidget()
        wid_array_like.setLayout(QtWidgets.QHBoxLayout())
        wid_array_like.layout().setContentsMargins(8, 8, 8, 0)
        wid_array_like.layout().addWidget(wid_label_array_like, 5)
        wid_array_like.layout().addWidget(wid_spiner_array_like, 5)

        # BTYPE
        wid_label_btype = QtWidgets.QWidget()
        wid_label_btype.setLayout(QtWidgets.QHBoxLayout())
        wid_label_btype.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_btype.layout().setContentsMargins(0, 0, 0, 0)

        wid_label_and_tooltip_filtro = QtWidgets.QWidget()
        wid_label_and_tooltip_filtro.setLayout(QtWidgets.QHBoxLayout())
        wid_label_and_tooltip_filtro.layout().setContentsMargins(0, 0, 0, 0)
        wid_label_and_tooltip_filtro.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_and_tooltip_filtro.layout().setSpacing(6)

        label_btype = QtWidgets.QLabel("Filtro")
        label_btype.setStyleSheet("padding:0px;margin:0px;")
        label_btype.setFont(font)

        self.btn_tooltip_filtro = QtWidgets.QPushButton()
        self.btn_tooltip_filtro.setStyleSheet("background-color:#114980;color:white;")
        self.btn_tooltip_filtro.setFixedWidth(13)
        self.btn_tooltip_filtro.setIcon(QtGui.QIcon(":/Static/img/tooltip.png"))
        self.btn_tooltip_filtro.setIconSize(QtCore.QSize(13, 13))

        wid_label_and_tooltip_filtro.layout().addWidget(self.btn_tooltip_filtro)
        wid_label_and_tooltip_filtro.layout().addWidget(label_btype)
        wid_label_btype.layout().addWidget(wid_label_and_tooltip_filtro)

        self.combobox_btype = QtWidgets.QComboBox()
        self.combobox_btype.setFixedWidth(150)
        self.combobox_btype.addItem("lowpass")
        self.combobox_btype.addItem("highpass")
        self.combobox_btype.addItem("bandpass")
        self.combobox_btype.addItem("bandstop")
        self.combobox_btype.setCurrentIndex(2)
        self.combobox_btype.setStyleSheet(estilos.estilos_combobox_filtro())

        wid_combobox_btype = QtWidgets.QWidget()
        wid_combobox_btype.setLayout(QtWidgets.QHBoxLayout())
        wid_combobox_btype.layout().setContentsMargins(0, 0, 0, 0)
        wid_combobox_btype.layout().setAlignment(Qt.AlignRight)
        wid_combobox_btype.layout().addWidget(self.combobox_btype)

        wid_btype = QtWidgets.QWidget()
        wid_btype.setLayout(QtWidgets.QHBoxLayout())
        wid_btype.layout().setContentsMargins(8, 8, 8, 0)
        wid_btype.layout().addWidget(wid_label_btype, 5)
        wid_btype.layout().addWidget(wid_combobox_btype, 5)

        # ANALOG
        wid_label_analog = QtWidgets.QWidget()
        wid_label_analog.setLayout(QtWidgets.QHBoxLayout())
        wid_label_analog.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_analog.layout().setContentsMargins(0, 0, 0, 0)

        wid_label_and_tooltip_analog = QtWidgets.QWidget()
        wid_label_and_tooltip_analog.setLayout(QtWidgets.QHBoxLayout())
        wid_label_and_tooltip_analog.layout().setContentsMargins(0, 0, 0, 0)
        wid_label_and_tooltip_analog.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_and_tooltip_analog.layout().setSpacing(6)

        label_analog = QtWidgets.QLabel("Analógico")
        label_analog.setStyleSheet("padding:0px;margin:0px;")
        label_analog.setFont(font)

        self.btn_tooltip_analog = QtWidgets.QPushButton()
        self.btn_tooltip_analog.setStyleSheet("background-color:#114980;color:white;")
        self.btn_tooltip_analog.setFixedWidth(13)
        self.btn_tooltip_analog.setIcon(QtGui.QIcon(":/Static/img/tooltip.png"))
        self.btn_tooltip_analog.setIconSize(QtCore.QSize(13, 13))

        wid_label_and_tooltip_analog.layout().addWidget(self.btn_tooltip_analog)
        wid_label_and_tooltip_analog.layout().addWidget(label_analog)
        wid_label_analog.layout().addWidget(wid_label_and_tooltip_analog)

        self.combobox_analog = QtWidgets.QComboBox()
        self.combobox_analog.setFixedWidth(150)
        self.combobox_analog.setStyleSheet(estilos.estilos_combobox_filtro())
        self.combobox_analog.addItem("True")
        self.combobox_analog.addItem("False")
        self.combobox_analog.setCurrentIndex(0)

        wid_combobox_analog = QtWidgets.QWidget()
        wid_combobox_analog.setLayout(QtWidgets.QHBoxLayout())
        wid_combobox_analog.layout().setContentsMargins(0, 0, 0, 0)
        wid_combobox_analog.layout().setAlignment(Qt.AlignRight)
        wid_combobox_analog.layout().addWidget(self.combobox_analog)

        wid_analog = QtWidgets.QWidget()
        wid_analog.setLayout(QtWidgets.QHBoxLayout())
        wid_analog.layout().setContentsMargins(8, 8, 8, 0)
        wid_analog.layout().addWidget(wid_label_analog, 5)
        wid_analog.layout().addWidget(wid_combobox_analog, 5)

        #CHECKBOX RANCIO.
        wid_checkbox_butter = QtWidgets.QWidget()
        wid_checkbox_butter.setLayout(QtWidgets.QHBoxLayout())
        wid_checkbox_butter.layout().setContentsMargins(8, 5, 0, 0)
        wid_checkbox_butter.layout().setAlignment(Qt.AlignLeft)
        wid_checkbox_butter.layout().setSpacing(0)

        label_checkbox = QtWidgets.QLabel("Aplicar Filtro Butterworth")
        label_checkbox.setFont(font)
        label_checkbox.setStyleSheet("margin:0px;")

        self.checkbox_butter = QtWidgets.QCheckBox()

        wid_checkbox_butter.layout().addWidget(self.checkbox_butter)
        wid_checkbox_butter.layout().addWidget(label_checkbox)

        # SE AGREGA CADA CONFIGURACIÓN EN ESTE ORDEN A LA VISTA
        widget_butter.layout().addWidget(wid_order)
        widget_butter.layout().addWidget(wid_array_like)
        widget_butter.layout().addWidget(wid_btype)
        widget_butter.layout().addWidget(wid_analog)
        widget_butter.layout().addWidget(wid_checkbox_butter)

        # BOTÓN APLICAR FILTROS
        wid_btn_aplicar = QtWidgets.QWidget()
        wid_btn_aplicar.setLayout(QtWidgets.QHBoxLayout())
        wid_btn_aplicar.layout().setContentsMargins(0, 0, 0, 0)
        wid_btn_aplicar.layout().setAlignment(Qt.AlignRight)

        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.aplicar_valores_filtro)
        btn_aplicar.setFixedWidth(80)
        btn_aplicar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn_aplicar.layout().addWidget(btn_aplicar)

        wid_derecha.layout().addWidget(tabs, 9)
        wid_derecha.layout().addWidget(wid_btn_aplicar, 1)

        self.layout().addWidget(wid_izquierda, 5)
        self.layout().addWidget(wid_derecha, 5)

        # FFT

        # VALOR1
        wid_spiner_valor1 = QtWidgets.QWidget()
        wid_spiner_valor1.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_valor1.layout().setContentsMargins(0, 0, 0, 0)
        wid_spiner_valor1.layout().setAlignment(Qt.AlignRight)

        wid_label_and_tooltip_valor1 = QtWidgets.QWidget()
        wid_label_and_tooltip_valor1.setLayout(QtWidgets.QHBoxLayout())
        wid_label_and_tooltip_valor1.layout().setContentsMargins(0, 0, 0, 0)
        wid_label_and_tooltip_valor1.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_and_tooltip_valor1.layout().setSpacing(6)

        label_valor1 = QtWidgets.QLabel("Valor 1")
        label_valor1.setStyleSheet("padding:0px;margin:0px;")
        label_valor1.setFont(font)

        self.btn_tooltip_valor1 = QtWidgets.QPushButton()
        self.btn_tooltip_valor1.setStyleSheet("background-color:#114980;color:white;")
        self.btn_tooltip_valor1.setFixedWidth(13)
        self.btn_tooltip_valor1.setIcon(QtGui.QIcon(":/Static/img/tooltip.png"))
        self.btn_tooltip_valor1.setIconSize(QtCore.QSize(13, 13))

        wid_label_and_tooltip_valor1.layout().addWidget(self.btn_tooltip_valor1)
        wid_label_and_tooltip_valor1.layout().addWidget(label_valor1)

        self.spin_box_valor1 = QtWidgets.QDoubleSpinBox()
        self.spin_box_valor1.setValue(0.002)
        self.spin_box_valor1.setMinimum(0)
        self.spin_box_valor1.setMaximum(100000)
        self.spin_box_valor1.setDecimals(4)
        self.spin_box_valor1.setMaximumWidth(90)
        self.spin_box_valor1.setStyleSheet(estilos.estilos_double_spinbox_filtros())
        wid_spiner_valor1.layout().addWidget(self.spin_box_valor1)

        wid_valor1 = QtWidgets.QWidget()
        wid_valor1.setLayout(QtWidgets.QHBoxLayout())
        wid_valor1.layout().setContentsMargins(8, 8, 8, 0)
        wid_valor1.layout().addWidget(wid_label_and_tooltip_valor1, 5)
        wid_valor1.layout().addWidget(wid_spiner_valor1, 5)

        widget_fft.layout().addWidget(wid_valor1)

        # VALOR2
        wid_spiner_valor2 = QtWidgets.QWidget()
        wid_spiner_valor2.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_valor2.layout().setContentsMargins(0, 0, 0, 0)
        wid_spiner_valor2.layout().setAlignment(Qt.AlignRight)

        wid_label_and_tooltip_valor2 = QtWidgets.QWidget()
        wid_label_and_tooltip_valor2.setLayout(QtWidgets.QHBoxLayout())
        wid_label_and_tooltip_valor2.layout().setContentsMargins(0, 0, 0, 0)
        wid_label_and_tooltip_valor2.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_and_tooltip_valor2.layout().setSpacing(6)

        label_valor2 = QtWidgets.QLabel("Valor 2")
        label_valor2.setStyleSheet("padding:0px;margin:0px;")
        label_valor2.setFont(font)

        self.btn_tooltip_valor2 = QtWidgets.QPushButton()
        self.btn_tooltip_valor2.setStyleSheet("background-color:#114980;color:white;")
        self.btn_tooltip_valor2.setFixedWidth(13)
        self.btn_tooltip_valor2.setIcon(QtGui.QIcon(":/Static/img/tooltip.png"))
        self.btn_tooltip_valor2.setIconSize(QtCore.QSize(13, 13))

        wid_label_and_tooltip_valor2.layout().addWidget(self.btn_tooltip_valor2)
        wid_label_and_tooltip_valor2.layout().addWidget(label_valor2)

        self.combobox_normtype = QtWidgets.QComboBox()
        self.combobox_normtype.setFixedWidth(150)
        self.combobox_normtype.addItem("forward")
        self.combobox_normtype.addItem("ortho")
        self.combobox_normtype.addItem("backward")
        self.combobox_normtype.setCurrentIndex(2)
        self.combobox_normtype.setStyleSheet(estilos.estilos_combobox_filtro())

        wid_combobox_btype = QtWidgets.QWidget()
        wid_combobox_btype.setLayout(QtWidgets.QHBoxLayout())
        wid_combobox_btype.layout().setContentsMargins(0, 0, 0, 0)
        wid_combobox_btype.layout().setAlignment(Qt.AlignRight)
        wid_combobox_btype.layout().addWidget(self.combobox_normtype)

        wid_spiner_valor2.layout().addWidget(self.combobox_normtype)

        #CHECKBOX RANCIO 2.
        wid_checkbox_fft = QtWidgets.QWidget()
        wid_checkbox_fft.setLayout(QtWidgets.QHBoxLayout())
        wid_checkbox_fft.layout().setContentsMargins(8, 5, 0, 0)
        wid_checkbox_fft.layout().setAlignment(Qt.AlignLeft)
        wid_checkbox_fft.layout().setSpacing(0)

        label_checkbox_fft = QtWidgets.QLabel("Aplicar Filtro FFT")
        label_checkbox_fft.setFont(font)
        label_checkbox_fft.setStyleSheet("margin:0px;")

        self.checkbox_fft= QtWidgets.QCheckBox()

        wid_checkbox_fft.layout().addWidget(self.checkbox_fft)
        wid_checkbox_fft.layout().addWidget(label_checkbox_fft)

        wid_valor2 = QtWidgets.QWidget()
        wid_valor2.setLayout(QtWidgets.QHBoxLayout())
        wid_valor2.layout().setContentsMargins(8, 8, 8, 0)
        wid_valor2.layout().addWidget(wid_label_and_tooltip_valor2, 5)
        wid_valor2.layout().addWidget(wid_spiner_valor2, 5)

        widget_fft.layout().addWidget(wid_valor2)
        widget_fft.layout().addWidget(wid_checkbox_fft)

        # PARA CAPTURAR EL EVENTO HOVER Y LANZAR UN TOOLTIP MÁS RÁPIDO QUE LOS QUE OFRECE QPushButton
        self.btn_tooltip_order.installEventFilter(self)
        self.btn_tooltip_arrayl.installEventFilter(self)
        self.btn_tooltip_filtro.installEventFilter(self)
        self.btn_tooltip_analog.installEventFilter(self)
        self.btn_tooltip_valor1.installEventFilter(self)
        self.btn_tooltip_valor2.installEventFilter(self)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.showTime)

        self.msgBox = QMessageBox(self)
        self.msgBox.setText("Filtros aplicados correctamente.")
        self.msgBox.setWindowTitle("ABS")
        self.msgBox.setStandardButtons(QMessageBox.Ok)

    def showTime(self):
        self.msgBox.close()

    def eventFilter(self, source, event):

        if source == self.btn_tooltip_order and event.type() == event.HoverEnter:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "Tooltip order", self.btn_tooltip_order)
            return True
        elif source == self.btn_tooltip_arrayl and event.type() == event.HoverEnter:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "Las frecuencias críticas indicadas en Hz.",
                                        self.btn_tooltip_arrayl)
            return True
        elif source == self.btn_tooltip_filtro and event.type() == event.HoverEnter:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "Filtro el cual será aplicado a las "
                                                    "gráficas\nseleccionadas. El valor predeterminado\nes bandpass.",
                                        self.btn_tooltip_filtro)
            return True
        elif source == self.btn_tooltip_analog and event.type() == event.HoverEnter:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "Si el valor seleccionado es True, se aplica\nun filtro "
                                                             "analógico; si es False, se aplica un\nfiltro digital.",
                                        self.btn_tooltip_analog)
            return True
        elif source == self.btn_tooltip_valor1 and event.type() == event.HoverEnter:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "Longitud del eje transformado de la salida.\n Si n es "
                                                             "menor que la longitud de la entrada, la entrada se "
                                                             "recorta.\n Si es mayor, la entrada se rellena con "
                                                             "ceros.",
                                        self.btn_tooltip_valor1)
            return True
        elif source == self.btn_tooltip_valor2 and event.type() == event.HoverEnter:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "El valor predeterminado es backward.\n Indica qué "
                                                             "dirección del par de transformadas forward / backward\n "
                                                             "se escala y con qué factor de normalización.",
                                        self.btn_tooltip_valor2)
            return True

        return super().eventFilter(source, event)

    def seleccionar_todas_las_graficas(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if not hijo.checkState(0):
                    hijo.setCheckState(0, Qt.Checked)

    def aplicar_valores_filtro(self):
        # * -------- Filtro Butterworth------------------* #
        hay_almenos_un_check = False
        order = self.spin_box.value()
        array_a = int(self.spiner_array_a.value()) * 0.001
        array_b = int(self.spiner_array_b.value()) * 0.001
        btype = self.combobox_btype.currentText()
        analog = None
        seguir = True
        # *-----------------------------------------------* #

        # * ------------- Filtro FFT * -------------------* #
        norm = self.combobox_normtype.currentText()
        n = self.spin_box_valor1.value()
        # * ------------- Filtro FFT * -------------------* #


        # *--------------------------------------------- CONTROLES --------------------------------------------------* #
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if hijo.checkState(0):
                    hay_almenos_un_check = True
                    break

        if not hay_almenos_un_check:
            QMessageBox.information(self, "Advertencia",
                                    "Seleccione al menos una gráfica")
            seguir = False
        elif not hay_almenos_un_check and order == 0:
            QMessageBox.information(self, "Advertencia",
                                    "El orden del filtro no puede ser 0")
            seguir = False

        # *--------------------------------------------- FIN DE CONTROLES  ------------------------------------------* #

        if self.combobox_analog.currentText() == "True":
            analog = True
        else:
            analog = False

        mostrarButter = self.checkbox_butter.isChecked()
        mostrarFFT = self.checkbox_fft.isChecked()

        if self.graficas is not None and seguir:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            if mostrarButter:
                                grafica.set_filtro(Filtro(order, array_a, array_b, btype, analog))
                            if mostrarFFT:
                                grafica.set_fastfouriertransform(Filtro_FFT(n, norm))

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)
                self.hide()
                self.timer.start(1550)
                self.msgBox.exec_()
                self.close()

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux


class ventana_comparar(QtWidgets.QDialog):
    def __init__(self, parent=None, graficas=None, v=""):
        super(ventana_comparar, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Comparar gráficas - " + v)
        self.setFixedSize(420, 470)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10, 0, 10, 10)
        self.layout().setSpacing(10)

        # PARAMETROS
        self.parent = parent
        self.graficas = graficas

        wid_izquierda = QtWidgets.QWidget()
        wid_derecha = QtWidgets.QWidget()

        # SOMBRAS
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        wid_izquierda.setGraphicsEffect(shadow)

        # ESTILOS
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")

        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())

        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setStyleSheet(estilos.estilos_barritas_gucci())
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id())
                item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                item.setCheckState(0, Qt.Unchecked)
                self.tree_graficas.addTopLevelItem(item)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()
        wid_btn.setStyleSheet("QWidget{margin-left:5px;")

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QHBoxLayout())
        wid_btn.layout().addWidget(btn_aplicar_a_todas)

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        # BOTÓN APLICAR FILTROS
        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.mostrar_comparacion_graficas)
        btn_aplicar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn.layout().addWidget(btn_aplicar)

        self.layout().addWidget(wid_izquierda, 5)
        self.layout().addWidget(wid_derecha, 5)

    def seleccionar_todas_las_graficas(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if not hijo.checkState(0):
                    hijo.setCheckState(0, Qt.Checked)

    def mostrar_comparacion_graficas(self):
        graficas = []

        if self.graficas is not None:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            graficas.append(grafica)
        # *--------------------------------------------- CONTROLES --------------------------------------------------* #
        if len(graficas) >= 2:
            self.parent.comparar_graficas(graficas)
            self.close()
        else:
            QMessageBox.warning(self, "Advertencia",
                                "Debe seleccionar 2 o más gráficas.")
        # *--------------------------------------------- FIN DE CONTROLES -------------------------------------------* #

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux


class ventana_valores_en_graficas(QtWidgets.QDialog):
    def __init__(self, parent=None, graficas=None, v=""):
        super(ventana_valores_en_graficas, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Valores en grafica - " + v)
        self.setFixedSize(800, 420)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10, 0, 10, 10)
        self.layout().setSpacing(15)

        # PARAMETROS
        self.parent = parent
        self.graficas = graficas

        # SOMBRAS
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)

        # ESTILOS
        wid_izquierda = QtWidgets.QWidget()
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")
        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())
        wid_izquierda.setGraphicsEffect(shadow)
        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

        wid_derecha = QtWidgets.QWidget()
        wid_derecha.setStyleSheet("background-color:white; border-radius:4px;")
        wid_derecha.setLayout(QtWidgets.QVBoxLayout())
        wid_derecha.layout().setContentsMargins(4, 14, 12, 8)
        wid_derecha.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        wid_derecha.setGraphicsEffect(shadow2)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")
        wid_izquierda.layout().addWidget(label_1, 1)

        widget_valores_pico = QtWidgets.QWidget()
        widget_valores_pico.setLayout(QtWidgets.QVBoxLayout())
        widget_valores_pico.layout().setAlignment(Qt.AlignTop)
        widget_valores_pico.layout().setContentsMargins(8, 16, 8, 0)
        widget_valores_pico.layout().setSpacing(10)

        widget_integral = QtWidgets.QWidget()
        widget_integral.setLayout(QtWidgets.QVBoxLayout())
        widget_integral.layout().setAlignment(Qt.AlignTop)
        widget_integral.layout().setContentsMargins(8, 16, 8, 0)
        widget_integral.layout().setSpacing(10)

        widget_valor_rms = QtWidgets.QWidget()
        widget_valor_rms.setLayout(QtWidgets.QVBoxLayout())
        widget_valor_rms.layout().setAlignment(Qt.AlignTop)
        widget_valor_rms.layout().setContentsMargins(8, 16, 8, 0)
        widget_valor_rms.layout().setSpacing(10)

        tabs = QtWidgets.QTabWidget()
        tabs.setStyleSheet(estilos.estilos_qtab_widget())
        tabs.addTab(widget_valores_pico, "Valores picos")
        tabs.addTab(widget_integral, "Integral")
        tabs.addTab(widget_valor_rms, "Valor RMS")

        wid_derecha.layout().addWidget(tabs, 9)

        # ALTURA MÍNIMA
        wid_min_height = QtWidgets.QWidget()
        wid_min_height.setLayout(QtWidgets.QHBoxLayout())
        wid_min_height.layout().setContentsMargins(8, 8, 8, 0)
        wid_min_height.layout().setSpacing(0)

        wid_label_and_tooltip_AM = QtWidgets.QWidget()
        wid_label_and_tooltip_AM.setLayout(QtWidgets.QHBoxLayout())
        wid_label_and_tooltip_AM.layout().setContentsMargins(0, 0, 0, 0)
        wid_label_and_tooltip_AM.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_and_tooltip_AM.layout().setSpacing(6)

        label_min_height = QtWidgets.QLabel("Altura Mínima")
        label_min_height.setStyleSheet("padding:0px;margin:0px;")
        label_min_height.setFont(font)

        self.btn_tooltip_AM = QtWidgets.QPushButton()
        self.btn_tooltip_AM.setStyleSheet("background-color:#114980;color:white;")
        self.btn_tooltip_AM.setFixedWidth(13)
        self.btn_tooltip_AM.setIcon(QtGui.QIcon(":/Static/img/tooltip.png"))
        self.btn_tooltip_AM.setIconSize(QtCore.QSize(13, 13))

        wid_label_and_tooltip_AM.layout().addWidget(self.btn_tooltip_AM)
        wid_label_and_tooltip_AM.layout().addWidget(label_min_height)

        self.spinbox_min_height = QtWidgets.QDoubleSpinBox()
        self.spinbox_min_height.setValue(0.002)
        self.spinbox_min_height.setMinimum(0)
        self.spinbox_min_height.setMaximum(100000)
        self.spinbox_min_height.setDecimals(4)
        self.spinbox_min_height.setMaximumWidth(90)
        self.spinbox_min_height.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_min_height.layout().addWidget(wid_label_and_tooltip_AM, 5)
        wid_min_height.layout().addWidget(self.spinbox_min_height, 2)
        widget_valores_pico.layout().addWidget(wid_min_height)

        # UMBRAL
        wid_threshold = QtWidgets.QWidget()
        wid_threshold.setLayout(QtWidgets.QHBoxLayout())
        wid_threshold.layout().setAlignment(Qt.AlignTop)
        wid_threshold.layout().setContentsMargins(8, 8, 8, 0)

        wid_label_and_tooltip_U = QtWidgets.QWidget()
        wid_label_and_tooltip_U.setLayout(QtWidgets.QHBoxLayout())
        wid_label_and_tooltip_U.layout().setContentsMargins(0, 0, 0, 0)
        wid_label_and_tooltip_U.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_and_tooltip_U.layout().setSpacing(6)

        label_threshold = QtWidgets.QLabel("Umbral")
        label_threshold.setStyleSheet("padding:0px;margin:0px;")
        label_threshold.setFont(font)

        self.btn_tooltip_umbral = QtWidgets.QPushButton()
        self.btn_tooltip_umbral.setStyleSheet("background-color:#114980;color:white;")
        self.btn_tooltip_umbral.setFixedWidth(13)
        self.btn_tooltip_umbral.setIcon(QtGui.QIcon(":/Static/img/tooltip.png"))
        self.btn_tooltip_umbral.setIconSize(QtCore.QSize(13, 13))

        wid_label_and_tooltip_U.layout().addWidget(self.btn_tooltip_umbral)
        wid_label_and_tooltip_U.layout().addWidget(label_threshold)

        self.spinbox_threshold = QtWidgets.QDoubleSpinBox()
        self.spinbox_threshold.setValue(0.0)
        self.spinbox_threshold.setMinimum(0)
        self.spinbox_threshold.setMaximum(20)  # Puede cambiar. (La máxima señal que vi llegaba a 8)
        self.spinbox_threshold.setDecimals(3)  # Tiene que tener mínimo 3 decimales, no sé si hay señales más chicas.
        self.spinbox_threshold.setMaximumWidth(90)
        self.spinbox_threshold.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_threshold.layout().addWidget(wid_label_and_tooltip_U, 5)
        wid_threshold.layout().addWidget(self.spinbox_threshold, 2)
        widget_valores_pico.layout().addWidget(wid_threshold)

        # DISTANCIA
        wid_distance = QtWidgets.QWidget()
        wid_distance.setLayout(QtWidgets.QHBoxLayout())
        wid_distance.layout().setAlignment(Qt.AlignTop)
        wid_distance.layout().setContentsMargins(8, 8, 8, 0)

        wid_label_and_tooltip_D = QtWidgets.QWidget()
        wid_label_and_tooltip_D.setLayout(QtWidgets.QHBoxLayout())
        wid_label_and_tooltip_D.layout().setContentsMargins(0, 0, 0, 0)
        wid_label_and_tooltip_D.layout().setAlignment(Qt.AlignHCenter | Qt.AlignLeft)
        wid_label_and_tooltip_D.layout().setSpacing(6)

        label_distance = QtWidgets.QLabel("Distancia")
        label_distance.setStyleSheet("padding:0px;margin:0px;")
        label_distance.setFont(font)

        self.btn_tooltip_distancia = QtWidgets.QPushButton()
        self.btn_tooltip_distancia.setStyleSheet("background-color:#114980;color:white;")
        self.btn_tooltip_distancia.setFixedWidth(13)
        self.btn_tooltip_distancia.setIcon(QtGui.QIcon(":/Static/img/tooltip.png"))
        self.btn_tooltip_distancia.setIconSize(QtCore.QSize(13, 13))

        wid_label_and_tooltip_D.layout().addWidget(self.btn_tooltip_distancia)
        wid_label_and_tooltip_D.layout().addWidget(label_distance)

        self.spinbox_distance = QtWidgets.QDoubleSpinBox()
        self.spinbox_distance.setMaximum(1000)
        self.spinbox_distance.setMinimum(1)
        self.spinbox_distance.setValue(400)
        self.spinbox_distance.setMaximumWidth(90)
        self.spinbox_distance.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_distance.layout().addWidget(wid_label_and_tooltip_D, 5)
        wid_distance.layout().addWidget(self.spinbox_distance, 2)
        widget_valores_pico.layout().addWidget(wid_distance)

        wid_checkbox = QtWidgets.QWidget()
        wid_checkbox.setLayout(QtWidgets.QHBoxLayout())
        wid_checkbox.layout().setContentsMargins(8, 5, 0, 0)
        wid_checkbox.layout().setAlignment(Qt.AlignLeft)
        wid_checkbox.layout().setSpacing(0)

        label_checkbox = QtWidgets.QLabel("Mostrar Picos")
        label_checkbox.setFont(font)
        label_checkbox.setStyleSheet("margin:0px;")

        self.checkbox_mostrar_picos = QtWidgets.QCheckBox()

        wid_checkbox.layout().addWidget(self.checkbox_mostrar_picos)
        wid_checkbox.layout().addWidget(label_checkbox)
        widget_valores_pico.layout().addWidget(wid_checkbox)

        # -------------------------------------------------------------------------------INTEGRAL-----------------------------------------------------------------
        wid_inicio = QtWidgets.QWidget()
        wid_inicio.setLayout(QtWidgets.QHBoxLayout())
        wid_inicio.layout().setContentsMargins(8, 8, 8, 0)
        wid_inicio.layout().setSpacing(0)

        label_inicio = QtWidgets.QLabel("Valor inicial")
        label_inicio.setFont(font)

        self.spinbox_inicio = QtWidgets.QDoubleSpinBox()
        self.spinbox_inicio.setValue(0.0)
        self.spinbox_inicio.setMaximumWidth(90)
        self.spinbox_inicio.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_inicio.layout().addWidget(label_inicio, 5)
        wid_inicio.layout().addWidget(self.spinbox_inicio, 2)
        widget_integral.layout().addWidget(wid_inicio)

        # segundo parametro
        wid_fin = QtWidgets.QWidget()
        wid_fin.setLayout(QtWidgets.QHBoxLayout())
        wid_fin.layout().setContentsMargins(8, 8, 8, 0)
        wid_fin.layout().setSpacing(0)

        label_fin = QtWidgets.QLabel("Valor final")
        label_fin.setFont(font)

        self.spinbox_fin = QtWidgets.QDoubleSpinBox()
        self.spinbox_fin.setValue(0.0)
        self.spinbox_fin.setMaximumWidth(90)
        self.spinbox_fin.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_fin.layout().addWidget(label_fin, 5)
        wid_fin.layout().addWidget(self.spinbox_fin, 2)
        widget_integral.layout().addWidget(wid_fin)

        # checkbox
        wid_checkbox_integral = QtWidgets.QWidget()
        wid_checkbox_integral.setLayout(QtWidgets.QHBoxLayout())
        wid_checkbox_integral.layout().setContentsMargins(8, 5, 0, 0)
        wid_checkbox_integral.layout().setAlignment(Qt.AlignLeft)
        wid_checkbox_integral.layout().setSpacing(0)

        label_checkbox_integral = QtWidgets.QLabel("Mostrar Integral")
        label_checkbox_integral.setFont(font)
        label_checkbox_integral.setStyleSheet("margin:0px;")

        self.checkbox_mostrar_integral = QtWidgets.QCheckBox()

        wid_checkbox_integral.layout().addWidget(self.checkbox_mostrar_integral)
        wid_checkbox_integral.layout().addWidget(label_checkbox_integral)
        widget_integral.layout().addWidget(wid_checkbox_integral)
        # -------------------------------------------------------------------------------INTEGRAL-----------------------------------------------------------------

        # -------------------------------------------------------------------------------RMS-----------------------------------------------------------------
        wid_inicioRMS = QtWidgets.QWidget()
        wid_inicioRMS.setLayout(QtWidgets.QHBoxLayout())
        wid_inicioRMS.layout().setContentsMargins(8, 8, 8, 0)
        wid_inicioRMS.layout().setSpacing(0)

        label_inicioRMS = QtWidgets.QLabel("Valor inicial")
        label_inicioRMS.setFont(font)

        self.spinbox_inicioRMS = QtWidgets.QDoubleSpinBox()
        self.spinbox_inicioRMS.setValue(0.0)
        self.spinbox_inicioRMS.setMaximumWidth(90)
        self.spinbox_inicioRMS.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_inicioRMS.layout().addWidget(label_inicioRMS, 5)
        wid_inicioRMS.layout().addWidget(self.spinbox_inicioRMS, 2)
        widget_valor_rms.layout().addWidget(wid_inicioRMS)

        # segundo parametro
        wid_finRMS = QtWidgets.QWidget()
        wid_finRMS.setLayout(QtWidgets.QHBoxLayout())
        wid_finRMS.layout().setContentsMargins(8, 8, 8, 0)
        wid_finRMS.layout().setSpacing(0)

        label_finRMS = QtWidgets.QLabel("Valor final")
        label_finRMS.setFont(font)

        self.spinbox_finRMS = QtWidgets.QDoubleSpinBox()
        self.spinbox_finRMS.setValue(0.0)
        self.spinbox_finRMS.setMaximumWidth(90)
        self.spinbox_finRMS.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_finRMS.layout().addWidget(label_finRMS, 5)
        wid_finRMS.layout().addWidget(self.spinbox_finRMS, 2)
        widget_valor_rms.layout().addWidget(wid_finRMS)

        # checkbox
        wid_checkbox_RMS = QtWidgets.QWidget()
        wid_checkbox_RMS.setLayout(QtWidgets.QHBoxLayout())
        wid_checkbox_RMS.layout().setContentsMargins(8, 5, 0, 0)
        wid_checkbox_RMS.layout().setAlignment(Qt.AlignLeft)
        wid_checkbox_RMS.layout().setSpacing(0)

        label_checkbox_RMS = QtWidgets.QLabel("Mostrar Valor RMS")
        label_checkbox_RMS.setFont(font)
        label_checkbox_RMS.setStyleSheet("margin:0px;")

        self.checkbox_mostrar_RMS = QtWidgets.QCheckBox()

        wid_checkbox_RMS.layout().addWidget(self.checkbox_mostrar_RMS)
        wid_checkbox_RMS.layout().addWidget(label_checkbox_RMS)
        widget_valor_rms.layout().addWidget(wid_checkbox_RMS)
        # -------------------------------------------------------------------------------RMS-----------------------------------------------------------------
        wid_btn_aplicar = QtWidgets.QWidget()
        wid_btn_aplicar.setLayout(QtWidgets.QHBoxLayout())
        wid_btn_aplicar.layout().setContentsMargins(0, 0, 0, 0)
        wid_btn_aplicar.layout().setAlignment(Qt.AlignRight)

        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.aplicar_valores)
        btn_aplicar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn_aplicar.layout().addWidget(btn_aplicar)
        wid_derecha.layout().addWidget(wid_btn_aplicar, 1)

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setStyleSheet(estilos.estilos_barritas_gucci())
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id())
                item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                item.setCheckState(0, Qt.Unchecked)
                self.tree_graficas.addTopLevelItem(item)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()
        wid_btn.setStyleSheet("QWidget{margin-left:5px;")

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QVBoxLayout())
        wid_btn.layout().setAlignment(Qt.AlignLeft)
        wid_btn.layout().addWidget(btn_aplicar_a_todas)

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        self.layout().addWidget(wid_izquierda, 5)
        self.layout().addWidget(wid_derecha, 5)

        # PARA CAPTURAR EL EVENTO HOVER Y LANZAR UN TOOLTIP MÁS RÁPIDO QUE LOS QUE OFRECE QPushButtons
        self.btn_tooltip_umbral.installEventFilter(self)
        self.btn_tooltip_AM.installEventFilter(self)
        self.btn_tooltip_distancia.installEventFilter(self)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.showTime)

        self.msgBox = QMessageBox(self)
        self.msgBox.setText("Valores aplicados correctamente")
        self.msgBox.setWindowTitle("ABS")
        self.msgBox.setStandardButtons(QMessageBox.Ok)

    def eventFilter(self, source, event):

        if source == self.btn_tooltip_AM and event.type() == event.HoverEnter:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "Altura mínima requerida\nEste parámetro es opcional",
                                        self.btn_tooltip_AM)
            return True
        elif source == self.btn_tooltip_umbral and event.type() == event.HoverEnter:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(),
                                        "Umbral mínimo requerido, distancia\nvertical a sus muestras vecinas.\nEste parámetro es opcional",
                                        self.btn_tooltip_umbral)
            return True
        elif source == self.btn_tooltip_distancia and event.type() == event.HoverEnter:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(),
                                        """Distancia horizontal mínima requerida (>=1)\nen muestras entre picos vecinos. Los picos más\npequeños se eliminan primero hasta que se\ncumpla la condición para todos los picos restantes.""",
                                        self.btn_tooltip_distancia)
            return True

        return super().eventFilter(source, event)

    def aplicar_valores(self):

        hay_almenos_un_check = False

        min_height = self.spinbox_min_height.value()
        treshold = self.spinbox_threshold.value()
        distance = self.spinbox_distance.value()
        mostrarPicos = self.checkbox_mostrar_picos.isChecked()

        inicio = self.spinbox_inicio.value()
        fin = self.spinbox_fin.value()
        mostrarIntegral = self.checkbox_mostrar_integral.isChecked()

        inicioRMS = self.spinbox_inicioRMS.value()
        finRMS = self.spinbox_finRMS.value()
        mostrarRMS = self.checkbox_mostrar_RMS.isChecked()

        # *------------------------------------controles------------------------------------
        seguir = True
        if mostrarIntegral and inicio >= fin:
            QMessageBox.warning(self, "Advertencia",
                                "El valor de inicio de la integral no puede ser menor o igual al valor final")
            seguir = False

        if mostrarRMS and inicioRMS >= finRMS:
            QMessageBox.warning(self, "Advertencia",
                                "El valor de inicio de RMS no puede ser menor o igual al valor final")
            seguir = False

        if not mostrarPicos and not mostrarIntegral and not mostrarRMS:
            QMessageBox.information(self, "Advertencia",
                                    "Seleccione que datos desea mostrar haciendo click en el checkbox de: \n - mostrarPicos\n - mostrarIntegral \n - mostrarRMS")
            seguir = False

        #controles de tiempo
        if self.graficas is not None and seguir:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        hay_almenos_un_check = True
                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            errorIntegral=False
                            errorRMS=False
                            limiteInicio = grafica.getLimitesTiempo()[0]
                            limiteFin = grafica.getLimitesTiempo()[1]

                            if mostrarIntegral:
                                if inicio < limiteInicio or inicio > limiteFin:
                                    seguir = False
                                    errorIntegral =True
                                elif fin < limiteInicio or fin > limiteFin:
                                    seguir = False
                                    errorIntegral =True

                            if mostrarRMS:
                                if inicioRMS < limiteInicio or inicioRMS > limiteFin:
                                    seguir = False
                                    errorRMS =True
                                elif finRMS < limiteInicio or finRMS > limiteFin:
                                    seguir = False
                                    errorRMS =True

                            if errorRMS or errorIntegral:
                                if errorRMS and not errorIntegral:
                                    mensaje="Los valores de tiempo de la ventana RMS sobrepasan los limites del grafico "
                                elif errorIntegral and not errorRMS:
                                    mensaje="Los valores de tiempo de la ventana calcular Integral sobrepasan los limites del grafico "
                                else:
                                    mensaje="Los valores de tiempo de las ventanas RMS e Integral sobrepasan los limites del grafico "
                                mensaje = mensaje + str(hijo.get_id()+1)
                                QMessageBox.information(self, "Advertencia",mensaje)

        # *------------------------------------controles------------------------------------
        if self.graficas is not None and seguir:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        hay_almenos_un_check = True

                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            if mostrarPicos:
                                grafica.set_valores_picos(Pico(min_height, treshold, distance))
                            if mostrarIntegral:
                                grafica.set_integral(([inicio, fin, mostrarIntegral]))
                            if mostrarRMS:
                                grafica.set_rmsLimites(([inicioRMS, finRMS, mostrarRMS]))

            if hay_almenos_un_check:
                self.parent.listar_graficas(valores_pico=True)
                self.hide()
                self.timer.start(1550)
                self.msgBox.exec_()
                self.close()
            else:
                QMessageBox.information(self, "Advertencia", "Seleccione al menos un grafico")

    def showTime(self):
        self.msgBox.close()

    def seleccionar_todas_las_graficas(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if not hijo.checkState(0):
                    hijo.setCheckState(0, Qt.Checked)

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux


class ventana_cortar(QtWidgets.QDialog):
    def __init__(self, parent=None, graficas=None, v=""):
        super(ventana_cortar, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        # self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Cortar Graficas - " + v)
        self.setFixedSize(770, 470)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10, 0, 10, 10)
        self.layout().setSpacing(15)

        self.cont = 0
        self.min = 0
        self.max = 0
        # PARAMETROS
        self.parent = parent
        self.graficas = graficas

        wid_izquierda = QtWidgets.QWidget()
        wid_derecha = QtWidgets.QWidget()

        # SOMBRAS
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        wid_izquierda.setGraphicsEffect(shadow)
        wid_derecha.setGraphicsEffect(shadow2)

        # ESTILOS
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")
        wid_derecha.setStyleSheet("background-color:white; border-radius:4px;")

        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())
        wid_derecha.setLayout(QtWidgets.QVBoxLayout())

        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        label_2 = QtWidgets.QLabel("CONFIGURAR RECORTE")
        label_2.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)
        wid_derecha.layout().addWidget(label_2, 1)

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setStyleSheet(estilos.estilos_barritas_gucci())
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id())
                item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                item.setCheckState(0, Qt.Unchecked)
                self.tree_graficas.addTopLevelItem(item)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()
        wid_btn.setStyleSheet("QWidget{margin-left:5px;")

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QVBoxLayout())
        wid_btn.layout().setAlignment(Qt.AlignLeft)
        wid_btn.layout().addWidget(btn_aplicar_a_todas)

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        # GROUP BOX VALORES FILTRO
        wid_content_der = QtWidgets.QWidget()
        wid_content_der.setLayout(QtWidgets.QVBoxLayout())
        wid_content_der.layout().setAlignment(Qt.AlignTop)
        wid_content_der.layout().setContentsMargins(10, 0, 0, 0)
        wid_content_der.layout().setSpacing(15)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)

        # DESDE
        wid_label_desde = QtWidgets.QWidget()
        wid_label_desde.setLayout(QtWidgets.QHBoxLayout())

        wid_spiner_desde = QtWidgets.QWidget()
        wid_spiner_desde.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_desde.layout().setContentsMargins(0, 0, 0, 0)
        wid_spiner_desde.layout().setAlignment(Qt.AlignRight)

        label_desde = QtWidgets.QLabel("Desde")
        label_desde.setFont(font)
        wid_label_desde.layout().addWidget(label_desde)

        self.spin_box = QtWidgets.QDoubleSpinBox()
        self.spin_box.setSingleStep(0.25)
        self.spin_box.setFixedWidth(60)
        self.spin_box.setValue(0)

        self.spin_box.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_label_desde.layout().addWidget(label_desde)
        wid_spiner_desde.layout().addWidget(self.spin_box)

        wid_desde = QtWidgets.QWidget()
        wid_desde.setLayout(QtWidgets.QHBoxLayout())
        wid_desde.layout().setContentsMargins(0, 0, 0, 0)
        wid_desde.layout().addWidget(wid_label_desde, 5)
        wid_desde.layout().addWidget(wid_spiner_desde, 5)

        # HASTA
        label_hasta = QtWidgets.QLabel("Hasta")
        label_hasta.setFont(font)

        wid_label_hasta = QtWidgets.QWidget()
        wid_label_hasta.setLayout(QtWidgets.QHBoxLayout())
        wid_label_hasta.layout().addWidget(label_hasta)

        self.spin_box2 = QtWidgets.QDoubleSpinBox()
        self.spin_box2.setSingleStep(0.25)
        self.spin_box2.setFixedWidth(60)
        self.spin_box2.setValue(0)
        self.spin_box2.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_combobox_hasta = QtWidgets.QWidget()
        wid_combobox_hasta.setLayout(QtWidgets.QHBoxLayout())
        wid_combobox_hasta.layout().setContentsMargins(0, 0, 0, 0)
        wid_combobox_hasta.layout().setAlignment(Qt.AlignRight)
        wid_combobox_hasta.layout().addWidget(self.spin_box2)

        wid_hasta = QtWidgets.QWidget()
        wid_hasta.setLayout(QtWidgets.QHBoxLayout())
        wid_hasta.layout().setContentsMargins(0, 0, 0, 0)

        wid_hasta.layout().addWidget(wid_label_hasta, 5)
        wid_hasta.layout().addWidget(wid_combobox_hasta, 5)

        # boton de reset
        btn_resetear = QtWidgets.QPushButton("Resetear")
        btn_resetear.clicked.connect(self.resetear_valores)
        btn_resetear.setFixedWidth(80)
        btn_resetear.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        btn_RecortarConClicks = QtWidgets.QPushButton("Recortar Haciendo Click")
        btn_RecortarConClicks.clicked.connect(self.RecortarHaciendoClick)
        btn_RecortarConClicks.setFixedWidth(140)
        btn_RecortarConClicks.setStyleSheet(estilos.estilos_btn_exportar())

        #   infooo
        label_info = QtWidgets.QLabel("<br>"
                                      "Se cortan las graficas desde un determinado valor de tiempo en segundos hasta otro valor"
                                      "<br>"
                                      "Para dejar la grafica original se deben de poner los valores de desde y hasta en 0"
                                      "<br>")
        label_info.setFont(font)
        label_info.setWordWrap(True)
        # SE AGREGA CADA CONFIGURACIÓN EN ESTE ORDEN A LA VISTA
        wid_content_der.layout().addWidget(wid_desde)
        wid_content_der.layout().addWidget(wid_hasta)
        wid_content_der.layout().addWidget(btn_resetear)
        wid_content_der.layout().addWidget(btn_RecortarConClicks)
        wid_content_der.layout().addWidget(label_info)

        # BOTÓN APLICAR RECORTE
        wid_btn_aplicar = QtWidgets.QWidget()
        wid_btn_aplicar.setLayout(QtWidgets.QHBoxLayout())
        wid_btn_aplicar.layout().setContentsMargins(0, 0, 0, 0)
        wid_btn_aplicar.layout().setAlignment(Qt.AlignRight)

        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.aplicar_recorte)
        btn_aplicar.setFixedWidth(80)
        btn_aplicar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn_aplicar.layout().addWidget(btn_aplicar)

        wid_derecha.layout().addWidget(wid_content_der, 8)
        wid_derecha.layout().addWidget(wid_btn_aplicar, 1)

        self.layout().addWidget(wid_izquierda, 5)
        self.layout().addWidget(wid_derecha, 5)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.showTime)

        self.msgBox = QMessageBox(self)
        self.msgBox.setText("Gráfica recortada correctamente")
        self.msgBox.setWindowTitle("ABS")
        self.msgBox.setStandardButtons(QMessageBox.Ok)

    def RecortarHaciendoClick(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        if cant_hijos == 1:
            self.hide()
            QMessageBox.information(self, "Info", "Por favos haga 2 click en el grafico que desea recortar")
            self.parent.setCortandoGrafico(True, False, self)
        else:
            self.hide()
            QMessageBox.information(self, "Info",
                                    "Por favos haga 2 click indicando la seccion que desea recortar \nImportante: Utilize el primer grafico")
            self.parent.setCortandoGrafico(True, True, self)

    def mostrar(self):
        self.show()
        self.parent.listar_graficas(True)

    def setRecorte(self, min, max):
        self.spin_box.setValue(min)
        self.spin_box2.setValue(max)

    def resetear_valores(self):
        self.spin_box.setValue(0)
        self.spin_box2.setValue(0)

    def seleccionar_todas_las_graficas(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if not hijo.checkState(0):
                    hijo.setCheckState(0, Qt.Checked)

    def aplicar_recorte(self):
        hay_almenos_un_check = False
        desde = self.spin_box.value()
        hasta = self.spin_box2.value()
        seguir = True
        valores_en_cero = False

        # *------------------------------------CONTROLES-------------------------------------------
        # Tengo que hacer este for rancio al menos una vez para chequear si hay algún check de las graficas chequeados.
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if hijo.checkState(0):
                    hay_almenos_un_check = True
                    break

        if hay_almenos_un_check and desde == 0 and hasta == 0:
            valores_en_cero = True

        if not hay_almenos_un_check:
            QMessageBox.information(self, "Advertencia",
                                    "Seleccione al menos una gráfica")
            seguir = False

        elif hay_almenos_un_check and hasta <= desde and not valores_en_cero:
            QMessageBox.warning(self, "Advertencia",
                                "El valor de inicio del recorte no puede ser mayor o igual al valor final.")
            seguir = False

        # controles para integral


        tieneIntegralFueradelRecorte = False
        tieneRMSFueraDelRecorte = False
        listadegraficasConProblema = []

        if self.graficas is not None and seguir:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            agregargrafica =False
                            datosIntegral = grafica.get_integral()
                            if datosIntegral[2]:
                                if desde >= datosIntegral[0] or hasta <= datosIntegral[1]:
                                    tieneIntegralFueradelRecorte = True
                                    agregargrafica=True
                            datosrms = grafica.get_rmsLimites()
                            if datosrms[2]:
                                if desde >= datosrms[0] or hasta <= datosrms[1]:
                                    tieneRMSFueraDelRecorte = True
                                    agregargrafica = True
                            if agregargrafica:
                                listadegraficasConProblema.append(grafica)


        mensaje = ""
        if tieneIntegralFueradelRecorte and not tieneRMSFueraDelRecorte:
            mensaje = "Los graficos que se van a recortar poseen una integral fuera del area de recorte \n Si continua esta integral se va a borrar"
        if tieneRMSFueraDelRecorte and not tieneIntegralFueradelRecorte:
            mensaje = "Los graficos que se van a recortar poseen un valor RMS fuera del area de recorte \n Si continua este valor se va a borrar"
        if tieneRMSFueraDelRecorte and tieneIntegralFueradelRecorte:
            mensaje = "Los graficos que se van a recortar poseen valores de Integral y RMS fuera del area de recorte \n Si continua estos valores se va a borrar"
        if mensaje != "":
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText(mensaje)
            msgBox.setWindowTitle("Advertencia")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            returnValue = msgBox.exec()
            if returnValue == QMessageBox.Ok:
                for grafica in listadegraficasConProblema:
                    grafica.borrarIntegralYRMS()
            else:
                seguir = False
        # controles de tiempo
        if self.graficas is not None and seguir:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        hay_almenos_un_check = True
                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            errorLimites = False
                            limiteInicio = grafica.getLimitesTiempo()[0]
                            limiteFin = grafica.getLimitesTiempo()[1]

                            if desde < limiteInicio or desde > limiteFin:
                                seguir = False
                                errorLimites = True
                            elif hasta < limiteInicio or hasta > limiteFin:
                                seguir = False
                                errorLimites = True

                            if errorLimites:
                                mensaje = "Los valores de tiempo sobrepasan los limites del grafico "
                                mensaje = mensaje + str(hijo.get_id() + 1)
                                QMessageBox.information(self, "Advertencia", mensaje)
        # *------------------------------------FIN DE CONTROLES------------------------------------

        if self.graficas is not None and seguir:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            grafica.set_recorte([desde, hasta])

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)
                self.hide()
                self.timer.start(1550)
                self.msgBox.exec_()
                self.close()

        if self.graficas is not None and seguir:
            return True
        else:
            self.parent.listar_graficas(True)
            return False

    def showTime(self):
        self.msgBox.close()

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux


class ventana_rectificar(QtWidgets.QDialog):
    def __init__(self, parent=None, graficas=None, v=""):
        super(ventana_rectificar, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Rectificar gráficas - " + v)
        self.setFixedSize(770, 470)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10, 0, 10, 10)
        self.layout().setSpacing(15)

        # PARAMETROS
        self.parent = parent
        self.graficas = graficas

        wid_izquierda = QtWidgets.QWidget()
        wid_derecha = QtWidgets.QWidget()

        # SOMBRAS
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        wid_izquierda.setGraphicsEffect(shadow)
        wid_derecha.setGraphicsEffect(shadow2)

        # ESTILOS
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")
        wid_derecha.setStyleSheet("background-color:white; border-radius:4px;")

        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())
        wid_derecha.setLayout(QtWidgets.QVBoxLayout())

        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        label_2 = QtWidgets.QLabel("CONFIGURAR")
        label_2.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)
        wid_derecha.layout().addWidget(label_2, 1)

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setStyleSheet(estilos.estilos_barritas_gucci())
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id())
                item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                item.setCheckState(0, Qt.Unchecked)
                self.tree_graficas.addTopLevelItem(item)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()
        wid_btn.setStyleSheet("QWidget{margin-left:5px;")

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QVBoxLayout())
        wid_btn.layout().setAlignment(Qt.AlignLeft)
        wid_btn.layout().addWidget(btn_aplicar_a_todas)

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        # GROUP BOX VALORES FILTRO
        wid_content_der = QtWidgets.QWidget()
        wid_content_der.setLayout(QtWidgets.QVBoxLayout())
        wid_content_der.layout().setAlignment(Qt.AlignTop)
        wid_content_der.layout().setContentsMargins(10, 0, 0, 0)
        wid_content_der.layout().setSpacing(15)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)

        # INICIO
        wid_label_desde = QtWidgets.QWidget()
        wid_label_desde.setLayout(QtWidgets.QHBoxLayout())

        wid_spiner_desde = QtWidgets.QWidget()
        wid_spiner_desde.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_desde.layout().setContentsMargins(0, 0, 0, 0)
        wid_spiner_desde.layout().setAlignment(Qt.AlignRight)

        label_desde = QtWidgets.QLabel("Inicio")
        label_desde.setFont(font)
        wid_label_desde.layout().addWidget(label_desde)

        self.spin_box = QtWidgets.QDoubleSpinBox()
        self.spin_box.setSingleStep(0.25)
        self.spin_box.setFixedWidth(60)
        self.spin_box.setValue(0.25)
        self.spin_box.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_label_desde.layout().addWidget(label_desde)
        wid_spiner_desde.layout().addWidget(self.spin_box)

        wid_desde = QtWidgets.QWidget()
        wid_desde.setLayout(QtWidgets.QHBoxLayout())
        wid_desde.layout().setContentsMargins(0, 0, 0, 0)
        wid_desde.layout().addWidget(wid_label_desde, 5)
        wid_desde.layout().addWidget(wid_spiner_desde, 5)

        # HASTA
        label_hasta = QtWidgets.QLabel("Fin")
        label_hasta.setFont(font)

        wid_label_hasta = QtWidgets.QWidget()
        wid_label_hasta.setLayout(QtWidgets.QHBoxLayout())
        wid_label_hasta.layout().addWidget(label_hasta)

        self.spin_box2 = QtWidgets.QDoubleSpinBox()
        self.spin_box2.setSingleStep(0.25)
        self.spin_box2.setFixedWidth(60)
        self.spin_box2.setValue(2)
        self.spin_box2.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_combobox_hasta = QtWidgets.QWidget()
        wid_combobox_hasta.setLayout(QtWidgets.QHBoxLayout())
        wid_combobox_hasta.layout().setContentsMargins(0, 0, 0, 0)
        wid_combobox_hasta.layout().setAlignment(Qt.AlignRight)
        wid_combobox_hasta.layout().addWidget(self.spin_box2)

        wid_hasta = QtWidgets.QWidget()
        wid_hasta.setLayout(QtWidgets.QHBoxLayout())
        wid_hasta.layout().setContentsMargins(0, 0, 0, 0)

        wid_hasta.layout().addWidget(wid_label_hasta, 5)
        wid_hasta.layout().addWidget(wid_combobox_hasta, 5)

        # valores absolutos
        label_hastaS = QtWidgets.QLabel("Valores absolutos")
        label_hastaS.setFont(font)

        wid_label_hastaS = QtWidgets.QWidget()
        wid_label_hastaS.setLayout(QtWidgets.QHBoxLayout())
        wid_label_hastaS.layout().addWidget(label_hastaS)

        self.qCheckBox = QtWidgets.QCheckBox()
        self.qCheckBox.setChecked(True)
        wid_combobox_hastaS = QtWidgets.QWidget()
        wid_combobox_hastaS.setLayout(QtWidgets.QHBoxLayout())
        wid_combobox_hastaS.layout().setContentsMargins(0, 0, 0, 0)
        wid_combobox_hastaS.layout().setAlignment(Qt.AlignRight)
        wid_combobox_hastaS.layout().addWidget(self.qCheckBox)

        wid_hastaS = QtWidgets.QWidget()
        wid_hastaS.setLayout(QtWidgets.QHBoxLayout())
        wid_hastaS.layout().setContentsMargins(0, 0, 0, 0)

        wid_hastaS.layout().addWidget(wid_label_hastaS, 5)
        wid_hastaS.layout().addWidget(wid_combobox_hastaS, 5)

        #   infooo
        label_info = QtWidgets.QLabel("<br>"
                                      "Se toman los valores de voltaje desde inicio hasta fin y se hace un promedio para poner la grafica lo mas cerca del 0 posible"
                                      "<br>"
                                      "Para dejar la grafica original se deben de poner los valores de inicio y fin en 0"
                                      "<br>")
        label_info.setFont(font)
        label_info.setWordWrap(True)

        # SE AGREGA CADA CONFIGURACIÓN EN ESTE ORDEN A LA VISTA
        wid_content_der.layout().addWidget(wid_desde)
        wid_content_der.layout().addWidget(wid_hasta)
        wid_content_der.layout().addWidget(wid_hastaS)
        wid_content_der.layout().addWidget(label_info)

        # BOTÓN APLICAR
        wid_btn_aplicar = QtWidgets.QWidget()
        wid_btn_aplicar.setLayout(QtWidgets.QHBoxLayout())
        wid_btn_aplicar.layout().setContentsMargins(0, 0, 0, 0)
        wid_btn_aplicar.layout().setAlignment(Qt.AlignRight)

        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.aplicar_cambios)
        btn_aplicar.setFixedWidth(80)
        btn_aplicar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn_aplicar.layout().addWidget(btn_aplicar)

        wid_derecha.layout().addWidget(wid_content_der, 8)
        wid_derecha.layout().addWidget(wid_btn_aplicar, 1)

        self.layout().addWidget(wid_izquierda, 5)
        self.layout().addWidget(wid_derecha, 5)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.showTime)

        self.msgBox = QMessageBox(self)
        self.msgBox.setText("Valores rectificados correctamente.")
        self.msgBox.setWindowTitle("ABS")
        self.msgBox.setStandardButtons(QMessageBox.Ok)

    def seleccionar_todas_las_graficas(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if not hijo.checkState(0):
                    hijo.setCheckState(0, Qt.Checked)

    def aplicar_cambios(self):
        hay_almenos_un_check = False
        desde = self.spin_box.value()
        hasta = self.spin_box2.value()
        abs = self.qCheckBox.isChecked()
        valores_en_cero = False
        seguir = True

        # *--------------------------------------------- CONTROLES --------------------------------------------------* #
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if hijo.checkState(0):
                    hay_almenos_un_check = True
                    break

        if hay_almenos_un_check and desde == 0 and hasta == 0:
            valores_en_cero = True

        if not hay_almenos_un_check:
            QMessageBox.information(self, "Advertencia",
                                    "Seleccione al menos una gráfica")
            seguir = False

        elif hay_almenos_un_check and hasta <= desde and not valores_en_cero:
            QMessageBox.warning(self, "Advertencia",
                                "El valor de inicio no puede ser mayor o igual al valor final.")
            seguir = False

        # *--------------------------------------------- FIN DE CONTROLES  ------------------------------------------* #

        if self.graficas is not None and seguir:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            grafica.set_offset([desde, hasta, abs])

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)
                self.hide()
                self.timer.start(1550)
                self.msgBox.exec_()
                self.close()

    def showTime(self):
        self.msgBox.close()

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux


class ventana_conf_vistas(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ventana_conf_vistas, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Configurar limite de gráficas")
        self.setFixedSize(290, 150)
        self.setStyleSheet("background-color:#FAFAFA;")
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(10)

        # PARAMETROS
        self.parent = parent

        wid_limite_vistas = QtWidgets.QWidget()
        wid_limite_vistas.setLayout(QtWidgets.QHBoxLayout())
        wid_limite_vistas.layout().setContentsMargins(0, 0, 0, 0)
        wid_limite_vistas.layout().setAlignment(Qt.AlignHCenter)
        wid_limite_vistas.layout().setSpacing(15)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)
        label_limite_vistas = QtWidgets.QLabel("Gráficas por vista:")
        label_limite_vistas.setFont(font)

        self.spinbox_limite_vistas = QtWidgets.QSpinBox()
        self.spinbox_limite_vistas.setFixedWidth(60)
        self.spinbox_limite_vistas.setValue(config.LIMITE_GRAFICAS_POR_VISTA)
        self.spinbox_limite_vistas.setStyleSheet(estilos.estilos_spinbox_filtros())

        wid_limite_vistas.layout().addWidget(label_limite_vistas)
        wid_limite_vistas.layout().addWidget(self.spinbox_limite_vistas)

        self.layout().addWidget(wid_limite_vistas)

        btn_aceptar = QtWidgets.QPushButton("Aplicar")
        btn_aceptar.clicked.connect(self.guardar_conf)
        btn_aceptar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        self.layout().addWidget(btn_aceptar)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.showTime)

        self.msgBox = QMessageBox(self)
        self.msgBox.setText("Configuración guardada.")
        self.msgBox.setWindowTitle("ABS")
        self.msgBox.setStandardButtons(QMessageBox.Ok)

    def guardar_conf(self):
        dato = self.spinbox_limite_vistas.value()
        dato_int = int(dato)

        config.LIMITE_GRAFICAS_POR_VISTA = dato_int
        Conexion.set_limite_graficas(dato_int)
        self.hide()
        self.timer.start(1550)
        self.msgBox.exec_()
        self.close()

    def showTime(self):
        self.msgBox.close()

class ventana_exportarVP(QtWidgets.QDialog):
    def __init__(self, parent=None, graficas=None):
        super(ventana_exportarVP, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Exportar datos")
        self.setFixedSize(420, 470)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10, 0, 10, 10)
        self.layout().setSpacing(10)

        # PARAMETROS
        self.parent = parent
        self.graficas = graficas

        wid_izquierda = QtWidgets.QWidget()
        wid_derecha = QtWidgets.QWidget()

        # SOMBRAS
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        wid_izquierda.setGraphicsEffect(shadow)

        # ESTILOS
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")

        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())

        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setStyleSheet(estilos.estilos_barritas_gucci())
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id())
                item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                item.setCheckState(0, Qt.Unchecked)
                self.tree_graficas.addTopLevelItem(item)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()
        wid_btn.setStyleSheet("QWidget{margin-left:5px;")

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QHBoxLayout())
        wid_btn.layout().addWidget(btn_aplicar_a_todas)

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        # BOTÓN APLICAR FILTROS
        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.exportar_valores_pico)
        btn_aplicar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn.layout().addWidget(btn_aplicar)

        self.layout().addWidget(wid_izquierda, 5)
        self.layout().addWidget(wid_derecha, 5)

    def seleccionar_todas_las_graficas(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if not hijo.checkState(0):
                    hijo.setCheckState(0, Qt.Checked)

    def exportar_valores_pico(self):
        graficas = []
        seguir = True
        hay_almenos_un_check = False

        # *--------------------------------------------- CONTROLES --------------------------------------------------* #
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if hijo.checkState(0):
                    hay_almenos_un_check = True
                    break

        if not hay_almenos_un_check:
            QMessageBox.information(self, "Advertencia",
                                    "Seleccione al menos una gráfica")
            seguir = False

        # *--------------------------------------------- FIN DE CONTROLES  ------------------------------------------* #

        if self.graficas is not None and seguir:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            graficas.append(grafica)

        if len(graficas) >= 1:
            self.parent.exportar_VP(graficas)
            self.close()

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux


class ventana_conf_archivos(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ventana_conf_archivos, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Configuraciones de archivos")
        self.setFixedSize(300, 150)
        self.setStyleSheet("background-color:#FAFAFA;")
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setSpacing(10)

        wid_content = QtWidgets.QWidget()
        wid_content.setLayout(QtWidgets.QVBoxLayout())
        wid_content.layout().setAlignment(Qt.AlignTop)

        wid_btn = QtWidgets.QWidget()
        wid_btn.setLayout(QtWidgets.QHBoxLayout())

        self.layout().addWidget(wid_content, 9)
        self.layout().addWidget(wid_btn, 1)

        # PARAMETROS
        self.parent = parent

        wid_row_columns = QtWidgets.QWidget()
        wid_row_columns.setLayout(QtWidgets.QHBoxLayout())
        wid_row_columns.layout().setContentsMargins(0, 0, 0, 0)
        wid_row_columns.layout().setAlignment(Qt.AlignHCenter)
        wid_row_columns.layout().setSpacing(15)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)
        label_limite_vistas = QtWidgets.QLabel("Nro. Linea de columnas:")
        label_limite_vistas.setFont(font)

        self.spinbox_row_column = QtWidgets.QSpinBox()
        self.spinbox_row_column.setFixedWidth(70)
        self.spinbox_row_column.setMinimum(1)
        self.spinbox_row_column.setMaximum(1000000)
        self.spinbox_row_column.setValue(config.ROW_COLUMNS + 1)
        self.spinbox_row_column.setStyleSheet(estilos.estilos_spinbox_filtros())

        wid_row_columns.layout().addWidget(label_limite_vistas)
        wid_row_columns.layout().addWidget(self.spinbox_row_column)

        wid_content.layout().addWidget(wid_row_columns)

        btn_aceptar = QtWidgets.QPushButton("Aplicar")
        btn_aceptar.clicked.connect(self.guardar_conf)
        btn_aceptar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn.layout().addWidget(btn_aceptar)

    def guardar_conf(self):
        dato = self.spinbox_row_column.value()
        dato_int = int(dato) - 1

        config.ROW_COLUMNS = dato_int
        Conexion.set_row_columns(dato_int)
        self.close()


class ventana_conf_linea_archivo(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ventana_conf_linea_archivo, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Configuraciones de columnas de información")
        self.setFixedSize(760, 500)
        self.setStyleSheet("background-color:#FAFAFA;")
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10, 0, 10, 10)
        self.layout().setSpacing(15)

        self.desde_confirmar = False
        # PARAMETROS
        self.parent = parent

        # SOMBRAS
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        shadow3 = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)

        # wid_filtro2.setGraphicsEffect(shadow2)

        # ESTILOS
        wid_izquierda = QtWidgets.QWidget(self)
        wid_izquierda.setGeometry(20, 10, 350, 470)
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")
        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())
        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        wid_izquierda.setGraphicsEffect(shadow)
        wid_izquierda.setGraphicsEffect(shadow)

        self.wid_derecha = QtWidgets.QWidget(self)
        self.wid_derecha.setGraphicsEffect(shadow2)
        self.wid_derecha.setGeometry(380, 10, 360, 470)
        self.wid_derecha.setLayout(QtWidgets.QVBoxLayout())
        self.wid_derecha.layout().setSpacing(20)
        self.wid_derecha.setStyleSheet("background-color:white; border-radius:4px;")
        self.wid_derecha.setGraphicsEffect(shadow2)

        self.wid_derecha2 = QtWidgets.QWidget(self)
        self.wid_derecha2.setGeometry(380, 500, 360, 470)
        self.wid_derecha2.setLayout(QtWidgets.QVBoxLayout())
        self.wid_derecha2.layout().setSpacing(10)
        self.wid_derecha2.setStyleSheet("background-color:white; border-radius:4px;")
        self.wid_derecha2.setGraphicsEffect(shadow3)

        label_1 = QtWidgets.QLabel("COLUMNAS DEL ARCHIVO")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        self.label_1_2 = QtWidgets.QLabel("")
        self.label_1_2.setStyleSheet("margin-top:14px;")

        wid_content_label_1 = QtWidgets.QWidget()
        wid_content_label_1.setLayout(QtWidgets.QHBoxLayout())
        wid_content_label_1.layout().setContentsMargins(0, 0, 0, 0)

        wid_label_1_2 = QtWidgets.QWidget()
        wid_label_1_2.setLayout(QtWidgets.QHBoxLayout())
        wid_label_1_2.layout().setAlignment(Qt.AlignRight)
        wid_label_1_2.layout().setContentsMargins(0, 0, 20, 0)
        wid_label_1_2.layout().addWidget(self.label_1_2)

        wid_label_1 = QtWidgets.QWidget()
        wid_label_1.setLayout(QtWidgets.QHBoxLayout())
        wid_label_1.layout().setAlignment(Qt.AlignLeft)
        wid_label_1.layout().setContentsMargins(0, 0, 0, 0)
        wid_label_1.layout().addWidget(label_1)

        wid_content_label_1.layout().addWidget(wid_label_1, 5)
        wid_content_label_1.layout().addWidget(wid_label_1_2, 5)

        wid_izquierda.layout().addWidget(wid_content_label_1, 1)

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setStyleSheet(estilos.estilos_barritas_gucci())
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        columnas = parent.archivito.get_archivo().columns
        self.label_1_2.setText("Total:" + str(int(len(columnas) / 2)))
        for x in range(1, len(columnas), 2):
            item = tree_widget_item_grafica(columnas[x])
            item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
            self.tree_graficas.addTopLevelItem(item)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        self.btn_seleccionar = QtWidgets.QPushButton("SELECCIONAR")
        self.btn_seleccionar.clicked.connect(self.seleccionar)
        self.btn_seleccionar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()
        wid_btn.setStyleSheet("QWidget{margin-left:5px;")

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QHBoxLayout())
        wid_btn.layout().setAlignment(Qt.AlignLeft)
        wid_btn.layout().addWidget(btn_aplicar_a_todas)
        wid_btn.layout().addWidget(self.btn_seleccionar)

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        # GROUP BOX VALORES FILTRO
        wid_content_filtrar = QtWidgets.QWidget()
        wid_content_filtrar.setLayout(QtWidgets.QVBoxLayout())
        wid_content_filtrar.layout().setAlignment(Qt.AlignTop)
        wid_content_filtrar.layout().setContentsMargins(10, 0, 0, 0)
        wid_content_filtrar.layout().setSpacing(20)

        label_2 = QtWidgets.QLabel("FILTRAR COLUMNAS")
        label_2.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;margin-bottom:16px;")
        wid_content_filtrar.layout().addWidget(label_2)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)

        # ORDER
        btn_filtrar_seleccionados = QtWidgets.QPushButton("FILTRAR SELECCIONADOS")
        btn_filtrar_seleccionados.clicked.connect(self.filtrar_seleccionados)
        btn_filtrar_seleccionados.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        btn_filtrar_no_seleccionados = QtWidgets.QPushButton("FILTRAR NO SELECCIONADOS")
        btn_filtrar_no_seleccionados.clicked.connect(self.filtrar_no_seleccionados)
        btn_filtrar_no_seleccionados.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_order = QtWidgets.QWidget()
        wid_order.setLayout(QtWidgets.QHBoxLayout())
        wid_order.layout().setContentsMargins(0, 0, 0, 0)
        wid_order.layout().addWidget(btn_filtrar_seleccionados)
        wid_order.layout().addWidget(btn_filtrar_no_seleccionados)

        # ARRAY LIKE
        wid_filtrar_content = QtWidgets.QWidget()
        wid_filtrar_content.setLayout(QtWidgets.QVBoxLayout())
        wid_filtrar_content.layout().setContentsMargins(0, 0, 0, 0)
        wid_filtrar_content.layout().setSpacing(0)

        label_filtrar_por_caracter = QtWidgets.QLabel("Filtrar por caracteres:")
        label_filtrar_por_caracter.setFont(font)

        wid_label_filtrar_caracter = QtWidgets.QWidget()
        wid_label_filtrar_caracter.setLayout(QtWidgets.QHBoxLayout())
        wid_label_filtrar_caracter.layout().addWidget(label_filtrar_por_caracter)

        self.textbox = QtWidgets.QLineEdit()
        self.textbox.setStyleSheet(estilos.textbox())

        wid_textbox = QtWidgets.QWidget()
        wid_textbox.setLayout(QtWidgets.QHBoxLayout())
        wid_textbox.layout().setContentsMargins(8, 2, 0, 2)
        wid_textbox.layout().setAlignment(Qt.AlignRight)
        wid_textbox.layout().addWidget(self.textbox)

        wid_textbox_label = QtWidgets.QWidget()
        wid_textbox_label.setLayout(QtWidgets.QHBoxLayout())
        wid_textbox_label.layout().setContentsMargins(0, 0, 0, 0)

        wid_textbox_label.layout().addWidget(wid_label_filtrar_caracter, 4)
        wid_textbox_label.layout().addWidget(wid_textbox, 6)

        wid_filtrar_content.layout().addWidget(wid_textbox_label)

        wid_checkbox = QtWidgets.QWidget()
        wid_checkbox.setLayout(QtWidgets.QHBoxLayout())
        wid_checkbox.layout().setAlignment(Qt.AlignRight)
        wid_checkbox.layout().setSpacing(0)

        label_palabra = QtWidgets.QLabel("Eliminar coincidencias")
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setCheckState(Qt.Checked)

        wid_checkbox.layout().addWidget(self.checkbox)
        wid_checkbox.layout().addWidget(label_palabra)
        wid_filtrar_content.layout().addWidget(wid_checkbox)

        wid_btn_2 = QtWidgets.QWidget()
        wid_btn_2.setLayout(QtWidgets.QHBoxLayout())
        wid_btn_2.layout().setContentsMargins(0, 10, 0, 0)
        wid_btn_2.layout().setAlignment(Qt.AlignRight)

        btn = QtWidgets.QPushButton("FILTRAR")
        btn.clicked.connect(self.filtrar_por_caracteres)
        btn.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn_2.layout().addWidget(btn)
        wid_filtrar_content.layout().addWidget(wid_btn_2)

        # SE AGREGA CADA CONFIGURACIÓN EN ESTE ORDEN A LA VISTA
        wid_content_filtrar.layout().addWidget(wid_order)
        wid_content_filtrar.layout().addWidget(wid_filtrar_content)

        # BOTÓN APLICAR FILTROS
        wid_btn_siguiente = QtWidgets.QWidget()
        wid_btn_siguiente.setLayout(QtWidgets.QHBoxLayout())
        wid_btn_siguiente.layout().setContentsMargins(0, 0, 0, 0)
        wid_btn_siguiente.layout().setAlignment(Qt.AlignRight)

        btn_siguiente = QtWidgets.QPushButton("SIGUIENTE")
        btn_siguiente.clicked.connect(self.siguiente)
        btn_siguiente.setFixedWidth(80)
        btn_siguiente.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn_siguiente.layout().addWidget(btn_siguiente)

        self.wid_derecha.layout().addWidget(wid_content_filtrar, 9)
        self.wid_derecha.layout().addWidget(wid_btn_siguiente, 1)

        # PANEL DE CREAR DIRECTORES
        label_3 = QtWidgets.QLabel("DIRECTORIOS")
        label_3.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;margin-bottom:16px;")
        self.wid_derecha2.layout().addWidget(label_3, 1)

        wid_content_archivos = QtWidgets.QWidget()
        wid_content_archivos.setLayout(QtWidgets.QVBoxLayout())
        wid_content_archivos.layout().setAlignment(Qt.AlignTop)
        wid_content_archivos.layout().setContentsMargins(10, 0, 0, 0)
        wid_content_archivos.layout().setSpacing(4)

        self.wid_derecha2.layout().addWidget(wid_content_archivos, 8)

        self.tree_widget_directorios = QtWidgets.QTreeWidget()
        self.tree_widget_directorios.setStyleSheet(estilos.estilos_tree_widget_importar_directorios())
        self.tree_widget_directorios.setFixedHeight(250)
        self.tree_widget_directorios.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget_directorios.customContextMenuRequested.connect(self.handle_rightClicked)
        self.tree_widget_directorios.setHeaderHidden(True)

        wid_content_archivos.layout().addWidget(self.tree_widget_directorios)

        wid_btn_crear_dir = QtWidgets.QWidget()
        wid_btn_crear_dir.setLayout(QtWidgets.QHBoxLayout())
        wid_btn_crear_dir.setFixedHeight(30)
        wid_btn_crear_dir.layout().setContentsMargins(0, 0, 0, 0)
        wid_btn_crear_dir.layout().setAlignment(Qt.AlignLeft)

        btn_crear_dir = QtWidgets.QPushButton("NUEVO DIRECTORIO")
        btn_crear_dir.clicked.connect(self.crear_directorio)
        btn_crear_dir.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn_crear_dir.layout().addWidget(btn_crear_dir)
        wid_content_archivos.layout().addWidget(wid_btn_crear_dir)

        wid_botones = QtWidgets.QWidget()
        wid_botones.setLayout(QtWidgets.QHBoxLayout())
        wid_botones.layout().setContentsMargins(0, 0, 0, 0)
        wid_botones.layout().setAlignment(Qt.AlignRight)

        btn_confirmar = QtWidgets.QPushButton("CONFIRMAR")
        btn_confirmar.clicked.connect(self.confirmar)
        btn_confirmar.setFixedWidth(80)
        btn_confirmar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        btn_volver = QtWidgets.QPushButton("VOLVER")
        btn_volver.clicked.connect(self.volver)
        btn_volver.setFixedWidth(80)
        btn_volver.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_botones.layout().addWidget(btn_volver)
        wid_botones.layout().addWidget(btn_confirmar)

        self.wid_derecha2.layout().addWidget(wid_botones, 1)

    def seleccionar_todas_las_graficas(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if not hijo.checkState(0):
                    hijo.setCheckState(0, Qt.Checked)

        self.btn_seleccionar.setText("CANCELAR")

    def seleccionar(self):
        if self.btn_seleccionar.text() == "SELECCIONAR":
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if not hijo.checkState(0):
                        hijo.setCheckState(0, Qt.Unchecked)
            self.btn_seleccionar.setText("CANCELAR")

        else:
            for i in range(self.tree_graficas.topLevelItemCount()):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    hijo.setData(0, Qt.CheckStateRole, None)
            self.btn_seleccionar.setText("SELECCIONAR")

    def filtrar_no_seleccionados(self):
        cantidad_seleccionados = 0
        cant_hijos_tree = 0

        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                cant_hijos_tree += 1
                if not hijo.checkState(0):
                    cantidad_seleccionados += 1

        if cantidad_seleccionados == cant_hijos_tree:
            for i in range(self.tree_graficas.topLevelItemCount()):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    hijo.setData(0, Qt.CheckStateRole, None)
            QtWidgets.QMessageBox.about(self, "Error",
                                        "No es posible eliminar todas las columnas, debe haber al menos 1.")
            return

        while True:
            hay = False
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if not hijo.checkState(0):
                        hay = True
                        self.tree_graficas.invisibleRootItem().removeChild(hijo)

            if not hay:
                break
            elif hay:
                hay = False
        cant = 0
        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                hijo.setData(0, Qt.CheckStateRole, None)
                cant += 1
                hijo.setData(0, Qt.CheckStateRole, None)
        self.label_1_2.setText("Total: " + str(cant))

    def filtrar_seleccionados(self):
        cantidad_seleccionados = 0
        cant_hijos_tree = 0

        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                cant_hijos_tree += 1
                if hijo.checkState(0):
                    cantidad_seleccionados += 1

        if cantidad_seleccionados == cant_hijos_tree:
            for i in range(self.tree_graficas.topLevelItemCount()):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    hijo.setData(0, Qt.CheckStateRole, None)
            QtWidgets.QMessageBox.about(self, "Error",
                                        "No es posible eliminar todas las columnas, debe haber al menos 1.")
            return

        while True:
            hay = False
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        hay = True
                        self.tree_graficas.invisibleRootItem().removeChild(hijo)

            if not hay:
                break
            elif hay:
                hay = False
        cant = 0
        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                hijo.setData(0, Qt.CheckStateRole, None)
                cant += 1
                hijo.setData(0, Qt.CheckStateRole, None)
        self.label_1_2.setText("Total: " + str(cant))

    def filtrar_por_caracteres(self):
        if len(self.textbox.text()) == 0:
            return

        cantidad_coincidencias = 0
        cant_hijos_tree = 0

        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                cant_hijos_tree += 1
                if hijo.text(0).find(self.textbox.text()) > -1 and self.checkbox.isChecked():
                    cantidad_coincidencias += 1
                elif hijo.text(0).find(self.textbox.text()) == -1 and not self.checkbox.isChecked():
                    cantidad_coincidencias += 1

        if cantidad_coincidencias == cant_hijos_tree:
            QtWidgets.QMessageBox.about(self, "Error",
                                        "No es posible eliminar todas las columnas, debe haber al menos 1.")
            return

        while True:
            hay = False
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.text(0).find(self.textbox.text()) > -1 and self.checkbox.isChecked():
                        hay = True
                        self.tree_graficas.invisibleRootItem().removeChild(hijo)
                    elif hijo.text(0).find(self.textbox.text()) == -1 and not self.checkbox.isChecked():
                        hay = True
                        self.tree_graficas.invisibleRootItem().removeChild(hijo)

            if not hay:
                break
            elif hay:
                hay = False

    def aplicar_valores_filtro(self):
        hay_almenos_un_check = False
        order = self.spin_box.value()
        array_a = int(self.spiner_array_a.value()) * 0.001
        array_b = int(self.spiner_array_b.value()) * 0.001
        btype = self.combobox_btype.currentText()
        analog = None
        if self.combobox_analog.currentText() == "True":
            analog = True
        else:
            analog = False

        cant = 0
        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                cant += 1

        self.label_1_2.setText("Total: " + str(cant))

    def siguiente(self):
        self.anim = QtCore.QPropertyAnimation(self.wid_derecha, b"pos")
        self.anim.setEndValue(QtCore.QPoint(380, -500))
        self.anim.setDuration(400)

        self.anim2 = QtCore.QPropertyAnimation(self.wid_derecha2, b"pos")
        self.anim2.setEndValue(QtCore.QPoint(380, 10))
        self.anim2.setDuration(400)

        self.anim.start()
        self.anim2.start()

    def volver(self):
        self.anim = QtCore.QPropertyAnimation(self.wid_derecha, b"pos")
        self.anim.setEndValue(QtCore.QPoint(380, 10))
        self.anim.setDuration(400)

        self.anim2 = QtCore.QPropertyAnimation(self.wid_derecha2, b"pos")
        self.anim2.setEndValue(QtCore.QPoint(380, 500))
        self.anim2.setDuration(400)

        self.anim.start()
        self.anim2.start()

    def confirmar(self):
        self.parent.archivito.agregar_electromiografias2(self.tree_widget_directorios)
        self.parent.seguir_proceso = True
        self.close()

    def crear_directorio(self):
        ventana_directorio(self, crear_directorio=True).exec_()

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux

    def importar_seleccionadas(self, padre: QtWidgets.QTreeWidgetItem):
        # tree_widget_directorios
        cant_seleccionados = 0
        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if hijo.checkState(0) and not self.existe_item_in_tree_dir(padre, hijo.text(0)):
                    cant_seleccionados += 1
                    item = QtWidgets.QTreeWidgetItem([hijo.text(0)])
                    item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                    padre.addChild(item)

        self.tree_widget_directorios.expandItem(padre)

        if cant_seleccionados > 0:
            self.quitar_checks_tree_columnas()

    def importar_rango(self, padre: QtWidgets.QTreeWidgetItem):
        primer_check = False
        cant_seleccionados = 0

        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if hijo.checkState(0):
                    cant_seleccionados += 1

        if cant_seleccionados > 2:
            QtWidgets.QMessageBox.about(self, "Error",
                                        "Para importar un rango de columnas solo debe haber \n2 columnas seleccionadas.")
            return
        elif cant_seleccionados < 2:
            QtWidgets.QMessageBox.about(self, "Error",
                                        "Para importar un rango de columnas debe haber \n2 columnas seleccionadas.")
            return

        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if hijo.checkState(0) and not primer_check:
                    primer_check = True
                    if not self.existe_item_in_tree_dir(padre, hijo.text(0)):
                        item = QtWidgets.QTreeWidgetItem([hijo.text(0)])
                        item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                        padre.addChild(item)
                elif not hijo.checkState(0) and primer_check and not self.existe_item_in_tree_dir(padre, hijo.text(0)):
                    item = QtWidgets.QTreeWidgetItem([hijo.text(0)])
                    item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                    padre.addChild(item)
                elif hijo.checkState(0) and primer_check:
                    if not self.existe_item_in_tree_dir(padre, hijo.text(0)):
                        item = QtWidgets.QTreeWidgetItem([hijo.text(0)])
                        item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                        padre.addChild(item)
                    break

        self.tree_widget_directorios.expandItem(padre)
        self.quitar_checks_tree_columnas()

    def eliminar_columnas(self, padre: QtWidgets.QTreeWidgetItem):
        padre.takeChildren()

    def eliminar_directorio(self, padre: QtWidgets.QTreeWidgetItem):
        self.tree_widget_directorios.takeTopLevelItem(self.tree_widget_directorios.indexOfTopLevelItem(padre))

    def cambiar_nombre_dir(self, padre):
        ventana_directorio(self, cambiar_nombre=True, dir=padre).exec_()

    def eliminar_columna(self, columna: QtWidgets.QTreeWidgetItem):
        padre = columna.parent()
        padre.takeChild(padre.indexOfChild(columna))

    def existe_item_in_tree_dir(self, padre: QtWidgets.QTreeWidgetItem, nombre):
        existe = False
        for index in range(padre.childCount()):
            hijo = padre.child(index)
            if hijo.text(0) == nombre:
                existe = True
                break

        return existe

    def quitar_checks_tree_columnas(self):
        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                hijo.setCheckState(0, Qt.Unchecked)

    def handle_rightClicked(self, pos):
        item = self.tree_widget_directorios.itemAt(pos)
        if item is None:
            return
        menu = QtWidgets.QMenu()
        if item.parent() is not None:
            eliminar_columna = QtWidgets.QAction("Eliminar")
            eliminar_columna.triggered.connect(lambda checked, item=item: self.eliminar_columna(item))
            menu.addAction(eliminar_columna)

        elif item.parent() is None:
            importar_seleccionadas = QtWidgets.QAction("Importar columnas seleccionadas")
            importar_seleccionadas.triggered.connect(lambda checked, item=item: self.importar_seleccionadas(item))

            importar_entre_dos_puntos = QtWidgets.QAction("Importar rango de columnas")
            importar_entre_dos_puntos.triggered.connect(lambda checked, item=item: self.importar_rango(item))

            eliminar_col = QtWidgets.QAction("Eliminar columnas")
            eliminar_col.triggered.connect(lambda checked, item=item: self.eliminar_columnas(item))

            eliminar_dir = QtWidgets.QAction("Eliminar directorio")
            eliminar_dir.triggered.connect(lambda checked, item=item: self.eliminar_directorio(item))

            cambiar_nombre = QtWidgets.QAction("Cambiar nombre")
            cambiar_nombre.triggered.connect(lambda checked, item=item: self.cambiar_nombre_dir(item))

            menu.addAction(importar_seleccionadas)
            menu.addAction(importar_entre_dos_puntos)
            menu.addAction(eliminar_col)
            menu.addAction(eliminar_dir)
            menu.addAction(cambiar_nombre)

        menu.exec_(self.tree_widget_directorios.viewport().mapToGlobal(pos))


class ventana_directorio(QtWidgets.QDialog):
    def __init__(self, parent=None, crear_directorio=False, cambiar_nombre=False, dir=None):
        super(ventana_directorio, self).__init__()

        # PARAMETROS
        self.parent = parent
        self.dir = dir
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        if cambiar_nombre:
            self.setWindowTitle("Cambiar nombre")
        elif crear_directorio:
            self.setWindowTitle("Nombre directorio")
        self.setFixedSize(300, 120)
        self.setStyleSheet("background-color:#FAFAFA;")
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(12, 12, 20, 0)
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setSpacing(12)

        label = QtWidgets.QLabel("Nombre directorio:")
        label.setStyleSheet("font-size:12px;")

        self.textbox_nombre = QtWidgets.QLineEdit()
        self.textbox_nombre.setStyleSheet(estilos.textbox())

        wid_botones = QtWidgets.QWidget()
        wid_botones.setStyleSheet("margin-top:4px;")
        wid_botones.setLayout(QtWidgets.QHBoxLayout())
        wid_botones.layout().setContentsMargins(0, 0, 0, 0)
        wid_botones.layout().setAlignment(Qt.AlignRight)

        btn_confirmar = QtWidgets.QPushButton("CONFIRMAR")

        if cambiar_nombre:
            btn_confirmar.clicked.connect(self.cambiar_nombre)
        elif crear_directorio:
            btn_confirmar.clicked.connect(self.crear_directorio)

        btn_confirmar.setFixedWidth(80)
        btn_confirmar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())
        wid_botones.layout().addWidget(btn_confirmar)

        self.layout().addWidget(label)
        self.layout().addWidget(self.textbox_nombre)
        self.layout().addWidget(wid_botones)

    def crear_directorio(self):
        nombre = self.textbox_nombre.text()
        if self.verificar_si_existe(nombre):
            QtWidgets.QMessageBox.about(self, "Error",
                                        "El nombre que ingresó ya existe.")
            return
        item = QtWidgets.QTreeWidgetItem([nombre])
        item.setIcon(0, QtGui.QIcon(config.ICONO_CARPETAS))
        self.parent.tree_widget_directorios.addTopLevelItem(item)
        self.close()

    def cambiar_nombre(self):
        nombre = self.textbox_nombre.text()
        if self.verificar_si_existe(nombre):
            QtWidgets.QMessageBox.about(self, "Error",
                                        "El nombre que ingresó ya existe.")
            return
        self.dir.setText(0, nombre)
        self.close()

    def verificar_si_existe(self, nombre):
        existe = False
        for i in range(self.parent.tree_widget_directorios.topLevelItemCount()):
            hijo = self.parent.tree_widget_directorios.topLevelItem(i)
            if isinstance(hijo, QtWidgets.QTreeWidgetItem):
                if hijo.text(0) == nombre:
                    existe = True
                    break
        return existe


class ventana_valoresEnBruto(QtWidgets.QDialog):
    def __init__(self, parent=None, graficas=None, v=""):
        super(ventana_valoresEnBruto, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Valores en bruto - " + v)
        self.setFixedSize(770 / 2, 470)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10, 0, 10, 10)
        self.layout().setSpacing(15)

        # PARAMETROS
        self.parent = parent
        self.graficas = graficas

        wid_izquierda = QtWidgets.QWidget()

        # SOMBRAS
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        wid_izquierda.setGraphicsEffect(shadow)

        # ESTILOS
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")
        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())
        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        label_2 = QtWidgets.QLabel("CONFIGURAR RECORTE")
        label_2.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setStyleSheet(estilos.estilos_barritas_gucci())
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id())
                item.setIcon(0, QtGui.QIcon(config.ICONO_GRAFICAS))
                item.setCheckState(0, Qt.Unchecked)
                self.tree_graficas.addTopLevelItem(item)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.aplicar_valoresEnBruto)
        btn_aplicar.setFixedWidth(80)
        btn_aplicar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()

        wid_btn.setStyleSheet("QWidget{margin-left:5px;")

        # wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QHBoxLayout())
        wid_btn.layout().setAlignment(Qt.AlignLeft)

        wid_btn.layout().addWidget(btn_aplicar_a_todas)
        wid_btn.layout().addWidget(btn_aplicar)

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)

        self.layout().addWidget(wid_izquierda)


        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.showTime)

        self.msgBox = QMessageBox(self)
        self.msgBox.setText("Valores brutos aplicados correctamente.")
        self.msgBox.setWindowTitle("ABS")
        self.msgBox.setStandardButtons(QMessageBox.Ok)

    def showTime(self):
        self.msgBox.close()

    def seleccionar_todas_las_graficas(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if not hijo.checkState(0):
                    hijo.setCheckState(0, Qt.Checked)

    def aplicar_valoresEnBruto(self):
        hay_almenos_un_check = False
        seguir = True

        # *------------------------------------CONTROLES-------------------------------------------
        # Tengo que hacer este for rancio al menos una vez para chequear si hay algún check de las graficas chequeados.
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if hijo.checkState(0):
                    hay_almenos_un_check = True
                    break

        if hay_almenos_un_check:
            valores_en_cero = True

        if not hay_almenos_un_check:
            QMessageBox.information(self, "Advertencia",
                                    "Seleccione al menos una gráfica")
            seguir = False

        # *------------------------------------FIN DE CONTROLES------------------------------------

        if self.graficas is not None and seguir:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            grafica.aplicarValoresBrutos()

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)
                self.hide()
                self.timer.start(1550)
                self.msgBox.exec_()
                self.close()

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux
