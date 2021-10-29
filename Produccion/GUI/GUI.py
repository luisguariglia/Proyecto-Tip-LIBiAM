from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QMessageBox, QGroupBox
from PyQt5.QtCore import QVariant, QUrl, QDir
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from matplotlib import pyplot as plt
import config
import os
from BD.Queries import Conexion
from Static.styles import estilos
from Modelo.Grafica import Grafica
from Modelo.Filtro import Filtro
from Modelo.Filtro_FFT import Filtro_FFT
from Modelo.Pico import Pico
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

        label_checkbox = QtWidgets.QLabel("Aplicar Filtro en la grafica")
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
        self.msgBox.setWindowTitle("Filtrado")
        self.msgBox.setStandardButtons(QMessageBox.Ok)

        self.msgBox2 = QMessageBox(self)
        self.msgBox2.setText("Error al aplicar filtro, puede que algun parametro este mal.")
        self.msgBox2.setWindowTitle("Error")
        self.msgBox2.setStandardButtons(QMessageBox.Ok)

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
        errorEnFiltro = False
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
                                errorEnFiltro = grafica.chequearErrorEnFiltro()
                            if mostrarFFT:
                                grafica.set_fastfouriertransform(Filtro_FFT(n, norm))

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)
                self.hide()
                self.timer.start(1550)
                if not errorEnFiltro:
                    self.msgBox.exec_()
                    self.close()
                else:
                    self.msgBox2.exec_()


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

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setStyleSheet(estilos.estilos_barritas_gucci())
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        # -------------------------------------------------------------------------------INTEGRAL-----------------------------------------------------------------
        btn_RecortarConClicks = QtWidgets.QPushButton("Indicar Haciendo Click")
        btn_RecortarConClicks.clicked.connect(self.RecortarIntegralHaciendoClick)
        btn_RecortarConClicks.setFixedWidth(140)
        btn_RecortarConClicks.setStyleSheet(estilos.estilos_btn_exportar())

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
        widget_integral.layout().addWidget(btn_RecortarConClicks)
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
        btn_RecortarConClicksRms = QtWidgets.QPushButton("Indicar Haciendo Click")
        btn_RecortarConClicksRms.clicked.connect(self.RecortarRMSHaciendoClick)
        btn_RecortarConClicksRms.setFixedWidth(140)
        btn_RecortarConClicksRms.setStyleSheet(estilos.estilos_btn_exportar())

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
        widget_valor_rms.layout().addWidget(btn_RecortarConClicksRms)

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

    def RecortarIntegralHaciendoClick(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        if cant_hijos == 1:
            self.hide()
            QMessageBox.information(self, "Información",
                                    "Por favor haga 2 clicks en el gráfico que desea realizar la integral \n"
                                    "Indicando el valor inicial y valor final")
            self.parent.setIndicandoIntegral("integral", False, self)
        else:
            self.hide()
            QMessageBox.information(self, "Información", "Por favor haga 2 clicks en el gráfico que desea realizar la integral \n"
                                                  "Indicando el valor inicial y valor final")
            self.parent.setIndicandoIntegral("integral", True, self)
    def RecortarRMSHaciendoClick(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        if cant_hijos == 1:
            self.hide()
            QMessageBox.information(self, "Información",
                                    "Por favor haga 2 clicks en el gráfico que desea realizar el calculo de RMS \n"
                                    "Indicando el valor inicial y valor final")
            self.parent.setIndicandoRMS("rms", False, self)
        else:
            self.hide()
            QMessageBox.information(self, "Información", "Por favor haga 2 clicks en el gráfico que desea realizar el calculo de RMS \n"
                                                  "Indicando el valor inicial y valor final")
            self.parent.setIndicandoRMS("rms", True, self)
    def seleccionar_grafica(self, num):
        cant_hijos = self.tree_graficas.topLevelItemCount()

        cont = 0
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if cont == num:
                    if not hijo.checkState(0):
                        hijo.setCheckState(0, Qt.Checked)
            cont = cont + 1
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

        if self.graficas is not None and seguir:
            return True
        else:
            self.parent.listar_graficas(True)
            return False
            
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

    def setRecorte(self, min, max):
        self.spinbox_inicio.setValue(min)
        self.spinbox_fin.setValue(max)
        self.checkbox_mostrar_integral.setChecked(True)

    def setRecorteRMS(self, min, max):
        self.spinbox_inicioRMS.setValue(min)
        self.spinbox_finRMS.setValue(max)
        self.checkbox_mostrar_RMS.setChecked(True)


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
        #wid_content_der.layout().addWidget(btn_RecortarConClicks)
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

        botones_layout = QtWidgets.QWidget()
        botones_layout.setLayout(QtWidgets.QHBoxLayout())

        botones_layout.layout().addWidget(btn_RecortarConClicks)
        botones_layout.layout().addWidget(wid_btn_aplicar)
        wid_derecha.layout().addWidget(botones_layout, 1)

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
            QMessageBox.information(self, "Información",
                                    "Por favor haga 2 clicks en el gráfico que desea recortar \n"
                                    "Indicando el valor inicial y valor final")
            self.parent.setCortandoGrafico("True", False, self)
        else:
            self.hide()
            QMessageBox.information(self, "Información",
                                    "Por favor haga 2 clicks en el gráfico que desea recortar \n"
                                    "Indicando el valor inicial y valor final")
            self.parent.setCortandoGrafico("True", True, self)

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
    def seleccionar_grafica(self,num):
        cant_hijos = self.tree_graficas.topLevelItemCount()

        cont = 0
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if cont == num:
                    if not hijo.checkState(0):
                        hijo.setCheckState(0, Qt.Checked)
            cont = cont + 1
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

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QVBoxLayout())
        wid_btn.layout().setAlignment(Qt.AlignLeft)
        wid_btn.layout().addWidget(btn_aplicar_a_todas)

        #btn_rectificar_todas_las_graficas = QtWidgets.QPushButton("RECTIFICAR TODA LA GRÁFICA")
        #btn_rectificar_todas_las_graficas.clicked.connect(self.rectificar_todas_las_graficas)
        #btn_rectificar_todas_las_graficas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())
        #wid_btn.layout().addWidget(btn_rectificar_todas_las_graficas)

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
                                      "Se toman los valores de voltaje desde inicio hasta fin y se hace un promedio para poner toda la grafica lo mas cerca del 0 posible"
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

        btn_aplicar = QtWidgets.QPushButton("RECTIFICAR TODA LA GRÁFICA")
        btn_aplicar.clicked.connect(self.aplicar_cambios)
        btn_aplicar.setFixedWidth(180)
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

    def rectificar_todas_las_graficas(self):
        abs = self.qCheckBox.isChecked()
        cant_hijos = self.tree_graficas.topLevelItemCount()
        hay_almenos_un_check = False
        seguir = True

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

        if hay_almenos_un_check and seguir:
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            tiempo = grafica.getLimitesTiempo()
                            desde = tiempo[0]
                            hasta = tiempo[1]
                            grafica.set_offset([desde, hasta, abs])

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)
                self.hide()
                self.timer.start(1550)
                self.msgBox.exec_()
                self.close()

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

        #PARAMETROS
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

        # ESTILOSjgkkjg
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

        # LISTA
        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)
        label_btype = QtWidgets.QLabel("Formatos para exportar: ")
        label_btype.setStyleSheet("padding:0px;margin:0px;")
        label_btype.setFont(font)

        self.combobox_btype = QtWidgets.QComboBox()
        self.combobox_btype.setFixedWidth(150)
        self.combobox_btype.addItem(".CSV")
        self.combobox_btype.addItem(".XLS")
        self.combobox_btype.setCurrentIndex(1)
        self.combobox_btype.setStyleSheet(estilos.estilos_combobox_filtro())

        wid_combobox_btype = QtWidgets.QWidget()
        wid_combobox_btype.setLayout(QtWidgets.QHBoxLayout())
        wid_combobox_btype.layout().setContentsMargins(0, 0, 0, 0)
        wid_combobox_btype.layout().setAlignment(Qt.AlignRight)
        wid_combobox_btype.layout().addWidget(self.combobox_btype)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QHBoxLayout())

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(label_btype)
        wid_izquierda.layout().addWidget(wid_combobox_btype)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        # BOTÓN APLICAR FILTROS
        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.exportar_valores_pico)
        btn_aplicar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn.layout().addWidget(btn_aplicar_a_todas)
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
        btype = self.combobox_btype.currentText()

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
            self.parent.exportar_VP(graficas, btype)
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
        label_limite_vistas = QtWidgets.QLabel("Nro. fila de columnas:")
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


class ventana_verayuda_antes_columnas(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ventana_verayuda_antes_columnas, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Ayuda - Abrir archivo csv")
        self.setFixedSize(900, 600)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.setStyleSheet("background-color:white;")
        self.layout().setContentsMargins(8,8,0,0)
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=10, xOffset=1, yOffset=1)

        layout_scroll = QtWidgets.QVBoxLayout()
        layout_scroll.setAlignment(Qt.AlignTop)
        layout_scroll.setContentsMargins(4, 4, 4, 4)
        layout_scroll.setSpacing(16)

        widget_scroll = QtWidgets.QWidget()
        widget_scroll.setLayout(layout_scroll)

        #SCROLL AREA
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setStyleSheet(estilos.estilos_sroll_area())
        #scroll_area.setGraphicsEffect(shadow)


        widget_paso_1 = QtWidgets.QWidget()
        widget_paso_1.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_1.layout().setAlignment(Qt.AlignTop)
        widget_paso_1.layout().setSpacing(8)

        label_paso_1_titulo = QtWidgets.QLabel("Paso 1:")
        label_paso_1_titulo.setStyleSheet("font: bold 13px;")

        label_paso_1_instruccion = QtWidgets.QLabel(
            "Abrir el archivo csv que desea importar al software con un programa de hoja de cálculo, por ejemplo Excel.")
        label_paso_1_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_1 = QtGui.QPixmap(':/Static/img/paso1.png')
        lab1 = QtWidgets.QLabel()
        lab1.setPixmap(img_paso_1)

        widget_paso_1.layout().addWidget(label_paso_1_titulo)
        widget_paso_1.layout().addWidget(label_paso_1_instruccion)
        widget_paso_1.layout().addWidget(lab1)

        #PASO 2
        widget_paso_2 = QtWidgets.QWidget()
        widget_paso_2.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_2.layout().setAlignment(Qt.AlignTop)
        widget_paso_2.layout().setSpacing(8)

        label_paso_2_titulo = QtWidgets.QLabel("Paso 2:")
        label_paso_2_titulo.setStyleSheet("font: bold 13px;")

        label_paso_2_instruccion = QtWidgets.QLabel(
            "Identificar el número de la fila donde se encuentran las columnas con la información obtenida por los sensores. En este ejemplo como se\npuede apreciar en la siguiente imagen las columnas se encuentran en la fila 789.")
        label_paso_2_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_2 = QtGui.QPixmap(':/Static/img/paso2.png')
        lab2 = QtWidgets.QLabel()
        lab2.setPixmap(img_paso_2)

        widget_paso_2.layout().addWidget(label_paso_2_titulo)
        widget_paso_2.layout().addWidget(label_paso_2_instruccion)
        widget_paso_2.layout().addWidget(lab2)

        #PASO 3
        widget_paso_3 = QtWidgets.QWidget()
        widget_paso_3.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_3.layout().setAlignment(Qt.AlignTop)
        widget_paso_3.layout().setSpacing(8)

        label_paso_3_titulo = QtWidgets.QLabel("Paso 3:")
        label_paso_3_titulo.setStyleSheet("font: bold 13px;")

        label_paso_3_instruccion = QtWidgets.QLabel(
            'Hacer click en el menú "Configuración" que se encuentra en la esquina superior izquiera y seleccionar la opción "Archivos".')
        label_paso_3_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_3 = QtGui.QPixmap(':/Static/img/paso3.png')
        lab3 = QtWidgets.QLabel()
        lab3.setPixmap(img_paso_3)

        widget_paso_3.layout().addWidget(label_paso_3_titulo)
        widget_paso_3.layout().addWidget(label_paso_3_instruccion)
        widget_paso_3.layout().addWidget(lab3)

        #PASO 4
        widget_paso_4 = QtWidgets.QWidget()
        widget_paso_4.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_4.layout().setAlignment(Qt.AlignTop)
        widget_paso_4.layout().setSpacing(8)

        label_paso_4_titulo = QtWidgets.QLabel("Paso 4:")
        label_paso_4_titulo.setStyleSheet("font: bold 13px;")

        label_paso_4_instruccion = QtWidgets.QLabel(
            'Al finalizar el Paso 3 se abrirá a continuación una ventana que contiene el campo "Nro. fila de columnas" con un número configurado\npor defecto, este indica al software en que fila comienzan las columnas con la información dentros de los archivos csv. En este ejemplo\nlas columnas se ubican en la fila número 789 (Paso 2), por lo tanto ingresamos este número en el campo y hacemos click en el botón\n"Aplicar".')
        label_paso_4_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_4 = QtGui.QPixmap(':/Static/img/paso4.png')
        lab4 = QtWidgets.QLabel()
        lab4.setPixmap(img_paso_4)

        widget_paso_4.layout().addWidget(label_paso_4_titulo)
        widget_paso_4.layout().addWidget(label_paso_4_instruccion)
        widget_paso_4.layout().addWidget(lab4)

        #PASO 5
        widget_paso_5 = QtWidgets.QWidget()
        widget_paso_5.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_5.layout().setAlignment(Qt.AlignTop)
        widget_paso_5.layout().setSpacing(8)

        label_paso_5_titulo = QtWidgets.QLabel("Paso 5:")
        label_paso_5_titulo.setStyleSheet("font: bold 13px;")

        label_paso_5_instruccion = QtWidgets.QLabel(
            'Como resultado final se debe de obtener una lista de directorios en la sección izquierda del software, cada uno de estos contiene las señales\ncorrespondientes a cada EMG.')
        label_paso_5_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_5 = QtGui.QPixmap(':/Static/img/paso5.png')
        lab5 = QtWidgets.QLabel()
        lab5.setPixmap(img_paso_5)

        widget_paso_5.layout().addWidget(label_paso_5_titulo)
        widget_paso_5.layout().addWidget(label_paso_5_instruccion)
        widget_paso_5.layout().addWidget(lab5)

        layout_scroll.addWidget(widget_paso_1)
        layout_scroll.addWidget(widget_paso_2)
        layout_scroll.addWidget(widget_paso_3)
        layout_scroll.addWidget(widget_paso_4)
        layout_scroll.addWidget(widget_paso_5)

        scroll_area.setWidget(widget_scroll)
        self.layout().addWidget(scroll_area, 10)


class ventana_verayuda_despues_columnas(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ventana_verayuda_despues_columnas, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Ayuda - Abrir archivo csv")
        self.setFixedSize(900, 600)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.setStyleSheet("background-color:white;")
        self.layout().setContentsMargins(8, 8, 0, 0)
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=10, xOffset=1, yOffset=1)

        layout_scroll = QtWidgets.QVBoxLayout()
        layout_scroll.setAlignment(Qt.AlignTop)
        layout_scroll.setContentsMargins(4, 4, 4, 4)
        layout_scroll.setSpacing(16)

        widget_scroll = QtWidgets.QWidget()
        widget_scroll.setLayout(layout_scroll)

        # SCROLL AREA
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setStyleSheet(estilos.estilos_sroll_area())
        # scroll_area.setGraphicsEffect(shadow)

        #OBSERVACIÓN
        widget_observacion = QtWidgets.QWidget()
        widget_observacion.setLayout(QtWidgets.QVBoxLayout())
        widget_observacion.layout().setAlignment(Qt.AlignTop)
        widget_observacion.layout().setSpacing(8)

        label_observacion = QtWidgets.QLabel("Observación:")
        label_observacion.setStyleSheet("font: bold 13px;")

        widget_label_instruccion = QtWidgets.QWidget()
        widget_label_instruccion.setLayout(QtWidgets.QVBoxLayout())
        widget_label_instruccion.layout().setAlignment(Qt.AlignTop)
        widget_label_instruccion.layout().setContentsMargins(0, 0, 0, 0)
        widget_label_instruccion.layout().setSpacing(1)

        label_paso_1_instruccion_a = QtWidgets.QLabel(
            'Si al abrirse la ventana de "Configuraciones de columnas de información" las columnas contienen números en su nombres como se puede')
        label_paso_1_instruccion_a.setStyleSheet("font-size: 13px;")

        widget_label_instruccion_b = QtWidgets.QWidget()
        widget_label_instruccion_b.setLayout(QtWidgets.QHBoxLayout())
        widget_label_instruccion_b.layout().setAlignment(Qt.AlignLeft)
        widget_label_instruccion_b.layout().setContentsMargins(0, 0, 0, 0)
        widget_label_instruccion_b.layout().setSpacing(8)

        label_paso_1_instruccion_b = QtWidgets.QLabel(
            'apreciar en la siguiente imagen, significa que el número de fila no se configuró correctamente, consulte la siguiente guía.')
        label_paso_1_instruccion_b.setStyleSheet("font-size: 13px;")

        btn_ver_guia = QtWidgets.QPushButton()
        btn_ver_guia.setText("Consultar guía")
        btn_ver_guia.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_ver_guia.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_ver_guia.clicked.connect(self.xdd)

        widget_label_instruccion_b.layout().addWidget(label_paso_1_instruccion_b)
        widget_label_instruccion_b.layout().addWidget(btn_ver_guia)

        widget_label_instruccion.layout().addWidget(label_paso_1_instruccion_a)
        widget_label_instruccion.layout().addWidget(widget_label_instruccion_b)

        img_observacion = QtGui.QPixmap(':/Static/img/observacion_dsp.png')
        lab_img_obs = QtWidgets.QLabel()
        lab_img_obs.setPixmap(img_observacion)

        widget_observacion.layout().addWidget(label_observacion)
        widget_observacion.layout().addWidget(widget_label_instruccion)
        widget_observacion.layout().addWidget(lab_img_obs)


        #PASO 1
        widget_paso_1 = QtWidgets.QWidget()
        widget_paso_1.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_1.layout().setAlignment(Qt.AlignTop)
        widget_paso_1.layout().setSpacing(8)

        label_paso_1_titulo = QtWidgets.QLabel("Instrucciones:")
        label_paso_1_titulo.setStyleSheet("font: bold 13px;")

        label_paso_1_instruccion = QtWidgets.QLabel(
            ' Al importar un archivo ".csv" diferente a los de Trigno se desplegará la siguiente ventana.')
        label_paso_1_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_1 = QtGui.QPixmap(':/Static/img/paso1_dsp.png')
        lab1 = QtWidgets.QLabel()
        lab1.setPixmap(img_paso_1)

        widget_paso_1.layout().addWidget(label_paso_1_titulo)
        widget_paso_1.layout().addWidget(label_paso_1_instruccion)
        widget_paso_1.layout().addWidget(lab1)

        # PASO 2
        widget_paso_2 = QtWidgets.QWidget()
        widget_paso_2.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_2.layout().setAlignment(Qt.AlignTop)
        widget_paso_2.layout().setSpacing(8)

        label_paso_2_titulo = QtWidgets.QLabel("Paso 2:")
        label_paso_2_titulo.setStyleSheet("font: bold 13px;")

        label_paso_2_instruccion = QtWidgets.QLabel(
            "En la sección (1), si el usuario desea seleccionar las columnas del archivo debe hacer click sobre el botón “Seleccionar” (3).")
        label_paso_2_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_2 = QtGui.QPixmap(':/Static/img/paso1_dsp_b.png')
        lab2 = QtWidgets.QLabel()
        lab2.setPixmap(img_paso_2)

        #widget_paso_2.layout().addWidget(label_paso_2_titulo)
        widget_paso_2.layout().addWidget(label_paso_2_instruccion)
        widget_paso_2.layout().addWidget(lab2)

        # PASO 3
        widget_paso_3 = QtWidgets.QWidget()
        widget_paso_3.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_3.layout().setAlignment(Qt.AlignTop)
        widget_paso_3.layout().setSpacing(8)

        label_paso_3_titulo = QtWidgets.QLabel("Paso 3:")
        label_paso_3_titulo.setStyleSheet("font: bold 13px;")

        label_paso_3_instruccion = QtWidgets.QLabel(
            'Al hacer esto, se mostrará por cada columna, una casilla de verificación correspondiente, en la cual el usuario podrá seleccionar las que desee\nhaciendo click sobre la misma. (4)Si se desea deseleccionar todas las casillas marcadas, se debe hacer click en el botón de “Cancelar” (5).')
        label_paso_3_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_3 = QtGui.QPixmap(':/Static/img/paso1_dsp_c.png')
        lab3 = QtWidgets.QLabel()
        lab3.setPixmap(img_paso_3)

        #widget_paso_3.layout().addWidget(label_paso_3_titulo)
        widget_paso_3.layout().addWidget(label_paso_3_instruccion)
        widget_paso_3.layout().addWidget(lab3)

        # PASO 4
        widget_paso_4 = QtWidgets.QWidget()
        widget_paso_4.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_4.layout().setAlignment(Qt.AlignTop)
        widget_paso_4.layout().setSpacing(8)

        label_paso_4_titulo = QtWidgets.QLabel("Paso 4:")
        label_paso_4_titulo.setStyleSheet("font: bold 13px;")

        label_paso_4_instruccion = QtWidgets.QLabel(
            'Adicionalmente, si se desea trabajar con todos los datos del archivo, se debe clickear sobre el botón “seleccionar todas” (6). Al hacer esto, se\nmarcarán automáticamente todas las casillas de verificación que no estén seleccionadas (7). Es debido a esto que el usuario no deberá\nseleccionarlas una por una. ')
        label_paso_4_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_4 = QtGui.QPixmap(':/Static/img/paso1_dsp_d.png')
        lab4 = QtWidgets.QLabel()
        lab4.setPixmap(img_paso_4)

        #widget_paso_4.layout().addWidget(label_paso_4_titulo)
        widget_paso_4.layout().addWidget(label_paso_4_instruccion)
        widget_paso_4.layout().addWidget(lab4)

        # PASO 5
        widget_paso_5 = QtWidgets.QWidget()
        widget_paso_5.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_5.layout().setAlignment(Qt.AlignTop)
        widget_paso_5.layout().setSpacing(8)

        label_paso_5_titulo = QtWidgets.QLabel("Paso 5:")
        label_paso_5_titulo.setStyleSheet("font: bold 13px;")

        label_paso_5_instruccion = QtWidgets.QLabel(
            '''En la segunda sección (2), si se desean quitar las columnas seleccionadas, se debe clickear sobre el botón “Filtrar Seleccionados” (4).
Por otro lado, si quiere quitar las no seleccionadas se debe clickear en “Filtrar no seleccionados” (5).
Además, se pueden filtrar aquellas columnas del archivo que en su nombre contengan los caracteres ingresados en la caja de texto (6).
Si se desea conservar aquellas columnas que cumplen con lo ingresado en el paso anterior, se debe desactivar la casilla de verificación
llamada “Eliminar coincidencias”, y de lo contrario, se debe dejar dicha casilla verificada (7).
Para que el filtro por caracteres se aplique sobre las columnas, se debe clickear sobre el botón “Filtrar” (8).

Luego de realizar estos pasos, el usuario debe clickear sobre el botón “Siguiente” para poder continuar hacia la siguiente ventana de configuración.
''')
        label_paso_5_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_5 = QtGui.QPixmap(':/Static/img/paso1_dsp_e.png')
        lab5 = QtWidgets.QLabel()
        lab5.setPixmap(img_paso_5)

        #widget_paso_5.layout().addWidget(label_paso_5_titulo)
        widget_paso_5.layout().addWidget(label_paso_5_instruccion)
        widget_paso_5.layout().addWidget(lab5)

        #PASO 6

        widget_paso_6 = QtWidgets.QWidget()
        widget_paso_6.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_6.layout().setAlignment(Qt.AlignTop)
        widget_paso_6.layout().setSpacing(8)

        label_paso_6_titulo = QtWidgets.QLabel("Paso 6:")
        label_paso_6_titulo.setStyleSheet("font: bold 13px;")

        label_paso_6_instruccion = QtWidgets.QLabel(
            '''Luego de realizar el paso (9), se mantendrá la sección izquierda con las columnas de archivos filtradas, y se mostrará una nueva sección
llamada “Directorios”. En ella, el usuario podrá crear directorios donde se contendrán las columnas que el usuario desee. Esta función es
útil a la hora de organizar todas las columnas que se van a importar. Para ello, deberá crear un nuevo directorio haciendo click sobre el
botón “Nuevo directorio” (10)
''')
        label_paso_6_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_6 = QtGui.QPixmap(':/Static/img/paso1_dsp_f.png')
        lab6 = QtWidgets.QLabel()
        lab6.setPixmap(img_paso_6)

        # widget_paso_6.layout().addWidget(label_paso_6_titulo)
        widget_paso_6.layout().addWidget(label_paso_6_instruccion)
        widget_paso_6.layout().addWidget(lab6)

        #PASO 7

        widget_paso_7 = QtWidgets.QWidget()
        widget_paso_7.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_7.layout().setAlignment(Qt.AlignTop)
        widget_paso_7.layout().setSpacing(8)

        label_paso_7_titulo = QtWidgets.QLabel("Paso 6:")
        label_paso_7_titulo.setStyleSheet("font: bold 13px;")

        label_paso_7_instruccion = QtWidgets.QLabel(
            '''hacer esto, se desplegará la siguiente ventana, en la que se podrá escoger un nombre para el directorio a crear (11).
Para finalizar, se debe clickear sobre el botón “Confirmar” (12).
''')
        label_paso_7_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_7 = QtGui.QPixmap(':/Static/img/paso1_dsp_g.png')
        lab7 = QtWidgets.QLabel()
        lab7.setPixmap(img_paso_7)

        # widget_paso_7.layout().addWidget(label_paso_7_titulo)
        widget_paso_7.layout().addWidget(label_paso_7_instruccion)
        widget_paso_7.layout().addWidget(lab7)

        #PASO 8
        widget_paso_8 = QtWidgets.QWidget()
        widget_paso_8.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_8.layout().setAlignment(Qt.AlignTop)
        widget_paso_8.layout().setSpacing(8)

        label_paso_8_titulo = QtWidgets.QLabel("Paso 6:")
        label_paso_8_titulo.setStyleSheet("font: bold 13px;")

        label_paso_8_instruccion = QtWidgets.QLabel(
            '''Una vez se tenga el directorio creado, el usuario deberá agregar columnas al mismo para poder confirmar su selección. Para realizar esto, se
debe hacer click derecho sobre el directorio (13), lo cual desplegará el siguiente menú (14).

En este menú, se podrán realizar las siguientes acciones para agregar las columnas del archivo seleccionadas al directorio:
    1.  Importar columnas seleccionadas: Al hacer click sobre esta opción, se añadirán todas las columnas que se 
         encuentren seleccionadas dentro del directorio.
    2.  Importar rango de columnas: Se deben seleccionar únicamente 2 casillas de verificación de la sección de 
         columnas del archivo, y se añadirán al directorio todas las que estén entre ese rango, incluyendo las que se seleccionaron.
    3.  Eliminar columnas: Elimina todas las columnas que se encuentren dentro del directorio.
    4.  Eliminar directorio: Remueve el directorio creado y todas las columnas que este contenga.
''')
        label_paso_8_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_8 = QtGui.QPixmap(':/Static/img/paso1_dsp_h.png')
        lab8 = QtWidgets.QLabel()
        lab8.setPixmap(img_paso_8)

        #widget_paso_8.layout().addWidget(label_paso_8_titulo)
        widget_paso_8.layout().addWidget(label_paso_8_instruccion)
        widget_paso_8.layout().addWidget(lab8)

        #PASO 9

        widget_paso_9 = QtWidgets.QWidget()
        widget_paso_9.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_9.layout().setAlignment(Qt.AlignTop)
        widget_paso_9.layout().setSpacing(8)

        label_paso_9_titulo = QtWidgets.QLabel("Paso 6:")
        label_paso_9_titulo.setStyleSheet("font: bold 13px;")

        label_paso_9_instruccion = QtWidgets.QLabel(
            '''     5.  Cambiar nombre: Si por alguna razón el usuario desea cambiar el nombre del directorio creado anteriormente, al hacer click sobre
          esta opción se muestra la siguiente pantalla en donde se deberá escribir el nuevo nombre del directorio (5.1) y luego se tendrá que clickear
          sobre el botón “Confirmar” para aplicar los cambios (5.2). ''')
        label_paso_9_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_9 = QtGui.QPixmap(':/Static/img/paso1_dsp_i.png')
        lab9 = QtWidgets.QLabel()
        lab9.setPixmap(img_paso_9)

        # widget_paso_9.layout().addWidget(label_paso_9_titulo)
        widget_paso_9.layout().addWidget(label_paso_9_instruccion)
        widget_paso_9.layout().addWidget(lab9)

        #PASO 10
        widget_paso_10 = QtWidgets.QWidget()
        widget_paso_10.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_10.layout().setAlignment(Qt.AlignTop)
        widget_paso_10.layout().setSpacing(8)

        label_paso_10_titulo = QtWidgets.QLabel("Paso 6:")
        label_paso_10_titulo.setStyleSheet("font: bold 13px;")

        label_paso_10_instruccion = QtWidgets.QLabel(
            '''Cabe destacar que una vez agregadas las columnas a un directorio, si por determinado motivo el usuario lo desea, se pueden eliminar,
haciendo click derecho sobre una de ellas y luego en “Eliminar” (15).''')

        label_paso_10_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_10 = QtGui.QPixmap(':/Static/img/paso1_dsp_j.png')
        lab10 = QtWidgets.QLabel()
        lab10.setPixmap(img_paso_10)

        # widget_paso_10.layout().addWidget(label_paso_10_titulo)
        widget_paso_10.layout().addWidget(label_paso_10_instruccion)
        widget_paso_10.layout().addWidget(lab10)

        #PASO 11

        widget_paso_11 = QtWidgets.QWidget()
        widget_paso_11.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_11.layout().setAlignment(Qt.AlignTop)
        widget_paso_11.layout().setSpacing(8)

        label_paso_11_titulo = QtWidgets.QLabel("Paso 6:")
        label_paso_11_titulo.setStyleSheet("font: bold 13px;")

        label_paso_11_instruccion = QtWidgets.QLabel(
            '''Por último, para confirmar los cambios, se deberá hacer click sobre el botón “Confirmar” (16)''')

        label_paso_11_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_11 = QtGui.QPixmap(':/Static/img/paso1_dsp_k.png')
        lab11 = QtWidgets.QLabel()
        lab11.setPixmap(img_paso_11)

        # widget_paso_11.layout().addWidget(label_paso_11_titulo)
        widget_paso_11.layout().addWidget(label_paso_11_instruccion)
        widget_paso_11.layout().addWidget(lab11)

        #PASO 12
        widget_paso_12 = QtWidgets.QWidget()
        widget_paso_12.setLayout(QtWidgets.QVBoxLayout())
        widget_paso_12.layout().setAlignment(Qt.AlignTop)
        widget_paso_12.layout().setSpacing(8)

        label_paso_12_titulo = QtWidgets.QLabel("Paso 6:")
        label_paso_12_titulo.setStyleSheet("font: bold 13px;")

        label_paso_12_instruccion = QtWidgets.QLabel(
            '''Luego de realizar todos los pasos mencionados anteriormente se mostrará en el panel de archivos “.csv” ubicado en la sección izquierda de
la pantalla principal, el siguiente resultado, es decir, los directorios creados y las columnas que fueron insertadas en los mismos.
A continuación se podrán graficar dichas columnas.
''')

        label_paso_12_instruccion.setStyleSheet("font-size: 13px;")

        img_paso_12 = QtGui.QPixmap(':/Static/img/paso1_dsp_l.png')
        lab12 = QtWidgets.QLabel()
        lab12.setPixmap(img_paso_12)

        # widget_paso_12.layout().addWidget(label_paso_12_titulo)
        widget_paso_12.layout().addWidget(label_paso_12_instruccion)
        widget_paso_12.layout().addWidget(lab12)

        #SE AGREGA TODOS LOS WIDGET
        layout_scroll.addWidget(widget_observacion)
        layout_scroll.addWidget(widget_paso_1)
        layout_scroll.addWidget(widget_paso_2)
        layout_scroll.addWidget(widget_paso_3)
        layout_scroll.addWidget(widget_paso_4)
        layout_scroll.addWidget(widget_paso_5)
        layout_scroll.addWidget(widget_paso_6)
        layout_scroll.addWidget(widget_paso_7)
        layout_scroll.addWidget(widget_paso_8)
        layout_scroll.addWidget(widget_paso_9)
        layout_scroll.addWidget(widget_paso_10)
        layout_scroll.addWidget(widget_paso_11)
        layout_scroll.addWidget(widget_paso_12)

        scroll_area.setWidget(widget_scroll)
        self.layout().addWidget(scroll_area, 10)

    def xdd(self):
        ventana_verayuda_antes_columnas(self).exec_()


class Manualdeusuario(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Manualdeusuario, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Manual de usuario")
        self.setFixedSize(1140, 700)
        self.setLayout(QtWidgets.QHBoxLayout())
        #self.layout().setAlignment(Qt.AlignTop)
        self.setStyleSheet("background-color:white;")
        self.layout().setContentsMargins(2, 2, 2, 2)

        wid_izquierda = QtWidgets.QWidget()
        wid_izquierda.setStyleSheet("border-right:1px solid #BDBDBD;")
        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())
        wid_izquierda.layout().setAlignment(Qt.AlignLeft | Qt.AlignTop)

        layout_wid_derecha = QtWidgets.QVBoxLayout()
        layout_wid_derecha.setAlignment(Qt.AlignTop)
        layout_wid_derecha.setContentsMargins(4, 4, 4, 4)
        layout_wid_derecha.setSpacing(16)


        wid_derecha = QtWidgets.QWidget()
        wid_derecha.setLayout(layout_wid_derecha)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setStyleSheet(estilos.estilos_sroll_area())

        #wid_derecha.layout().addWidget(self.scroll , 10)

        self.layout().addWidget(wid_izquierda, 3)


        #BOTONES INDICE
        btn_inicio = QtWidgets.QPushButton()
        btn_inicio.setText("1 Introducción")
        btn_inicio.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_inicio.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_inicio.clicked.connect(self.inicio)
        wid_izquierda.layout().addWidget(btn_inicio)

        btn_manipular_archivo_csv = QtWidgets.QPushButton()
        btn_manipular_archivo_csv.setText("1.1 Manipular archivos en formato “.csv”")
        btn_manipular_archivo_csv.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_manipular_archivo_csv.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_manipular_archivo_csv.clicked.connect(self.manipular_csv)
        wid_izquierda.layout().addWidget(btn_manipular_archivo_csv)

        btn_agregar_csv = QtWidgets.QPushButton()
        btn_agregar_csv.setText("1.1.1 Importar archivo “.csv”")
        btn_agregar_csv.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_agregar_csv.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_agregar_csv.clicked.connect(self.importar_csv)
        wid_izquierda.layout().addWidget(btn_agregar_csv)

        btn_agregar_csv_distinto = QtWidgets.QPushButton()
        btn_agregar_csv_distinto.setText("1.1.2 Importar archivo “.csv” con formato diferente a Trigno")
        btn_agregar_csv_distinto.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_agregar_csv_distinto.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_agregar_csv_distinto.clicked.connect(self.importar_csv_diferente)
        wid_izquierda.layout().addWidget(btn_agregar_csv_distinto)

        btn_eliminar_csv = QtWidgets.QPushButton()
        btn_eliminar_csv.setText("1.1.3 Eliminar archivo “.csv”")
        btn_eliminar_csv.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_eliminar_csv.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_eliminar_csv.clicked.connect(self.eliminar_archivo)
        wid_izquierda.layout().addWidget(btn_eliminar_csv)

        btn_manejo_vistas = QtWidgets.QPushButton()
        btn_manejo_vistas.setText("1.2 Manejo de Vistas")
        btn_manejo_vistas.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_manejo_vistas.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_manejo_vistas.clicked.connect(self.manejo_vistas)
        wid_izquierda.layout().addWidget(btn_manejo_vistas)

        btn_graficar_datos = QtWidgets.QPushButton()
        btn_graficar_datos.setText("1.3 Graficar Datos")
        btn_graficar_datos.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_graficar_datos.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_graficar_datos.clicked.connect(self.graficar_datos)
        wid_izquierda.layout().addWidget(btn_graficar_datos)

        btn_manipulacion_graficas = QtWidgets.QPushButton()
        btn_manipulacion_graficas.setText("1.4 Manipulación de Gráficas")
        btn_manipulacion_graficas.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_manipulacion_graficas.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_manipulacion_graficas.clicked.connect(self.manipulacion_de_graficas)
        wid_izquierda.layout().addWidget(btn_manipulacion_graficas)

        btn_valores_bruto = QtWidgets.QPushButton()
        btn_valores_bruto.setText("1.4.1 Valores en bruto")
        btn_valores_bruto.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_valores_bruto.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_valores_bruto.clicked.connect(self.valores_en_bruto)
        wid_izquierda.layout().addWidget(btn_valores_bruto)

        btn_rectificar_grafico = QtWidgets.QPushButton()
        btn_rectificar_grafico.setText("1.4.2 Rectificar Gráfico")
        btn_rectificar_grafico.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_rectificar_grafico.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_rectificar_grafico.clicked.connect(self.rectificar_grafico)
        wid_izquierda.layout().addWidget(btn_rectificar_grafico)

        btn_aplicar_filtros = QtWidgets.QPushButton()
        btn_aplicar_filtros.setText("1.4.3 Aplicar filtros")
        btn_aplicar_filtros.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_aplicar_filtros.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_aplicar_filtros.clicked.connect(self.aplicar_filtros)
        wid_izquierda.layout().addWidget(btn_aplicar_filtros)

        btn_recortar_grafico = QtWidgets.QPushButton()
        btn_recortar_grafico.setText("1.4.4 Recortar Gráfico")
        btn_recortar_grafico.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_recortar_grafico.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_recortar_grafico.clicked.connect(self.recortar_grafico)
        wid_izquierda.layout().addWidget(btn_recortar_grafico)

        btn_recortar_grafico_clicki = QtWidgets.QPushButton()
        btn_recortar_grafico_clicki.setText("1.4.5 Recortar gráfico haciendo click")
        btn_recortar_grafico_clicki.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_recortar_grafico_clicki.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_recortar_grafico_clicki.clicked.connect(self.recortar_haciendo_click)
        wid_izquierda.layout().addWidget(btn_recortar_grafico_clicki)

        btn_valores_grafica = QtWidgets.QPushButton()
        btn_valores_grafica.setText("1.4.6 Valores en la gráfica")
        btn_valores_grafica.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_valores_grafica.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_valores_grafica.clicked.connect(self.valores_en_grafica)
        wid_izquierda.layout().addWidget(btn_valores_grafica)

        btn_calcular_ymostrar_valores_picos = QtWidgets.QPushButton()
        btn_calcular_ymostrar_valores_picos.setText("1.4.6.1 Calcular y mostrar valores picos")
        btn_calcular_ymostrar_valores_picos.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_calcular_ymostrar_valores_picos.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_calcular_ymostrar_valores_picos.clicked.connect(self.valores_picos)
        wid_izquierda.layout().addWidget(btn_calcular_ymostrar_valores_picos)

        btn_calcular_ymostrar_integral = QtWidgets.QPushButton()
        btn_calcular_ymostrar_integral.setText("1.4.6.2 Calcular y mostrar integral")
        btn_calcular_ymostrar_integral.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_calcular_ymostrar_integral.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_calcular_ymostrar_integral.clicked.connect(self.valores_integral)
        wid_izquierda.layout().addWidget(btn_calcular_ymostrar_integral)

        btn_calcular_ymostrar_integral_clicki = QtWidgets.QPushButton()
        btn_calcular_ymostrar_integral_clicki.setText("1.4.6.3 Calcular y mostrar integral haciendo click")
        btn_calcular_ymostrar_integral_clicki.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_calcular_ymostrar_integral_clicki.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_calcular_ymostrar_integral_clicki.clicked.connect(self.valores_integral_clicki)
        wid_izquierda.layout().addWidget(btn_calcular_ymostrar_integral_clicki)

        btn_calcular_ymostrar_rms = QtWidgets.QPushButton()
        btn_calcular_ymostrar_rms.setText("1.4.6.4 Calcular y mostrar valor RMS")
        btn_calcular_ymostrar_rms.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_calcular_ymostrar_rms.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_calcular_ymostrar_rms.clicked.connect(self.valores_rms)
        wid_izquierda.layout().addWidget(btn_calcular_ymostrar_rms)

        btn_comparar = QtWidgets.QPushButton()
        btn_comparar.setText("1.4.7 Comparar")
        btn_comparar.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_comparar.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_comparar.clicked.connect(self.comparar)
        wid_izquierda.layout().addWidget(btn_comparar)

        btn_eliminar_grafica = QtWidgets.QPushButton()
        btn_eliminar_grafica.setText("1.4.8 Eliminar gráfica")
        btn_eliminar_grafica.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_eliminar_grafica.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_eliminar_grafica.clicked.connect(self.eliminar_grafica)
        wid_izquierda.layout().addWidget(btn_eliminar_grafica)

        btn_panel_superior_grafico = QtWidgets.QPushButton()
        btn_panel_superior_grafico.setText("1.4.9 Panel superior del gráfico")
        btn_panel_superior_grafico.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_panel_superior_grafico.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_panel_superior_grafico.clicked.connect(self.panel_superior)
        wid_izquierda.layout().addWidget(btn_panel_superior_grafico)

        btn_configuracion_programa = QtWidgets.QPushButton()
        btn_configuracion_programa.setText("1.5 Sección de Configuración del Programa")
        btn_configuracion_programa.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_configuracion_programa.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_configuracion_programa.clicked.connect(self.seccion_configuraciones)
        wid_izquierda.layout().addWidget(btn_configuracion_programa)

        btn_configuracion_archivos = QtWidgets.QPushButton()
        btn_configuracion_archivos.setText("1.5.1 Configuración de archivos")
        btn_configuracion_archivos.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_configuracion_archivos.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_configuracion_archivos.clicked.connect(self.configuraciones_archivos)
        wid_izquierda.layout().addWidget(btn_configuracion_archivos)

        btn_configuracion_limite_graficas = QtWidgets.QPushButton()
        btn_configuracion_limite_graficas.setText("1.5.2 Configuración de límite de gráficas")
        btn_configuracion_limite_graficas.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_configuracion_limite_graficas.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_configuracion_limite_graficas.clicked.connect(self.configuraciones_limites_graficas)
        wid_izquierda.layout().addWidget(btn_configuracion_limite_graficas)


        btn_exportar = QtWidgets.QPushButton()
        btn_exportar.setText("1.6 Exportar datos")
        btn_exportar.setStyleSheet(estilos.estilos_btn_ver_guia())
        btn_exportar.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        btn_exportar.clicked.connect(self.exportar_datos)
        wid_izquierda.layout().addWidget(btn_exportar)

        #WIDGET DERECHA (CONTENIDO)

        #INTRODUCCIÓN
        widget_introduccion = QtWidgets.QWidget()

        widget_introduccion.setLayout(QtWidgets.QVBoxLayout())
        widget_introduccion.layout().setAlignment(Qt.AlignTop)
        widget_introduccion.layout().setContentsMargins(0,0,0,0)
        widget_introduccion.layout().setSpacing(8)

        widget_introduccion2 = QtWidgets.QWidget()

        widget_introduccion2.setLayout(QtWidgets.QVBoxLayout())
        widget_introduccion2.layout().setAlignment(Qt.AlignTop)
        widget_introduccion2.layout().setContentsMargins(0, 0, 0, 0)
        widget_introduccion2.layout().setSpacing(8)

        label_introduccion = QtWidgets.QLabel("1 Introducción:")
        label_introduccion.setStyleSheet("font: bold 13px;")

        label_texto_introduccion = QtWidgets.QLabel(
            """Analysis of Biomechanical Signal (ABS) es un software que tiene como objetivo facilitar el análisis de señales electromiográficas procedentes del aparato Trigno, ofreciendo la posibilidad de visualizar en forma de gráficas la información que se encuentra en los archivos .csv obtenidos por el mismo así como también, si el usuario lo desea, aplicar filtros y cálculos a dichas gráficas.

Este software cuenta con tres distribuciones dependiendo de qué sistema operativo se utilice (Windows, Linux y MacOS). Dado que estas son portables no es necesario realizar una instalación del programa; solamente se deberá solicitar a los representantes del LIBiAM una copia de la carpeta correspondiente al sistema operativo instalado en el equipo del usuario.

Para poder utilizar ABSse debe hacer doble click en el archivo ejecutable “ABS”,que se encuentra dentro de la carpeta mencionada anteriormente (se recomienda ubicarla en el Escritorio del equipo).

Una vez realizado el paso anterior, se visualizará la pantalla principal, con las diferentes secciones que la componen. Estas serán explicadas a continuación.
""")
        label_texto_introduccion.setStyleSheet("font-size: 13px;")
        label_texto_introduccion.setFixedWidth(735)
        label_texto_introduccion.setWordWrap(True)


        img_paso_1 = QtGui.QPixmap(':/Static/img/img1.png')
        lab0 = QtWidgets.QLabel()
        lab0.setPixmap(img_paso_1)

        #(1)
        label_a1 = QtWidgets.QLabel(
            """(1) En esta sección se pueden realizar operaciones básicas tales como importar un archivo .csv, como se explica en el punto 1.1.1 de este manual. Asimismo, se pueden realizar configuraciones, tal como se detalla en el punto 1.5.""")
        label_a1.setStyleSheet("font-size: 13px;margin-top:30px;")
        label_a1.setFixedWidth(735)
        label_a1.setWordWrap(True)

        img2 = QtGui.QPixmap(':/Static/img/img2.png')
        lab2 = QtWidgets.QLabel()
        lab2.setPixmap(img2)

        # (2)
        label_a3 = QtWidgets.QLabel(
            """(2) En esta sección se encuentra la barra superior de navegación, a través de la que se pueden acceder a las diferentes funcionalidades que brinda el software. Estas son: crear una nueva vista, agregar y quitar filtros a una gráfica, realizarle recortes, obtener valores de interés al aplicar cálculos matemáticos (valor RMS, valores máximos, integral) sobre una o varias gráficas, comparar gráficas y exportar datos.""")
        label_a3.setStyleSheet("font-size: 13px;margin-top:30px;")
        label_a3.setFixedWidth(735)
        label_a3.setWordWrap(True)

        img3 = QtGui.QPixmap(':/Static/img/img3.png')
        lab3 = QtWidgets.QLabel()
        lab3.setPixmap(img3)

        # (3)

        label_a4 = QtWidgets.QLabel(
            """(3) Esta es la sección donde se muestran los archivos .csv que se hayan agregado con anterioridad al software. Los datos de estos archivos se encuentra organizado dentro de diferentes directorios y contienen las señales electromiográficas que posteriormente serán graficadas si el usuario lo desea. 
También se puede agregar o eliminar archivos .csv y minimizar la sección, como se detalla en los puntos 1.1.1, 1.1.2 y 1.1.3 del manual
""")
        label_a4.setStyleSheet("font-size: 13px;margin-top:30px;")
        label_a4.setFixedWidth(735)
        label_a4.setWordWrap(True)

        img4 = QtGui.QPixmap(':/Static/img/img4.png')
        lab4 = QtWidgets.QLabel()
        lab4.setPixmap(img4)

        # (4)

        label_a5 = QtWidgets.QLabel(
            """(4) En esta sección se muestran las vistas creadas además de las señales que se encuentran abiertas en dichas vistas.""")
        label_a5.setStyleSheet("font-size: 13px;margin-top:30px;")
        label_a5.setFixedWidth(735)
        label_a5.setWordWrap(True)

        img5 = QtGui.QPixmap(':/Static/img/img5.png')
        lab5 = QtWidgets.QLabel()
        lab5.setPixmap(img5)

        # (5)
        label_a6 = QtWidgets.QLabel(
            """(5) Esta es la sección donde se encuentran todas las vistas y se pueden ver las gráficas. Cuando se inicia el programa se mostrará una pestaña llamada “Inicio” la cual contiene información del LIBiAM.""")
        label_a6.setStyleSheet("font-size: 13px;margin-top:30px;")
        label_a6.setFixedWidth(735)
        label_a6.setWordWrap(True)

        img6 = QtGui.QPixmap(':/Static/img/img6.png')
        lab6 = QtWidgets.QLabel()
        lab6.setPixmap(img6)

        # 1.1 Manipular archivos en formato .csv

        label_manipular_archivos_csv = QtWidgets.QLabel("1.1 Manipular archivos en formato .csv")
        label_manipular_archivos_csv.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a7 = QtWidgets.QLabel(
            """Por defecto el sistema interpreta el archivo .csv con el formato obtenido del aparato Trigno, pero cabe destacar que también se pueden importar archivos de este tipo con un contenido distinto al de Trigno, como se indica en el punto 1.1.2 del manual.""")
        label_a7.setStyleSheet("font-size: 13px;")
        label_a7.setFixedWidth(735)
        label_a7.setWordWrap(True)

        # 1.1.1 Importar archivo .csv

        label_importar_archivos_csv = QtWidgets.QLabel("1.1.1 Importar archivo .csv")
        label_importar_archivos_csv.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a8 = QtWidgets.QLabel(
            """El software permite importar uno o varios archivos .csv haciendo click en el menú “Archivo” (1) y luego en la opción “Abrir .CSV” (2).""")
        label_a8.setStyleSheet("font-size: 13px;")
        label_a8.setFixedWidth(735)
        label_a8.setWordWrap(True)

        img7 = QtGui.QPixmap(':/Static/img/img7.png')
        lab7 = QtWidgets.QLabel()
        lab7.setPixmap(img7)

        label_a9 = QtWidgets.QLabel(
            """También se puede lograr lo anteriormente mencionado haciendo click en el ícono de suma (“+”) en el menú principal (3).""")
        label_a9.setStyleSheet("font-size: 13px;")
        label_a9.setFixedWidth(735)
        label_a9.setWordWrap(True)

        img8 = QtGui.QPixmap(':/Static/img/img8.png')
        lab8 = QtWidgets.QLabel()
        lab8.setPixmap(img8)

        label_a10 = QtWidgets.QLabel(
            """Posteriormente se desplegará una ventana donde se puede abrir un archivo .csv proveniente de Trigno haciendo click sobre el mismo (4). Para finalizar la acción se da click en abrir (5).""")
        label_a10.setStyleSheet("font-size: 13px;")
        label_a10.setFixedWidth(735)
        label_a10.setWordWrap(True)

        img9 = QtGui.QPixmap(':/Static/img/img9.png')
        lab9 = QtWidgets.QLabel()
        lab9.setPixmap(img9)

        label_a11 = QtWidgets.QLabel(
            """Luego de esto el programa mostrará en el panel izquierdo el nombre del archivo importado y su contenido organizado en directorios. Dentro de ellos se encuentran contenidas las señales electromiográficas (6) que posteriormente serán graficadas si el usuario lo desea, tal como se indica en el punto 1.3 del manual. """)
        label_a11.setStyleSheet("font-size: 13px;")
        label_a11.setFixedWidth(735)
        label_a11.setWordWrap(True)

        img10 = QtGui.QPixmap(':/Static/img/img10.png')
        lab10 = QtWidgets.QLabel()
        lab10.setPixmap(img10)

        # 1.1.2 Importar archivo .csv con formato diferente a Trigno

        label_importar_archivos_csv_diferentes = QtWidgets.QLabel("1.1.2 Importar archivo .csv con formato diferente a Trigno")
        label_importar_archivos_csv_diferentes.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a12 = QtWidgets.QLabel(
            """Como se explicó anteriormente, el programa detecta por defecto el formato de archivo que genera el aparato Trigno. En caso de que suceda lo contrario, se mostrará el siguiente error. Este ocurre cuando, al importar un archivo, el número de la fila que se le especificó al software (como se indica en el punto 1.5.1 del manual) no corresponde a la del archivo .csv donde comienzan los datos correspondientes a cada sensor de electromiografía.""")
        label_a12.setStyleSheet("font-size: 13px;")
        label_a12.setFixedWidth(735)
        label_a12.setWordWrap(True)

        img11 = QtGui.QPixmap(':/Static/img/img11.png')
        lab11= QtWidgets.QLabel()
        lab11.setPixmap(img11)

        label_a13 = QtWidgets.QLabel(
            """Luego de clickear en el botón “OK”, se desplegará la siguiente ventana, la cual cuenta con dos secciones: una para seleccionar columnas (1) y la otra para el filtrado de aquellas columnas que no son de interés para el usuario (2).""")
        label_a13.setStyleSheet("font-size: 13px;")
        label_a13.setFixedWidth(735)
        label_a13.setWordWrap(True)

        img12 = QtGui.QPixmap(':/Static/img/img12.png')
        lab12 = QtWidgets.QLabel()
        lab12.setPixmap(img12)

        label_a14 = QtWidgets.QLabel(
            """Si se desean seleccionar las columnas del archivo se debe hacer click sobre el botón “Seleccionar”(3) en la sección (1).""")
        label_a14.setStyleSheet("font-size: 13px;")
        label_a14.setFixedWidth(735)
        label_a14.setWordWrap(True)

        img13 = QtGui.QPixmap(':/Static/img/img13.png')
        lab13 = QtWidgets.QLabel()
        lab13.setPixmap(img13)

        label_a15 = QtWidgets.QLabel(
            """Al hacer esto se mostrará por cada columna una casilla de verificación correspondiente, donde el usuario podrá seleccionar las de interés a utilizar haciendo click sobre ellas (4).
Si se desea deseleccionar todas las casillas marcadas, se debe hacer click en el botón de “Desmarcar Todas” (5).
""")
        label_a15.setStyleSheet("font-size: 13px;")
        label_a15.setFixedWidth(735)
        label_a15.setWordWrap(True)

        img14 = QtGui.QPixmap(':/Static/img/img14.png')
        lab14 = QtWidgets.QLabel()
        lab14.setPixmap(img14)

        label_a16 = QtWidgets.QLabel(
            """Adicionalmente, si se desea trabajar con todas las columnas del archivo, se debe clickear sobre el botón “Seleccionar todas” (6). Al hacer esto se marcarán automáticamente todas las casillas de verificación que no estén seleccionadas (7) y no será necesario seleccionarlas una por una.""")
        label_a16.setStyleSheet("font-size: 13px;")
        label_a16.setFixedWidth(735)
        label_a16.setWordWrap(True)

        img15 = QtGui.QPixmap(':/Static/img/img15.png')
        lab15 = QtWidgets.QLabel()
        lab15.setPixmap(img15)

        label_a17 = QtWidgets.QLabel(
            """Si se desean quitar las columnas seleccionadas, se debe clickear sobre el botón “Filtrar Seleccionados” (4) en la sección (2) del punto 1.1.2 del manual.
Por otro lado, si quiere quitar las no seleccionadas se debe clickear en “Filtrar no seleccionados” (5).
Además, se pueden filtrar aquellas columnas del archivo que en su nombre contengan los caracteres (alfanuméricos) que se ingresen en la caja de texto, con el fin de filtrar rápidamente aquellas columnas que no son de interés (6).
Si se desea conservar aquellas columnas que cumplen con lo ingresado en el paso anterior, se debe desactivar la casilla de verificación llamada “Eliminar coincidencias”; de lo contrario, se debe dejar dicha casilla verificada (7).
Para que el filtro por caracteres se aplique sobre las columnas se debe clickear sobre el botón “Filtrar” (8).
Luego de realizar estos pasos, se debe clickear sobre el botón “Siguiente” para poder continuar hacia la siguiente ventana de configuración.
""")
        label_a17.setStyleSheet("font-size: 13px;")
        label_a17.setFixedWidth(735)
        label_a17.setWordWrap(True)

        img16 = QtGui.QPixmap(':/Static/img/img16.png')
        lab16 = QtWidgets.QLabel()
        lab16.setPixmap(img16)

        label_a18 = QtWidgets.QLabel(
            """Luego de realizar el paso (9), se mantendrá la sección izquierda con las columnas de archivos filtradas, como se muestra en la sección (1) del punto 1.1.2 del manual de usuario, y se mostrará una nueva sección llamada “Directorios”.
En ella, el usuario podrá crear directorios donde se contendrán las columnas que el usuario desee. Esta función es útil a la hora de organizar todas las columnas que se van a importar. Para ello, deberá crear un nuevo directorio haciendo click sobre el botón “Nuevo directorio” (10)
""")
        label_a18.setStyleSheet("font-size: 13px;")
        label_a18.setFixedWidth(735)
        label_a18.setWordWrap(True)

        img17 = QtGui.QPixmap(':/Static/img/img17.png')
        lab17 = QtWidgets.QLabel()
        lab17.setPixmap(img17)

        label_a19 = QtWidgets.QLabel(
            """Al hacer esto se desplegará la siguiente ventana, en la que se podrá escoger un nombre para el directorio a crear (11). Para finalizar, se debe clickear sobre el botón “Confirmar” (12).""")
        label_a19.setStyleSheet("font-size: 13px;")
        label_a19.setFixedWidth(735)
        label_a19.setWordWrap(True)

        img18 = QtGui.QPixmap(':/Static/img/img18.png')
        lab18 = QtWidgets.QLabel()
        lab18.setPixmap(img18)

        label_a20 = QtWidgets.QLabel(
            """Una vez que se tenga el directorio creado, se deberá agregar columnas al mismo para poder confirmar su selección. Para realizar esto, es necesario hacer click derecho sobre el directorio (13), lo cual desplegará el siguiente menú (14)""")
        label_a20.setStyleSheet("font-size: 13px;")
        label_a20.setFixedWidth(735)
        label_a20.setWordWrap(True)

        img19 = QtGui.QPixmap(':/Static/img/img19.png')
        lab19 = QtWidgets.QLabel()
        lab19.setPixmap(img19)

        img20 = QtGui.QPixmap(':/Static/img/img20.png')
        lab20 = QtWidgets.QLabel()
        lab20.setPixmap(img20)

        label_a21 = QtWidgets.QLabel(
            """En este menú se podrán realizar las siguientes acciones para agregar al directorio aquellas columnas cuyas casillas de verificación fueron seleccionadas:
    1. Importar columnas seleccionadas: al hacer click sobre esta opción se añadirán todas las columnas que se encuentren seleccionadas dentro del directorio.
    2. Importar rango de columnas: se deben seleccionar únicamente 2 casillas de verificación de la sección de columnas del archivo; luego se añadirán al directorio todas las que estén entre ese rango, incluyendo las que se eligieron.
    3. Eliminar columnas: elimina todas las columnas que se encuentren dentro del directorio.
    4. Eliminar directorio: remueve el directorio creado y todas las columnas que este contenga.
    5. Cambiar nombre: si por alguna razón se desea cambiar el nombre del directorio creado anteriormente, al hacer click sobre esta opción se muestra la siguiente pantalla donde se deberá escribir el nuevo nombre del directorio (5.1) y luego clickear sobre el botón “Confirmar” para aplicar los cambios (5.2).
""")
        label_a21.setStyleSheet("font-size: 13px;")
        label_a21.setFixedWidth(735)
        label_a21.setWordWrap(True)

        img21 = QtGui.QPixmap(':/Static/img/img21.png')
        lab21 = QtWidgets.QLabel()
        lab21.setPixmap(img21)

        label_a22 = QtWidgets.QLabel(
            """Cabe destacar que, una vez agregadas las columnas a un directorio, si se desea se pueden eliminar haciendo click derecho sobre una de ellas y luego click izquierdo en “Eliminar” (15).
""")
        label_a22.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_a22.setFixedWidth(735)
        label_a22.setWordWrap(True)

        img22 = QtGui.QPixmap(':/Static/img/img22.png')
        lab22 = QtWidgets.QLabel()
        lab22.setPixmap(img22)

        label_a23 = QtWidgets.QLabel(
            """Por último, para confirmar los cambios se deberá hacer click sobre el botón “Confirmar” (16)""")
        label_a23.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_a23.setFixedWidth(735)
        label_a23.setWordWrap(True)

        img23 = QtGui.QPixmap(':/Static/img/img23.png')
        lab23 = QtWidgets.QLabel()
        lab23.setPixmap(img23)

        label_a24 = QtWidgets.QLabel(
            """Luego de realizar todos los pasos mencionados anteriormente se mostrará en el panel de archivos .csv, ubicado en la sección izquierda de la pantalla principal, los directorios creados y las columnas que fueron insertadas en los mismos""")
        label_a24.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_a24.setFixedWidth(735)
        label_a24.setWordWrap(True)

        img24 = QtGui.QPixmap(':/Static/img/img24.png')
        lab24 = QtWidgets.QLabel()
        lab24.setPixmap(img24)

        label_a25 = QtWidgets.QLabel(
            """A continuación, se podrán graficar dichas columnas tal como se muestra en el paso 1.3 de este manual.""")
        label_a25.setStyleSheet("font-size: 13px;")
        label_a25.setFixedWidth(735)
        label_a25.setWordWrap(True)

        # 1.1.3 Eliminar archivo .csv

        label_eliminar_archivos_csv = QtWidgets.QLabel("1.1.3 Eliminar archivo .csv")
        label_eliminar_archivos_csv.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a26 = QtWidgets.QLabel(
            """Si se desea eliminar un archivo .csv se lo debe seleccionar desde la lista de .csv que se encuentran cargados en el sistema (1) y luego hacer click sobre el símbolo de papelera (2). Posteriormente se quita el archivo y este deja de estar disponible para su utilización en el software.""")
        label_a26.setStyleSheet("font-size: 13px;")
        label_a26.setFixedWidth(735)
        label_a26.setWordWrap(True)

        img25 = QtGui.QPixmap(':/Static/img/img25.png')
        lab25 = QtWidgets.QLabel()
        lab25.setPixmap(img25)

        # 1.2 MANEJO DE VISTAS

        label_manejo_vistas = QtWidgets.QLabel("1.2 Manejo de Vistas")
        label_manejo_vistas.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a27 = QtWidgets.QLabel(
            """El programa permite la creación de varias pestañas denominadas como “vistas”. En estas se mostrarán las gráficas que el usuario desee visualizar con el fin de permitirle organizarlas y dividirlas.
Para crear una nueva vista se debe clickear sobre el botón “Nueva Vista” ubicado en la barra superior de navegación en la esquina superior izquierda de la pantalla (1).
""")
        label_a27.setStyleSheet("font-size: 13px;")
        label_a27.setFixedWidth(735)
        label_a27.setWordWrap(True)

        img26 = QtGui.QPixmap(':/Static/img/img26.png')
        lab26 = QtWidgets.QLabel()
        lab26.setPixmap(img26)

        label_a28 = QtWidgets.QLabel(
            """Al clickear este botón se creará la vista nueva que originalmente se encuentra vacía debido a que aún no se le han insertado gráficas. (2)
Posteriormente, si se desea se puede eliminar esta vista pulsando sobre la cruz roja (3), lo cual hará que la misma se remueva de la sección de vistas quitando también las gráficas que estén presentes en ella, si es que cuenta con alguna.
""")
        label_a28.setStyleSheet("font-size: 13px;")
        label_a28.setFixedWidth(735)
        label_a28.setWordWrap(True)

        img27 = QtGui.QPixmap(':/Static/img/img27.png')
        lab27 = QtWidgets.QLabel()
        lab27.setPixmap(img27)

        # 1.3 GRAFICAR DATOS

        label_graficar_datos = QtWidgets.QLabel("1.3 Graficar Datos")
        label_graficar_datos.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a29 = QtWidgets.QLabel(
            """Cabe destacar que para graficar una señal electromiográfica debe haberse creado una vista previamente, tal como se muestra en la sección 1.2 de este manual.
Para graficar una señal electromiográfica se debe dirigir a la carpeta ubicada en la sección (3) de la introducción, donde se encuentra la señal que desee graficar y hacer doble click sobre ella. (1)
""")
        label_a29.setStyleSheet("font-size: 13px;")
        label_a29.setFixedWidth(735)
        label_a29.setWordWrap(True)

        img28 = QtGui.QPixmap(':/Static/img/img28.png')
        lab28 = QtWidgets.QLabel()
        lab28.setPixmap(img28)

        label_a30 = QtWidgets.QLabel(
            """Posteriormente se desplegarán todas las señales que contenga la carpeta que se abrió. (2)""")
        label_a30.setStyleSheet("font-size: 13px;")
        label_a30.setFixedWidth(735)
        label_a30.setWordWrap(True)

        img29 = QtGui.QPixmap(':/Static/img/img29.png')
        lab29 = QtWidgets.QLabel()
        lab29.setPixmap(img29)

        label_a31 = QtWidgets.QLabel(
            """Al realizar doble click sobre una de estas señales, esta se graficará automáticamente y se mostrará la gráfica correspondiente en la vista actual (3).""")
        label_a31.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_a31.setFixedWidth(735)
        label_a31.setWordWrap(True)

        img30 = QtGui.QPixmap(':/Static/img/img30.png')
        lab30 = QtWidgets.QLabel()
        lab30.setPixmap(img30)

        label_shrek = QtWidgets.QLabel(
            """Este procedimiento puede repetirse si se desea graficar varias señales EMG en la misma vista.""")
        label_shrek.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_shrek.setFixedWidth(735)
        label_shrek.setWordWrap(True)

        # 1.4 MANIPULACIÓN DE GRÁFICAS

        label_manipulacion_de_graficasxd = QtWidgets.QLabel("1.4 Manipulación de gráficas")
        label_manipulacion_de_graficasxd.setStyleSheet("font: bold 15px;margin-top:30px;")

        # 1.4.1 VALORES EN BRUTOS

        label_valores_en_brutos = QtWidgets.QLabel("1.4.1 Valores en bruto")
        label_valores_en_brutos.setStyleSheet("font: bold 13px;margin-top:4px;")

        label_a32 = QtWidgets.QLabel(
            """Cabe destacar que para aplicar valores en bruto a una señal EMG debe haberse creado una vista previamente, tal como se muestra en la sección 1.2 de este manual, y haberse graficado alguna señal, como se indica en la sección 1.3 de este manual.

Para aplicar los valores en bruto a una señal electromiográfica, es decir quitar todos los filtros con los que cuenta por defecto, se debe acceder a la barra de navegación superior haciendo click en el botón de Valores En Bruto (1).
""")
        label_a32.setStyleSheet("font-size: 13px;")
        label_a32.setFixedWidth(735)
        label_a32.setWordWrap(True)

        img31 = QtGui.QPixmap(':/Static/img/img31.png')
        lab31 = QtWidgets.QLabel()
        lab31.setPixmap(img31)

        label_a33 = QtWidgets.QLabel(
            """Posteriormente se desplegará una ventana en la cual se debe indicar el o los gráficos a los que se desean aplicar valores en bruto, haciendo click en la casilla de verificación correspondiente (1). Adicionalmente, si se desea se pueden seleccionar todas las gráficas haciendo click sobre el botón “Seleccionar todas” (2).
Por último, para guardar los cambios y actualizar la gráfica se debe dar click en aplicar (3).
""")
        label_a33.setStyleSheet("font-size: 13px;")
        label_a33.setFixedWidth(735)
        label_a33.setWordWrap(True)

        img32 = QtGui.QPixmap(':/Static/img/img32.png')
        lab32 = QtWidgets.QLabel()
        lab32.setPixmap(img32)

        # 1.4.2 VALORES EN BRUTOS

        label_rectificar_grafico = QtWidgets.QLabel("1.4.2 Rectificar gráfico")
        label_rectificar_grafico.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a34 = QtWidgets.QLabel(
            """Cabe destacar que para rectificar un gráfico debe haberse creado una vista previamente, tal como se muestra en la sección 1.2 de este manual, y haberse graficado los datos según la sección 1.3 de este manual.
Para rectificar uno o varios gráficos es necesario acceder a la barra de navegación superior haciendo click en el botón de Rectificar (1).
""")
        label_a34.setStyleSheet("font-size: 13px;")
        label_a34.setFixedWidth(735)
        label_a34.setWordWrap(True)

        img33 = QtGui.QPixmap(':/Static/img/img33.png')
        lab33 = QtWidgets.QLabel()
        lab33.setPixmap(img33)

        label_a35 = QtWidgets.QLabel(
            """Posteriormente se desplegará una ventana en la cual se debe indicar el o los gráficos que se desean rectificar haciendo click en la casilla de verificación correspondiente (2), pudiéndose seleccionar todos los gráficos existentes en la vista pulsando el botón “Seleccionar todas” (3).""")
        label_a35.setStyleSheet("font-size: 13px;")
        label_a35.setFixedWidth(735)
        label_a35.setWordWrap(True)

        img34 = QtGui.QPixmap(':/Static/img/img34.png')
        lab34 = QtWidgets.QLabel()
        lab34.setPixmap(img34)

        label_a36 = QtWidgets.QLabel(
            """Luego de esto se debe configurar desde el periodo que se van a tomar los datos, ingresando los parámetros Inicio y Fin que corresponden al tiempo en segundos de una señal (4).
Si se desea que todos los valores del gráfico sean absolutos se debe seleccionar la casilla de verificación (5).
Por último, para guardar los cambios y actualizar la o las gráficas seleccionadasse debe hacer click en aplicar (6).
""")
        label_a36.setStyleSheet("font-size: 13px;")
        label_a36.setFixedWidth(735)
        label_a36.setWordWrap(True)

        img35 = QtGui.QPixmap(':/Static/img/img35.png')
        lab35 = QtWidgets.QLabel()
        lab35.setPixmap(img35)

        # 1.4.3 APLICAR FILTROS

        label_aplicar_filtros = QtWidgets.QLabel("1.4.3 Aplicar filtros")
        label_aplicar_filtros.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a37 = QtWidgets.QLabel(
            """Cabe destacar que para aplicar filtros a una señal EMG con el objetivo de eliminar el ruido y mejorar la calidad de la misma, debe haberse creado una vista previamente, tal como se muestra en la sección 1.2 de este manual, y graficado los datos,según la sección 1.3 de este manual.
Para aplicar filtros a una o más gráficas, es necesario acceder a la barra de navegación superior y hacer click al botón Filtrado (1).
""")
        label_a37.setStyleSheet("font-size: 13px;")
        label_a37.setFixedWidth(735)
        label_a37.setWordWrap(True)

        img36 = QtGui.QPixmap(':/Static/img/img36.png')
        lab36 = QtWidgets.QLabel()
        lab36.setPixmap(img36)

        label_a38 = QtWidgets.QLabel(
            """Luego de esto se desplegará una ventana en la cual se podrán seleccionar los gráficos en los que se desee aplicar filtros haciendo click en la casilla de verificación correspondiente (2), pudiéndose seleccionar todas las gráficas existentes en la vista pulsando el botón “Seleccionar todas” (3).""")
        label_a38.setStyleSheet("font-size: 13px;")
        label_a38.setFixedWidth(735)
        label_a38.setWordWrap(True)

        img37 = QtGui.QPixmap(':/Static/img/img37.png')
        lab37 = QtWidgets.QLabel()
        lab37.setPixmap(img37)

        label_a39 = QtWidgets.QLabel(
            """Posteriormente se podrán indicar los parámetros del filtro:
    • Orden del filtro (4): describe el grado de aceptación o rechazo de frecuencias por arriba o por debajo de la respectiva
      frecuencia de corte.
    • Frecuencias críticas (5): son las frecuencias críticas indicadas en Hertz.
    • Tipo de filtro (6): entre ellos se encuentran los tipos ‘lowpass’, ‘highpass’, ‘bandpass’ y bandstop’.
    • Si es analógico o no (7): cuando el valor de la lista está en “True” (Verdadero), la gráfica se muestra en forma analógica;
      de lo contrario se muestra un filtro digital.

Para que los valores ingresados se apliquen a la/s gráfica/s, debe chequearse la casilla de verificación “Aplicar Filtro Butterworth” (8).Una vez indicados estos valores se da click en Aplicar (9).
""")
        label_a39.setStyleSheet("font-size: 13px;")
        label_a39.setFixedWidth(735)
        label_a39.setWordWrap(True)

        img38 = QtGui.QPixmap(':/Static/img/img38.png')
        lab38 = QtWidgets.QLabel()
        lab38.setPixmap(img38)

        # 1.4.4 RECORTAR GRAFICO

        label_recortar_grafico = QtWidgets.QLabel("1.4.4 Recortar gráfico")
        label_recortar_grafico.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a40 = QtWidgets.QLabel(
            """Cabe destacar que para recortar un segmento de un gráfico debe haberse creado una vista previamente, tal como se muestra en la sección 1.2 de este manual, y graficado los datos, según la sección 1.3 de este manual.
Para recortar un gráfico es necesario accederá la barra de navegación superior y hacer click en el botón Cortar (1).
 """)
        label_a40.setStyleSheet("font-size: 13px;")
        label_a40.setFixedWidth(735)
        label_a40.setWordWrap(True)

        img39 = QtGui.QPixmap(':/Static/img/img39.png')
        lab39 = QtWidgets.QLabel()
        lab39.setPixmap(img39)

        label_a41 = QtWidgets.QLabel(
            """Luego de esto se desplegará una ventana en la cual se podrán seleccionar los gráficos a recortar haciendo click en la casilla de verificación correspondiente (2), pudiéndose seleccionar todas las gráficas existentes en la vista pulsando el botón “Seleccionar todas” (3).""")
        label_a41.setStyleSheet("font-size: 13px;")
        label_a41.setFixedWidth(735)
        label_a41.setWordWrap(True)

        img40 = QtGui.QPixmap(':/Static/img/img40.png')
        lab40 = QtWidgets.QLabel()
        lab40.setPixmap(img40)

        label_a42 = QtWidgets.QLabel(
            """A continuación, se indica el tramo de la gráfica que se va a recortar, ingresando el tiempo desde donde empieza el recorte hasta el tiempo en el que finaliza (4).Una vez indicados estos valores se dará click en Aplicar (5).""")
        label_a42.setStyleSheet("font-size: 13px;")
        label_a42.setFixedWidth(735)
        label_a42.setWordWrap(True)

        img41 = QtGui.QPixmap(':/Static/img/img41.png')
        lab41 = QtWidgets.QLabel()
        lab41.setPixmap(img41)

        label_a43 = QtWidgets.QLabel(
            """Alternativamente, si se desea volver al gráfico original, es decir sin recortarlo, se debe hacer click en el botón “Resetear” (6) y posteriormente en Aplicar (7).""")
        label_a43.setStyleSheet("font-size: 13px;")
        label_a43.setFixedWidth(735)
        label_a43.setWordWrap(True)

        img42 = QtGui.QPixmap(':/Static/img/img42.png')
        lab42 = QtWidgets.QLabel()
        lab42.setPixmap(img42)

        # 1.4.5 RECORTAR HACIENDO CLICK

        label_recortar_haciendo_click = QtWidgets.QLabel("1.4.5 Recortar gráfico haciendo click")
        label_recortar_haciendo_click.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a44 = QtWidgets.QLabel(
            """Cabe destacar que para recortar un segmento de un gráfico debe haberse creado una vista previamente, tal como se muestra en la sección 1.2 de este manual, y graficado los datos, según la sección 1.3 de este manual.
Para recortar un gráfico es necesario acceder a la barra de navegación superior y hacer click en el botón Cortar (1).
""")
        label_a44.setStyleSheet("font-size: 13px;")
        label_a44.setFixedWidth(735)
        label_a44.setWordWrap(True)

        img43 = QtGui.QPixmap(':/Static/img/img43.png')
        lab43 = QtWidgets.QLabel()
        lab43.setPixmap(img43)

        label_a45 = QtWidgets.QLabel(
            """Luego de esto se desplegará una ventana en la cual se podrán seleccionar los gráficos a recortar haciendo click en la casilla de verificación correspondiente (2), pudiéndose seleccionar todas las gráficas existentes en la vista pulsando el botón “Seleccionar todas” (3).""")
        label_a45.setStyleSheet("font-size: 13px;")
        label_a45.setFixedWidth(735)
        label_a45.setWordWrap(True)

        img44 = QtGui.QPixmap(':/Static/img/img44.png')
        lab44 = QtWidgets.QLabel()
        lab44.setPixmap(img44)

        label_a46 = QtWidgets.QLabel(
            """Posteriormente es requerido hacer click sobre el botón “Recortar Haciendo Click" para continuar (4).""")
        label_a46.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_a46.setFixedWidth(735)
        label_a46.setWordWrap(True)

        img45 = QtGui.QPixmap(':/Static/img/img45.png')
        lab45 = QtWidgets.QLabel()
        lab45.setPixmap(img45)

        label_a47 = QtWidgets.QLabel(
            """A continuación, se desplegará un mensaje de información y, al hacer click en el botón “OK”, se podrá continuar con el recorte (5).""")
        label_a47.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_a47.setFixedWidth(735)
        label_a47.setWordWrap(True)

        img46 = QtGui.QPixmap(':/Static/img/img46.png')
        lab46 = QtWidgets.QLabel()
        lab46.setPixmap(img46)

        label_a48 = QtWidgets.QLabel(
            """Luego se indicará el tramo de la gráfica que se desea recortar, haciendo click sobre ella, especificando el tiempo desde donde empieza el recorte (6) hasta el tiempo en el que finaliza (7).""")
        label_a48.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_a48.setFixedWidth(735)
        label_a48.setWordWrap(True)

        img47 = QtGui.QPixmap(':/Static/img/img47.png')
        lab47 = QtWidgets.QLabel()
        lab47.setPixmap(img47)

        label_a49 = QtWidgets.QLabel(
            """Se obtendrá el siguiente resultado: una gráfica recortada que comienza desde el valor inicial indicado en el punto (6) y finaliza en el punto (7), sustituyendo la anterior""")
        label_a49.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_a49.setFixedWidth(735)
        label_a49.setWordWrap(True)

        img48 = QtGui.QPixmap(':/Static/img/img48.png')
        lab48 = QtWidgets.QLabel()
        lab48.setPixmap(img48)

        # 1.4.6 VALORES EN GRÁFICA

        label_valores_en_grafica = QtWidgets.QLabel("1.4.6 Valores en la gráfica")
        label_valores_en_grafica.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a50 = QtWidgets.QLabel(
            """Cabe destacar que para aplicar valores en gráfica de una señal EMG debe haberse creado una vista previamente, tal como se muestra en la sección 1.2 de este manual, y haber graficado los datos según la sección 1.3 de este manual.
Para aplicar los cálculos correspondientes a valores picos, integral y valor RMS en las gráficas, es necesario hacer click en el botón de “Valores en Gráfica” (1).
""")
        label_a50.setStyleSheet("font-size: 13px;")
        label_a50.setFixedWidth(735)
        label_a50.setWordWrap(True)

        img49 = QtGui.QPixmap(':/Static/img/img49.png')
        lab49 = QtWidgets.QLabel()
        lab49.setPixmap(img49)

        label_a51 = QtWidgets.QLabel(
            """Al realizar esto se desplegará una ventana con dos secciones distintas (2 y 3); una para seleccionar gráficas y otra para aplicar cálculos.""")
        label_a51.setStyleSheet("font-size: 13px;")
        label_a51.setFixedWidth(735)
        label_a51.setWordWrap(True)

        img50 = QtGui.QPixmap(':/Static/img/img50.png')
        lab50 = QtWidgets.QLabel()
        lab50.setPixmap(img50)

        label_a52 = QtWidgets.QLabel(
            """En la sección “Seleccionar gráficas” se podrán escoger los gráficos a los cuales se le aplicarán cálculos haciendo click en la casilla de verificación correspondiente (4), pudiéndose también seleccionar todas las gráficas existentes en la vista pulsando el botón “Seleccionar todas” (5).""")
        label_a52.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_a52.setFixedWidth(735)
        label_a52.setWordWrap(True)

        img51 = QtGui.QPixmap(':/Static/img/img51.png')
        #img51.scaledToHeight(200)
        lab51 = QtWidgets.QLabel()

        #lab51.setStyleSheet("background-color:red;border:1px solid blue;")
        #lab51.setFixedHeight(500)
        lab51.setPixmap(img51)

        label_a53 = QtWidgets.QLabel(
            """En la segunda sección se mostrarán los cálculos anteriormente mencionados, que se pueden aplicar a las gráficas seleccionadas (6).Cada cálculo será explicado a continuación.""")
        label_a53.setStyleSheet("font-size: 13px;margin-top:12px;")
        label_a53.setFixedWidth(735)
        label_a53.setWordWrap(True)

        img52 = QtGui.QPixmap(':/Static/img/img52.png')
        lab52 = QtWidgets.QLabel()
        lab52.setPixmap(img52)

        # 1.4.6.1 CALCULAR Y MOSTRAR VALORES PICOS

        label_valores_picos = QtWidgets.QLabel("1.4.6.1 Calcular y mostrar valores picos")
        label_valores_picos.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a54 = QtWidgets.QLabel(
            """Para mostrar los valores pico de las gráficas seleccionadas se deberá de acceder a la pestaña “Valores picos" (1).
Luego es necesario indicar la altura mínima (2), el umbral (3) y la distancia (4).
Para que los valores ingresados se apliquen a la/s gráfica/s, es requerido chequear la casilla de verificación “Mostrar picos” (5). Por último, se debe clickear en el botón “Aplicar” (6).
""")
        label_a54.setStyleSheet("font-size: 13px;")
        label_a54.setFixedWidth(735)
        label_a54.setWordWrap(True)

        img53 = QtGui.QPixmap(':/Static/img/img53.png')
        lab53 = QtWidgets.QLabel()
        lab53.setPixmap(img53)

        label_a55 = QtWidgets.QLabel(
            """Luego de esto se visualizarán en la o las gráficas seleccionadas sus valores picos, marcados con un círculo en rojo tal como se muestra en la imagen a continuación.""")
        label_a55.setStyleSheet("font-size: 13px;")
        label_a55.setFixedWidth(735)
        label_a55.setWordWrap(True)

        img54 = QtGui.QPixmap(':/Static/img/img54.png')
        lab54 = QtWidgets.QLabel()
        lab54.setPixmap(img54)

        # 1.4.6.2 CALCULAR Y MOSTRAR INTEGRAL

        label_valores_de_integral = QtWidgets.QLabel("1.4.6.2 Calcular y mostrar integral")
        label_valores_de_integral.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a56 = QtWidgets.QLabel(
            """Para mostrar la integral de las gráficas seleccionadas se deberá clickear sobre la pestaña “Integral” (1). A continuación es necesario indicar el valor inicial y el valor final (2).
Para que los valores ingresados se apliquen a la/s gráfica/s, se requiere chequear la casilla de verificación “Mostrar Integral” (3) y por último clickear en el botón “Aplicar” (4).
""")
        label_a56.setStyleSheet("font-size: 13px;")
        label_a56.setFixedWidth(735)
        label_a56.setWordWrap(True)

        img55 = QtGui.QPixmap(':/Static/img/img55.png')
        lab55 = QtWidgets.QLabel()
        lab55.setPixmap(img55)

        # 1.4.6.3 CALCULAR Y MOSTRAR INTEGRAL haciendo clicki

        label_valores_de_integral_clicki = QtWidgets.QLabel("1.4.6.3 Calcular y mostrar integral haciendo click")
        label_valores_de_integral_clicki.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a57 = QtWidgets.QLabel(
            """Para mostrar la integral de las gráficas seleccionadas se deberá clickear sobre la pestaña “Integral” (1).Luego es necesario clickear sobre el botón “Indicar haciendo click” (2).""")
        label_a57.setStyleSheet("font-size: 13px;")
        label_a57.setFixedWidth(735)
        label_a57.setWordWrap(True)

        img56 = QtGui.QPixmap(':/Static/img/img56.png')
        lab56 = QtWidgets.QLabel()
        lab56.setPixmap(img56)

        label_a58 = QtWidgets.QLabel(
            """A continuación se desplegará un mensaje de información y, al hacer click en el botón “OK”, se podrá continuar con el cálculo de la integral (3).""")
        label_a58.setStyleSheet("font-size: 13px;")
        label_a58.setFixedWidth(735)
        label_a58.setWordWrap(True)

        img57 = QtGui.QPixmap(':/Static/img/img57.png')
        lab57 = QtWidgets.QLabel()
        lab57.setPixmap(img57)

        label_a59 = QtWidgets.QLabel(
            """Por último, se indicará el tramo de la gráfica al que se le desea calcular la integral haciendo click sobre ella e indicando el tiempo desde donde empieza (4) hasta el tiempo en el que finaliza (5).""")
        label_a59.setStyleSheet("font-size: 13px;")
        label_a59.setFixedWidth(735)
        label_a59.setWordWrap(True)

        img58 = QtGui.QPixmap(':/Static/img/img58.png')
        lab58 = QtWidgets.QLabel()
        lab58.setPixmap(img58)

        label_a60 = QtWidgets.QLabel(
            """Luego de realizar todos los pasos mencionados anteriormente se mostrará en la o las gráficas seleccionadas el siguiente resultado, indicando el valor de la integral y su área coloreada en verde.""")
        label_a60.setStyleSheet("font-size: 13px;")
        label_a60.setFixedWidth(735)
        label_a60.setWordWrap(True)

        img59 = QtGui.QPixmap(':/Static/img/img59.png')
        lab59 = QtWidgets.QLabel()
        lab59.setPixmap(img59)

        # 1.4.6.4 CALCULAR Y MOSTRAR valor RMS

        label_valores_rms = QtWidgets.QLabel("1.4.6.4 Calcular y mostrar valor RMS")
        label_valores_rms.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a61 = QtWidgets.QLabel(
            """Para mostrar el valor RMS de la o las gráficas seleccionadas se deberá clickear sobre la pestaña “valor RMS” (1). Luego es necesario indicar el valor inicial y el valor final (2).
Para que los valores ingresados se apliquen a la/s gráfica/s se requiere chequear la casilla de verificación “Mostrar Valor RMS” (3) y por último clickear en el botón “Aplicar” (4).
""")
        label_a61.setStyleSheet("font-size: 13px;")
        label_a61.setFixedWidth(735)
        label_a61.setWordWrap(True)

        img60 = QtGui.QPixmap(':/Static/img/img60.png')
        lab60 = QtWidgets.QLabel()
        lab60.setPixmap(img60)

        label_a62 = QtWidgets.QLabel(
            """Luego de realizar todos los pasos mencionados anteriormente se mostrará en las gráficas seleccionadas el siguiente resultado indicando su valor RMS, marcado en un rectángulo gris.""")
        label_a62.setStyleSheet("font-size: 13px;")
        label_a62.setFixedWidth(735)
        label_a62.setWordWrap(True)

        img61 = QtGui.QPixmap(':/Static/img/img61.png')
        lab61 = QtWidgets.QLabel()
        lab61.setPixmap(img61)

        # 1.4.7 Comparar

        label_comparar = QtWidgets.QLabel("1.4.7 Comparar")
        label_comparar.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a63 = QtWidgets.QLabel(
            """Una vez teniendo disponibles dos o más gráficas en pantalla en una misma vista se las puede comparar haciendo click en el botón “Comparar gráficas”, situado en la barra superior de navegación (1).""")
        label_a63.setStyleSheet("font-size: 13px;")
        label_a63.setFixedWidth(735)
        label_a63.setWordWrap(True)

        img62 = QtGui.QPixmap(':/Static/img/img62.png')
        lab62 = QtWidgets.QLabel()
        lab62.setPixmap(img62)

        label_a64 = QtWidgets.QLabel(
            """A continuación, se deberán seleccionar al menos dos de las señales graficadas (2) o, si se desea, se pueden elegir todas las gráficas existentes en la vista pulsando sobre el botón “Seleccionar todas” (3). Por último, se debe clickear sobre el botón “Aplicar” """)
        label_a64.setStyleSheet("font-size: 13px;")
        label_a64.setFixedWidth(735)
        label_a64.setWordWrap(True)

        img63 = QtGui.QPixmap(':/Static/img/img63.png')
        lab63 = QtWidgets.QLabel()
        lab63.setPixmap(img63)

        label_a65 = QtWidgets.QLabel(
            """Esto mostrará las dos señales en una misma gráfica con distintos colores aleatorios para poder compararlas (5).""")
        label_a65.setStyleSheet("font-size: 13px;")
        label_a65.setFixedWidth(735)
        label_a65.setWordWrap(True)

        img64 = QtGui.QPixmap(':/Static/img/img64.png')
        lab64 = QtWidgets.QLabel()
        lab64.setPixmap(img64)

        # 1.4.8 eliminar gráfica

        label_eliminar_grafica = QtWidgets.QLabel("1.4.8 Eliminar gráfica")
        label_eliminar_grafica.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a66 = QtWidgets.QLabel(
            """Una vez que se tenga una vista creada (ver sección 1.2 de este manual) y al menos una gráfica en la misma (ver sección 1.3), en el panel inferior izquierdo se mostrará la vista y su/s gráfica/s correspondiente/s (1).""")
        label_a66.setStyleSheet("font-size: 13px;")
        label_a66.setFixedWidth(735)
        label_a66.setWordWrap(True)

        img65 = QtGui.QPixmap(':/Static/img/img65.png')
        lab65 = QtWidgets.QLabel()
        lab65.setPixmap(img65)

        label_a67 = QtWidgets.QLabel(
            """Luego se debe hacer click derecho en el botón sobre la señal graficada en la vista (2) y por último click izquierdo sobre “Remover gráfica” (3).""")
        label_a67.setStyleSheet("font-size: 13px;")
        label_a67.setFixedWidth(735)
        label_a67.setWordWrap(True)

        img66 = QtGui.QPixmap(':/Static/img/img66.png')
        lab66 = QtWidgets.QLabel()
        lab66.setPixmap(img66)

        label_final_boss = QtWidgets.QLabel(
            """Esto quitará la gráfica de la vista, pero mantendrá las demás gráficas, si es que existen.""")
        label_final_boss.setStyleSheet("font-size: 13px;")
        label_final_boss.setFixedWidth(735)
        label_final_boss.setWordWrap(True)

        # 1.4.9 PANEL SUPERIOR DEL GRAFICO

        label_panel_superior = QtWidgets.QLabel("1.4.9 Panel superior del gráfico")
        label_panel_superior.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a68 = QtWidgets.QLabel(
            """Una vez que se tenga una vista creada (ver sección 1.2 de este manual) y al menos una gráfica en la misma (ver sección 1.3), en la parte superior de la gráfica se mostrarán las siguientes opciones que permitirán interactuar con la misma.""")
        label_a68.setStyleSheet("font-size: 13px;")
        label_a68.setFixedWidth(735)
        label_a68.setWordWrap(True)

        img67 = QtGui.QPixmap(':/Static/img/img67.png')
        lab67 = QtWidgets.QLabel()
        lab67.setPixmap(img67)

        label_a69 = QtWidgets.QLabel(
            """Referencias de la imagen:
    • (1) Esta opción permite volver a la posición original del gráfico si se movió anteriormente con los botones indicados (4) y
       (5).
    • (2 y 3) Estas opciones permiten retroceder y avanzar los movimientos que se realizaron sobre el gráfico, dependiendo de si
       se movió o se hizo zoom utilizando los botones del punto 4 y 5.
    • (4) Haciendo click en esta herramienta y arrastrando el mouse, el usuario se puede desplazar a través de la gráfica.
    • (5) Con esta herramienta se permite seleccionar un área determinada y hacerle zoom. Esto se realiza haciendo click
       y arrastrando el mouse en una gráfica.
    • (6) Esta herramienta despliega una ventana que permite configurar los márgenes (6.1) y el espaciado (6.2) de cada
       gráfico. Adicionalmente posibilita ajustar el gráfico a la ventana actual (6.3).
""")
        label_a69.setStyleSheet("font-size: 13px;")
        label_a69.setFixedWidth(735)
        label_a69.setWordWrap(True)

        img68 = QtGui.QPixmap(':/Static/img/img68.png')
        lab68 = QtWidgets.QLabel()
        lab68.setPixmap(img68)

        label_a70 = QtWidgets.QLabel(
            """• Haciendo click en esta herramienta, si se tiene más de un gráfico en la vista actual se desplegará la siguiente ventana en la cual se debe elegir cuál de ellos se desea modificar.""")
        label_a70.setStyleSheet("font-size: 13px;")
        label_a70.setFixedWidth(735)
        label_a70.setWordWrap(True)

        img69 = QtGui.QPixmap(':/Static/img/img69.png')
        lab69 = QtWidgets.QLabel()
        lab69.setPixmap(img69)

        label_a71 = QtWidgets.QLabel(
            """En caso contrario, o luego de haber seleccionado una gráfica, se desplegará una ventana que contiene dos secciones distintas.
La sección de “Axes” permite cambiar el título de dicha gráfica o insertar uno si no lo tiene (7.1), modificar la posición de los ejes (7.2) y actualizar el nombre de cada uno de estos (7.3).
Por último, para aplicar los cambios se debe hacer click sobre el botón “Apply” (7.4).
""")
        label_a71.setStyleSheet("font-size: 13px;")
        label_a71.setFixedWidth(735)
        label_a71.setWordWrap(True)

        img70 = QtGui.QPixmap(':/Static/img/img70.png')
        lab70 = QtWidgets.QLabel()
        lab70.setPixmap(img70)

        label_a72 = QtWidgets.QLabel(
            """Por otra parte, en la sección de “Curves” se pueden cambiar la leyenda de la gráfica (7.5), su estilo (7.6), su grosor (7.7), sus colores (7.8) y el tamaño de los puntos que la forman (7.9).""")
        label_a72.setStyleSheet("font-size: 13px;")
        label_a72.setFixedWidth(735)
        label_a72.setWordWrap(True)

        img71 = QtGui.QPixmap(':/Static/img/img71.png')
        lab71 = QtWidgets.QLabel()
        lab71.setPixmap(img71)

        label_a73 = QtWidgets.QLabel(
            """• (8) Esta opción despliega una ventana que permite guardar todos los gráficos de una vista en el formato que se seleccione, como por ejemplo .png, .jpg, .pdf, etc. (8.1).""")
        label_a73.setStyleSheet("font-size: 13px;")
        label_a73.setFixedWidth(735)
        label_a73.setWordWrap(True)

        img72 = QtGui.QPixmap(':/Static/img/img72.png')
        lab72 = QtWidgets.QLabel()
        lab72.setPixmap(img72)

        label_a74 = QtWidgets.QLabel(
            """Una vez que se elige el nombre y el formato deseado, se debe hacer click en Guardar. (8.2)""")
        label_a74.setStyleSheet("font-size: 13px;")
        label_a74.setFixedWidth(735)
        label_a74.setWordWrap(True)

        img73 = QtGui.QPixmap(':/Static/img/img73.png')
        lab73 = QtWidgets.QLabel()
        lab73.setPixmap(img73)

        # 1.5 SECCION DE CONFIGURACIONES DEL PROGRAMA

        label_configuraciones_programa = QtWidgets.QLabel("1.5 Sección de configuración del programa")
        label_configuraciones_programa.setStyleSheet("font: bold 15px;margin-top:30px;")

        # 1.5.1 CONFIGURACIONES DEL ARCHIVO

        label_configuraciones_archivo = QtWidgets.QLabel("1.5.1 Configuración de archivos")
        label_configuraciones_archivo.setStyleSheet("font: bold 13px;margin-top:15px;")

        label_a75 = QtWidgets.QLabel(
            """Para configurar la línea desde la cual el software comenzará a leer los datos de los archivos .csv se debe clickear en la barra superior en el menú “Configuración” (1) y luego en la opción “Archivos” (2).""")
        label_a75.setStyleSheet("font-size: 13px;")
        label_a75.setFixedWidth(735)
        label_a75.setWordWrap(True)

        img74 = QtGui.QPixmap(':/Static/img/img74.png')
        lab74 = QtWidgets.QLabel()
        lab74.setPixmap(img74)

        label_a76 = QtWidgets.QLabel(
            """Posteriormente se desplegará una ventana en la cual es necesario indicar la línea deseada (3) y luego clickear en “Aplicar” (4).""")
        label_a76.setStyleSheet("font-size: 13px;")
        label_a76.setFixedWidth(735)
        label_a76.setWordWrap(True)

        img75 = QtGui.QPixmap(':/Static/img/img75.png')
        lab75 = QtWidgets.QLabel()
        lab75.setPixmap(img75)

        # 1.5.2 CONFIGURACIONES LIMITE DE GRÁFICAS

        label_configuraciones_limite_grafica = QtWidgets.QLabel("1.5.2 Configuración de límite de gráficas")
        label_configuraciones_limite_grafica.setStyleSheet("font: bold 13px;margin-top:30px;")

        label_a77 = QtWidgets.QLabel(
            """Para configurar el límite de gráficas de una vista se debe clickear en la barra superior en el menú “Configuración” (1) y luego hacer click en la opción “Límite gráficas” (2).""")
        label_a77.setStyleSheet("font-size: 13px;")
        label_a77.setFixedWidth(735)
        label_a77.setWordWrap(True)

        img76 = QtGui.QPixmap(':/Static/img/img76.png')
        lab76 = QtWidgets.QLabel()
        lab76.setPixmap(img76)

        label_a78 = QtWidgets.QLabel(
            """Posteriormente se desplegará una ventana en la cual se requiere indicar la cantidad máxima de gráficas y luego click en “Aplicar” (4).""")
        label_a78.setStyleSheet("font-size: 13px;")
        label_a78.setFixedWidth(735)
        label_a78.setWordWrap(True)

        img77 = QtGui.QPixmap(':/Static/img/img77.png')
        lab77 = QtWidgets.QLabel()
        lab77.setPixmap(img77)

        # 1.6 EXPORTAR DATOS

        label_exportar_datos = QtWidgets.QLabel("1.6 Exportar datos")
        label_exportar_datos.setStyleSheet("font: bold 15px;margin-top:30px;")

        label_a80 = QtWidgets.QLabel(
            """Una vez que se tenga una vista creada y al menos una gráfica en la misma, con uno o más filtros aplicados (valores pico, integral o RMS promedio) (1), haciendo click en el botón “Exportar datos” situado en la barra superior de navegación (2), se podrán exportar estos filtros a un archivo .csv.""")
        label_a80.setStyleSheet("font-size: 13px;")
        label_a80.setFixedWidth(735)
        label_a80.setWordWrap(True)

        img79 = QtGui.QPixmap(':/Static/img/img79.png')
        lab79 = QtWidgets.QLabel()
        lab79.setPixmap(img79)

        label_a81 = QtWidgets.QLabel(
            """Para ello es necesario seleccionar las gráficas a las cuales se deseen exportar sus filtros (3) o bien clickear sobre el botón “Seleccionar todas” (4). Por último se debe hacer click en Aplicar (5).""")
        label_a81.setStyleSheet("font-size: 13px;")
        label_a81.setFixedWidth(735)
        label_a81.setWordWrap(True)

        img80 = QtGui.QPixmap(':/Static/img/img80.png')
        lab80 = QtWidgets.QLabel()
        lab80.setPixmap(img80)

        label_a82 = QtWidgets.QLabel(
            """Se podrá especificar en qué carpeta se guardará este archivo situándose sobre ella (6). Posteriormente se requiere ingresar el nombre del archivo que se va a guardar (7).
Por último, se deberá clickear sobre el botón “Guardar” para guardarlo.
""")
        label_a82.setStyleSheet("font-size: 13px;")
        label_a82.setFixedWidth(735)
        label_a82.setWordWrap(True)

        img81 = QtGui.QPixmap(':/Static/img/img81.png')
        lab81 = QtWidgets.QLabel()
        lab81.setPixmap(img81)

        label_a83 = QtWidgets.QLabel(
            """Al acceder al mismo archivo exportado se podrán ver los datos correspondientes a cada filtro aplicado. (8)""")
        label_a83.setStyleSheet("font-size: 13px;")
        label_a83.setFixedWidth(735)
        label_a83.setWordWrap(True)

        img82 = QtGui.QPixmap(':/Static/img/img82.png')
        lab82 = QtWidgets.QLabel()
        lab82.setPixmap(img82)

        widget_introduccion.layout().addWidget(label_introduccion)
        widget_introduccion.layout().addWidget(label_texto_introduccion)
        widget_introduccion.layout().addWidget(lab0)
        widget_introduccion.layout().addWidget(label_a1)
        widget_introduccion.layout().addWidget(lab2)
        widget_introduccion.layout().addWidget(label_a3)
        widget_introduccion.layout().addWidget(lab3)
        widget_introduccion.layout().addWidget(label_a4)
        widget_introduccion.layout().addWidget(lab4)
        widget_introduccion.layout().addWidget(label_a5)
        widget_introduccion.layout().addWidget(lab5)
        widget_introduccion.layout().addWidget(label_a6)
        widget_introduccion.layout().addWidget(lab6)
        widget_introduccion.layout().addWidget(label_manipular_archivos_csv)
        widget_introduccion.layout().addWidget(label_a7)
        widget_introduccion.layout().addWidget(label_importar_archivos_csv)
        widget_introduccion.layout().addWidget(label_a8)
        widget_introduccion.layout().addWidget(lab7)
        widget_introduccion.layout().addWidget(label_a9)
        widget_introduccion.layout().addWidget(lab8)
        widget_introduccion.layout().addWidget(label_a10)
        widget_introduccion.layout().addWidget(lab9)
        widget_introduccion.layout().addWidget(label_a11)
        widget_introduccion.layout().addWidget(lab10)
        widget_introduccion.layout().addWidget(label_importar_archivos_csv_diferentes)
        widget_introduccion.layout().addWidget(label_a12)
        widget_introduccion.layout().addWidget(lab11)
        widget_introduccion.layout().addWidget(label_a13)
        widget_introduccion.layout().addWidget(lab12)
        widget_introduccion.layout().addWidget(label_a14)
        widget_introduccion.layout().addWidget(lab13)
        widget_introduccion.layout().addWidget(label_a15)
        widget_introduccion.layout().addWidget(lab14)
        widget_introduccion.layout().addWidget(label_a16)
        widget_introduccion.layout().addWidget(lab15)
        widget_introduccion.layout().addWidget(label_a17)
        widget_introduccion.layout().addWidget(lab16)
        widget_introduccion.layout().addWidget(label_a18)
        widget_introduccion.layout().addWidget(lab17)
        widget_introduccion.layout().addWidget(label_a19)
        widget_introduccion.layout().addWidget(lab18)
        widget_introduccion.layout().addWidget(label_a20)
        widget_introduccion.layout().addWidget(lab19)
        widget_introduccion.layout().addWidget(lab20)
        widget_introduccion.layout().addWidget(label_a21)
        widget_introduccion.layout().addWidget(lab21)
        widget_introduccion.layout().addWidget(label_a22)
        widget_introduccion.layout().addWidget(lab22)
        widget_introduccion.layout().addWidget(label_a23)
        widget_introduccion.layout().addWidget(lab23)
        widget_introduccion.layout().addWidget(label_a24)
        widget_introduccion.layout().addWidget(lab24)
        widget_introduccion.layout().addWidget(label_a25)
        widget_introduccion.layout().addWidget(label_eliminar_archivos_csv)
        widget_introduccion.layout().addWidget(label_a26)
        widget_introduccion.layout().addWidget(lab25)
        widget_introduccion.layout().addWidget(label_manejo_vistas)
        widget_introduccion.layout().addWidget(label_a27)
        widget_introduccion.layout().addWidget(lab26)
        widget_introduccion.layout().addWidget(label_a28)
        widget_introduccion.layout().addWidget(lab27)
        widget_introduccion.layout().addWidget(label_graficar_datos)
        widget_introduccion.layout().addWidget(label_a29)
        widget_introduccion.layout().addWidget(lab28)
        widget_introduccion.layout().addWidget(label_a30)
        widget_introduccion.layout().addWidget(lab29)
        widget_introduccion.layout().addWidget(label_a31)
        widget_introduccion.layout().addWidget(lab30)
        widget_introduccion.layout().addWidget(label_shrek)
        widget_introduccion.layout().addWidget(label_manipulacion_de_graficasxd)
        widget_introduccion.layout().addWidget(label_valores_en_brutos)
        widget_introduccion.layout().addWidget(label_a32)
        widget_introduccion.layout().addWidget(lab31)
        widget_introduccion.layout().addWidget(label_a33)
        widget_introduccion.layout().addWidget(lab32)
        widget_introduccion.layout().addWidget(label_rectificar_grafico)
        widget_introduccion.layout().addWidget(label_a34)
        widget_introduccion.layout().addWidget(lab33)
        widget_introduccion.layout().addWidget(label_a35)
        widget_introduccion.layout().addWidget(lab34)
        widget_introduccion.layout().addWidget(label_a36)
        widget_introduccion.layout().addWidget(lab35)
        widget_introduccion.layout().addWidget(label_aplicar_filtros)
        widget_introduccion.layout().addWidget(label_a37)
        widget_introduccion.layout().addWidget(lab36)
        widget_introduccion.layout().addWidget(label_a38)
        widget_introduccion.layout().addWidget(lab37)
        widget_introduccion.layout().addWidget(label_a39)
        widget_introduccion.layout().addWidget(lab38)
        widget_introduccion.layout().addWidget(label_recortar_grafico)
        widget_introduccion.layout().addWidget(label_a40)
        widget_introduccion.layout().addWidget(lab39)
        widget_introduccion.layout().addWidget(label_a41)
        widget_introduccion.layout().addWidget(lab40)
        widget_introduccion.layout().addWidget(label_a42)
        widget_introduccion.layout().addWidget(lab41)
        widget_introduccion.layout().addWidget(label_a43)
        widget_introduccion.layout().addWidget(lab42)
        widget_introduccion.layout().addWidget(label_recortar_haciendo_click)
        widget_introduccion.layout().addWidget(label_a44)
        widget_introduccion.layout().addWidget(lab43)
        widget_introduccion.layout().addWidget(label_a45)
        widget_introduccion.layout().addWidget(lab44)
        widget_introduccion.layout().addWidget(label_a46)
        widget_introduccion.layout().addWidget(lab45)
        widget_introduccion.layout().addWidget(label_a47)
        widget_introduccion.layout().addWidget(lab46)
        widget_introduccion.layout().addWidget(label_a48)
        widget_introduccion.layout().addWidget(lab47)
        widget_introduccion.layout().addWidget(label_a49)
        widget_introduccion.layout().addWidget(lab48)
        widget_introduccion.layout().addWidget(label_valores_en_grafica)
        widget_introduccion.layout().addWidget(label_a50)
        widget_introduccion.layout().addWidget(lab49)
        widget_introduccion.layout().addWidget(label_a51)
        widget_introduccion.layout().addWidget(lab50)
        widget_introduccion.layout().addWidget(label_a52)
        widget_introduccion.layout().addWidget(lab51)
        widget_introduccion.layout().addWidget(label_a53)
        widget_introduccion.layout().addWidget(lab52)
        widget_introduccion.layout().addWidget(label_valores_picos)
        widget_introduccion.layout().addWidget(label_a54)
        widget_introduccion.layout().addWidget(lab53)
        widget_introduccion.layout().addWidget(label_a55)
        widget_introduccion.layout().addWidget(lab54)

        # EMPIEZO A PONER EN OTRO WIDGET XQ SINO SE DEFORMA LA ALTURA DE LAS IMAGENES X ALGUNA RAZÓN xd
        widget_introduccion2.layout().addWidget(label_valores_de_integral)
        widget_introduccion2.layout().addWidget(label_a56)
        widget_introduccion2.layout().addWidget(lab55)
        widget_introduccion2.layout().addWidget(label_valores_de_integral_clicki)
        widget_introduccion2.layout().addWidget(label_a57)
        widget_introduccion2.layout().addWidget(lab56)
        widget_introduccion2.layout().addWidget(label_a58)
        widget_introduccion2.layout().addWidget(lab57)
        widget_introduccion2.layout().addWidget(label_a59)
        widget_introduccion2.layout().addWidget(lab58)
        widget_introduccion2.layout().addWidget(label_a60)
        widget_introduccion2.layout().addWidget(lab59)
        widget_introduccion2.layout().addWidget(label_valores_rms)
        widget_introduccion2.layout().addWidget(label_a61)
        widget_introduccion2.layout().addWidget(lab60)
        widget_introduccion2.layout().addWidget(label_a62)
        widget_introduccion2.layout().addWidget(lab61)
        widget_introduccion2.layout().addWidget(label_comparar)
        widget_introduccion2.layout().addWidget(label_a63)
        widget_introduccion2.layout().addWidget(lab62)
        widget_introduccion2.layout().addWidget(label_a64)
        widget_introduccion2.layout().addWidget(lab63)
        widget_introduccion2.layout().addWidget(label_a65)
        widget_introduccion2.layout().addWidget(lab64)
        widget_introduccion2.layout().addWidget(label_eliminar_grafica)
        widget_introduccion2.layout().addWidget(label_a66)
        widget_introduccion2.layout().addWidget(lab65)
        widget_introduccion2.layout().addWidget(label_a67)
        widget_introduccion2.layout().addWidget(lab66)
        widget_introduccion2.layout().addWidget(label_final_boss)
        widget_introduccion2.layout().addWidget(label_panel_superior)
        widget_introduccion2.layout().addWidget(label_a68)
        widget_introduccion2.layout().addWidget(lab67)
        widget_introduccion2.layout().addWidget(label_a69)
        widget_introduccion2.layout().addWidget(lab68)
        widget_introduccion2.layout().addWidget(label_a70)
        widget_introduccion2.layout().addWidget(lab69)
        widget_introduccion2.layout().addWidget(label_a71)
        widget_introduccion2.layout().addWidget(lab70)
        widget_introduccion2.layout().addWidget(label_a72)
        widget_introduccion2.layout().addWidget(lab71)
        widget_introduccion2.layout().addWidget(label_a73)
        widget_introduccion2.layout().addWidget(lab72)
        widget_introduccion2.layout().addWidget(label_a74)
        widget_introduccion2.layout().addWidget(lab73)
        widget_introduccion2.layout().addWidget(label_configuraciones_programa)
        widget_introduccion2.layout().addWidget(label_configuraciones_archivo)
        widget_introduccion2.layout().addWidget(label_a75)
        widget_introduccion2.layout().addWidget(lab74)
        widget_introduccion2.layout().addWidget(label_a76)
        widget_introduccion2.layout().addWidget(lab75)
        widget_introduccion2.layout().addWidget(label_configuraciones_limite_grafica)
        widget_introduccion2.layout().addWidget(label_a77)
        widget_introduccion2.layout().addWidget(lab76)
        widget_introduccion2.layout().addWidget(label_a78)
        widget_introduccion2.layout().addWidget(lab77)
        widget_introduccion2.layout().addWidget(label_exportar_datos)
        widget_introduccion2.layout().addWidget(label_a80)
        widget_introduccion2.layout().addWidget(lab79)
        widget_introduccion2.layout().addWidget(label_a81)
        widget_introduccion2.layout().addWidget(lab80)
        widget_introduccion2.layout().addWidget(label_a82)
        widget_introduccion2.layout().addWidget(lab81)
        widget_introduccion2.layout().addWidget(label_a83)
        widget_introduccion2.layout().addWidget(lab82)


        #AGREGANDO CAPITULOS
        layout_wid_derecha.addWidget(widget_introduccion)
        layout_wid_derecha.addWidget(widget_introduccion2)


        #WIDGET SCROLL
        self.scroll.setWidget(wid_derecha)
        self.layout().addWidget(self.scroll, 7)

        widget_scroll = QtWidgets.QWidget()

        self.scroll.widget().scroll(200, 200)

    def inicio(self):
        self.scroll.verticalScrollBar().setValue(0)

    def manipular_csv(self):
        self.scroll.verticalScrollBar().setValue(2050)

    def importar_csv(self):
        self.scroll.verticalScrollBar().setValue(2150)

    def importar_csv_diferente(self):
        self.scroll.verticalScrollBar().setValue(3680)

    def eliminar_archivo(self):
        self.scroll.verticalScrollBar().setValue(9660)

    def manejo_vistas(self):
        self.scroll.verticalScrollBar().setValue(10130)

    def graficar_datos(self):
        self.scroll.verticalScrollBar().setValue(11000)

    def manipulacion_de_graficas(self):
        self.scroll.verticalScrollBar().setValue(12180)

    def valores_en_bruto(self):
        self.scroll.verticalScrollBar().setValue(12210)

    def rectificar_grafico(self):
        self.scroll.verticalScrollBar().setValue(12920)

    def aplicar_filtros(self):
        self.scroll.verticalScrollBar().setValue(14210)

    def recortar_grafico(self):
        self.scroll.verticalScrollBar().setValue(15550)

    def recortar_haciendo_click(self):
        self.scroll.verticalScrollBar().setValue(17120)

    def valores_en_grafica(self):
        self.scroll.verticalScrollBar().setValue(19400)

    def valores_picos(self):
        self.scroll.verticalScrollBar().setValue(20640)

    def valores_integral(self):
        self.scroll.verticalScrollBar().setValue(21460)

    def valores_integral_clicki(self):
        self.scroll.verticalScrollBar().setValue(21980)

    def valores_rms(self):
        self.scroll.verticalScrollBar().setValue(23290)

    def comparar(self):
        self.scroll.verticalScrollBar().setValue(24090)

    def eliminar_grafica(self):
        self.scroll.verticalScrollBar().setValue(25050)

    def panel_superior(self):
        self.scroll.verticalScrollBar().setValue(25740)

    def seccion_configuraciones(self):
        self.scroll.verticalScrollBar().setValue(28640)

    def configuraciones_archivos(self):
        self.scroll.verticalScrollBar().setValue(28685)

    def configuraciones_limites_graficas(self):
        self.scroll.verticalScrollBar().setValue(29160)

    def exportar_datos(self):
        self.scroll.verticalScrollBar().setValue(29710)

class acerca_de(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(acerca_de, self).__init__()

        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Acerca de")
        self.setFixedSize(720, 500)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setSpacing(0)

        label = QtWidgets.QLabel()
        img_paso_1 = QtGui.QPixmap(':/Static/img/splashscreenLibiam2.jpg')
        label.setPixmap(img_paso_1)


        self.layout().addWidget(label)
