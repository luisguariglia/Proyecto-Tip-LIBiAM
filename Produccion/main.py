import numpy
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import (QLabel, QMessageBox, QDesktopWidget,QGraphicsDropShadowEffect, QMenuBar,QFileDialog,QWidget,QAction, QGraphicsScene, QGraphicsView ,QTreeWidget, QToolBar, QMenu,QComboBox, QTreeWidgetItem, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, QScrollArea)
from PyQt5.QtGui import QIcon, QFont, QFontDatabase,QGuiApplication, QPixmap, QScreen
from PyQt5.QtCore import QSize, QEvent,QEventLoop,Qt,pyqtSignal,QPoint,QEasingCurve,QPropertyAnimation,QDir
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMessageBox
import shutil
import numpy as np
import pandas
import os
import config
import funciones
import sys
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import MultipleLocator
from scipy.signal import find_peaks
from ConfigVentanas.butterConfig import butterConfigClass
from ConfigVentanas.ValoresEnGrafica import valoresEnGraficaClass
from Helpers import filtersHelper
from Static.Strings import strings
from Static.styles import estilos
from Modelo.Vista import Vista
from Modelo.Archivo import Archivo
from Modelo.Grafica import Grafica
from Modelo.Pico import Pico
from GUI.GUI import ventana_valoresEnBruto,ventana_filtro,ventana_verayuda_antes_columnas, ventana_conf_vistas, ventana_exportarVP, ventana_cortar, ventana_rectificar,ventana_valores_en_graficas,ventana_comparar, ventana_conf_archivos, ventana_conf_linea_archivo
from matplotlib.patches import Polygon
import scipy
import csv
import img
import configparser
import time
from PyQt5.QtWidgets import QSplashScreen
import re

cant_graficas = 0
##       esto es para el cortar
cont = 0
min=0
max=0
cortando=False
cortandoVarios=False
ventanaCortarInstance= None
listaDeAxes = []
graficaActual = None
##

def load_fonts_from_dir(directory):
    families = set()
    for fi in QDir(directory).entryInfoList(["*.ttf"]):
        _id = QFontDatabase.addApplicationFont(fi.absoluteFilePath())
        families |= set(QFontDatabase.applicationFontFamilies(_id))
    return families


class tree_widget_item_grafica(QTreeWidgetItem):
    def __init__(self,text,id):
        super(tree_widget_item_grafica, self).__init__()
        self.setText(0,text)
        self.id = id

    def get_id(self):
        return self.id

    def set_id(self,id):
        self.id = id


class tree_widget_item_vista(QTreeWidgetItem):
    def __init__(self,text,name):
        super(tree_widget_item_vista, self).__init__()
        self.setText(0,text)
        self.name = name

    def get_name_object(self):
        return self.name

    def set_name_object(self,name):
        self.name = name


class ventana_principal(QWidget):

    def __init__(self, parent=None, *args):
        super(ventana_principal,self).__init__(parent=parent)
        self.initUI()

    def initUI(self):
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowTitle("ABS")
        self.setWindowIcon(QIcon(":/Static/img/LIBiAM.jpg"))
        self.resize(700, 500)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.archivos_csv = []

        # OBTENER TAMAÑO Y ANCHO DE LA PANTALLA SIN LA BARRA DE TAREAS
        widget_xdd = QDesktopWidget()
        rec = widget_xdd.availableGeometry(widget_xdd.primaryScreen())
        self.setGeometry(rec.x(), rec.y(), rec.width(), rec.height())

        #IDENTIFICADOR ARCHIVOS
        self.id_archivo = 1

        #IDENTIFICADORES PARA LAS GRÁFICAS
        self.id_grafica = 0

        #CARGAR FUENTES AL PROYECTO
        load_fonts_from_dir(os.fspath(config.PATH_FONTS))

        # VALORES PANEL VISTAS
        self.vistas = []
        self.contador_vistas = 0

        # VALORES DE VISTA INICIO
        self.contador = 0
        self.lista_labels = []

        # AGREGO MENU DE ARRIBA
        menubar = QMenuBar()
        self.layout().addWidget(menubar, 0)

        #para saber si cerró desde la cruz superor derecha de la ventana o desde el o botón confirmar
        self.seguir_proceso = False

        actionFile = menubar.addMenu("Archivo")

        abrirCSV= QAction("Abrir .CSV",self)
        abrirCSV.triggered.connect(self.agregar_csv)
        actionFile.addAction(abrirCSV)

        Nuevo = QAction("Nuevo", self)
        # Nuevo.triggered.connect(quit)
        Nuevo.setEnabled(False)
        actionFile.addAction(Nuevo)

        Abrir = QAction("Abrir", self)
        # Nuevo.triggered.connect(quit)
        Abrir.setEnabled(False)
        actionFile.addAction(Abrir)

        # Guardar = QAction("Guardar", self)
        # Nuevo.triggered.connect(quit)
        #Guardar.setEnabled(False)
        #actionFile.addAction(Guardar)

        actionFile.addSeparator()
        Salir = QAction("Salir", self)
        Salir.triggered.connect(self.cerrar)
        actionFile.addAction(Salir)

        #editarMenu=menubar.addMenu("Editar")
        # editarMenu.addAction("")

        #filtradoMenu = menubar.addMenu("Filtrado")

        #Config = QAction("Configuracion", self)
        # Nuevo.triggered.connect(quit)
        #Config.setEnabled(False)
        #filtradoMenu.addAction(Config)

        #vista=menubar.addMenu("Vista")
        #nuevaV = QAction("Nueva Vista", self)
        #nuevaV.triggered.connect(self.nueva_vista)
        #vista.addAction(nuevaV)"""

        #ayudaMenu=menubar.addMenu("Ayuda")
        #Doc = QAction("Documentacion", self)
        # Nuevo.triggered.connect(quit)
        #Doc.setEnabled(False)
        #ayudaMenu.addAction(Doc)"""

        #Sobre = QAction("Sobre Nosotros", self)
        #Sobre.triggered.connect(self.ventana_inicio)
        #Sobre.setEnabled(False)
        #ayudaMenu.addAction(Sobre)

        confMenu = menubar.addMenu("Configuración")
        confArchivos = QAction("Archivos", self)
        confArchivos.triggered.connect(self.ventana_conf_archivos)

        confVistas = QAction("Límite gráficas", self)
        confVistas.triggered.connect(self.ventana_conf_vistas)

        confMenu.addAction(confArchivos)
        confMenu.addAction(confVistas)

        confMenuAyuda = menubar.addMenu("Ayuda")

        confManual = QAction("Descargar manual de usuario", self)
        confManual.triggered.connect(self.descargar_manual)
        confAcercaDe = QAction("Acerca de", self)

        confMenuAyuda.addAction(confManual)
        confMenuAyuda.addAction(confAcercaDe)

        #TOOLBAR
        self.widget_toolbar = QWidget()
        self.widget_toolbar.setMaximumHeight(40)
        self.widget_toolbar.setLayout(QHBoxLayout())
        self.widget_toolbar.layout().setContentsMargins(0,0,0,0)

        #WIDGET IZQUIERDA TOOLBAR
        wid_izquierda_toolbar = QWidget()
        wid_izquierda_toolbar.setLayout(QHBoxLayout())
        wid_izquierda_toolbar.layout().setContentsMargins(0,0,0,0)
        wid_izquierda_toolbar.layout().setAlignment(Qt.AlignLeft)
        wid_izquierda_toolbar.setMaximumWidth(270)

        # RANCIADA
        btn_nueva_vista = QPushButton("Nueva Vista")
        btn_nueva_vista.clicked.connect(self.nueva_vista)
        btn_nueva_vista.setStyleSheet(estilos.nuevaVista())
        wid_izquierda_toolbar.layout().addWidget(btn_nueva_vista)

        #WIDGET DERECHA TOOLBAR
        wid_derecha_toolbar = QWidget()
        wid_derecha_toolbar.setLayout(QHBoxLayout())
        wid_derecha_toolbar.layout().setContentsMargins(0,0,0,0)
        wid_derecha_toolbar.layout().setAlignment(Qt.AlignLeft)

        #BOTONES WIDGET DERECHA TOOLBAR
        btn_valores_en_bruto = QPushButton("Valores en bruto")
        btn_valores_en_bruto.clicked.connect(self.ventana_valoresEnBruto)
        btn_valores_en_bruto.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        btn_butter_filter = QPushButton("Filtrado")
        btn_butter_filter.clicked.connect(self.ventana_butter)
        btn_butter_filter.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        btn_valores_en_grafica = QPushButton("Valores en Gráfica")
        btn_valores_en_grafica.clicked.connect(self.ventana_valores_en_grafica)
        btn_valores_en_grafica.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        btn_cortar = QPushButton("Cortar")
        btn_cortar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())
        btn_cortar.clicked.connect(self.ventana_cortarMain)

        btn_rectificar = QPushButton("Rectificar")
        btn_rectificar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())
        btn_rectificar.clicked.connect(self.ventana_rectificar)

        btn_comparar = QPushButton("Comparar gráficas")
        btn_comparar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())
        btn_comparar.clicked.connect(self.ventana_comparar)

        btn_exportar_VP = QPushButton("▪ |Exportar datos| ▪")
        btn_exportar_VP.setStyleSheet(estilos.estilos_btn_exportar())
        btn_exportar_VP.clicked.connect(self.ventana_exportar_valores_pico)

        wid_derecha_toolbar.layout().addWidget(btn_valores_en_bruto)
        wid_derecha_toolbar.layout().addWidget(btn_rectificar)
        wid_derecha_toolbar.layout().addWidget(btn_butter_filter)
        wid_derecha_toolbar.layout().addWidget(btn_cortar)
        wid_derecha_toolbar.layout().addWidget(btn_valores_en_grafica)
        wid_derecha_toolbar.layout().addWidget(btn_comparar)
        wid_derecha_toolbar.layout().addWidget(btn_exportar_VP)

        self.widget_toolbar.layout().addWidget(wid_izquierda_toolbar, 2)
        self.widget_toolbar.layout().addWidget(wid_derecha_toolbar, 8)

        #botonesFiltrado = uic.loadUi('Static/uiFiles/botonesGraficado.ui')

        self.layout().addWidget(self.widget_toolbar, 1)

        # CONTENEDOR DEL PANEL Y GRÁFICAS
        self.widget_content = QWidget()
        self.widget_content.setLayout(QHBoxLayout())
        self.widget_content.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.widget_content, 9)

        self.width = rec.width()
        self.height = rec.height()

        # CONTENEDOR DE TREE GRÁFICAS
        self.widget_izq = QWidget(self.widget_content)
        self.widget_izq.setGeometry(0,0,275,int(self.height * 0.85))
        self.widget_izq.setLayout(QVBoxLayout())
        self.widget_izq.setStyleSheet("background-color:white;margin:0px;padding:0px;")
        self.widget_izq.layout().setContentsMargins(0, 0, 0, 0)
        self.widget_izq.layout().setSpacing(0)

        #CONTENEDOR DE BOTONES TOGGLE
        self.widget_buttons_toggle = QWidget(self.widget_content)
        self.widget_buttons_toggle.setGeometry(0,0,20,int(self.height * 0.9))
        self.widget_buttons_toggle.move(-20,0)
        self.widget_buttons_toggle.setStyleSheet("QWidget{border:0px solid black;background-color:white;}")
        self.widget_buttons_toggle.setLayout(QHBoxLayout())
        self.widget_buttons_toggle.layout().setContentsMargins(0,2,0,0)
        self.widget_buttons_toggle.layout().setSpacing(0)
        self.widget_buttons_toggle.layout().setAlignment(Qt.AlignTop)

        #WIDGET PARA ROTAR LOS BOTONES -90 GRADOS
        self.scene = QGraphicsScene()
        graphicView = QGraphicsView(self.scene, self)
        graphicView.setContentsMargins(0, 0, 0, 0)
        graphicView.setStyleSheet("QGraphicsView{border:none;}")
        graphicView.setMaximumHeight(400)
        graphicView.setAlignment(Qt.AlignTop)

        #<ELEMENTOS NECESARIOS PARA EL WIDGET ANTERIOR>
        wid = QWidget()
        wid.setLayout(QHBoxLayout())
        bt = QPushButton("Panel")
        bt.clicked.connect(self.maximizar_panel)
        bt.setFixedHeight(20)
        bt.setFixedWidth(75)

        wid.layout().setContentsMargins(0, 0, 0, 0)
        wid.layout().setSpacing(25)
        wid.layout().addWidget(bt)
        wid1 = self.scene.addWidget(wid)

        wid1.setRotation(-90)
        wid1.setPos(50, 50)
        #</ELEMENTOS NECESARIOS PARA EL WIDGET ANTERIOR>

        self.widget_buttons_toggle.layout().addWidget(graphicView)

        # CONTENEDOR GRÁFICAS
        self.widget_der = QTabWidget(self.widget_content)
        self.widget_der.setGeometry(280,0,int(self.width - 275),int(self.height * 0.9))
        self.ventana_inicio()
        self.widget_der.setMovable(True)
        self.widget_der.setTabsClosable(True)
        self.widget_der.tabCloseRequested.connect(self.eliminar_vista)
        self.widget_der.installEventFilter(self)
        self.widget_der.tabBar().installEventFilter(self)

        #CONTENEDOR DE COMBOBOX Y TOOLBAR DE ARCHIVOS CSV
        widget_archivos_csv = QWidget()
        widget_archivos_csv.setLayout(QHBoxLayout())
        widget_archivos_csv.layout().setContentsMargins(0,0,0,0)
        widget_archivos_csv.layout().setSpacing(0)
        widget_archivos_csv.setStyleSheet("background-color:white;border:1px solid gray;border-bottom:0px;")
        widget_archivos_csv.setFixedHeight(24)
        self.widget_izq.layout().addWidget(widget_archivos_csv)

        #CONTENEDOR DE LOS ARCHIVOS CSV
        widget_lista_archivos = QWidget()
        widget_lista_archivos.setLayout(QVBoxLayout())
        widget_lista_archivos.layout().setContentsMargins(2, 2, 2, 2)
        widget_lista_archivos.layout().setSpacing(0)

        #COMBOBOX DE ARCHIVOS CSV
        self.combo = QComboBox()
        self.combo.addItem("Agregue un archivo csv")
        self.combo.currentIndexChanged.connect(self.actualizar_tree)
        self.combo.setStyleSheet(estilos.estilos_combobox_archivos_csv())
        widget_lista_archivos.layout().addWidget(self.combo)

        # CONTENEDOR DE BOTONES PARA LOS ARCHIVOS CSV
        widget_botones_csv = QToolBar()
        widget_botones_csv.setIconSize(QSize(14,14))
        widget_botones_csv.setStyleSheet(estilos.estilos_toolbar_archvos_csv())
        icono_hide = QIcon(":/Static/img/hide.svg")
        icono_remove = QIcon(":/Static/img/eliminar.svg")
        icono_agregar = QIcon(":/Static/img/add.svg")

        widget_botones_csv.addAction(icono_remove, 'eliminar', self.eliminar_csv)
        widget_botones_csv.addAction(icono_agregar, 'agregar', self.agregar_csv)
        widget_botones_csv.addAction(icono_hide,'ocultar',self.minimizar_panel)

        widget_archivos_csv.layout().addWidget(widget_lista_archivos, 7)
        widget_archivos_csv.layout().addWidget(widget_botones_csv, 3)

        #ÁRBOL DE GRÁFICAS
        self.tree_widget = QTreeWidget()
        self.tree_widget.setStyleSheet(estilos.estilos_tree_widget_graficas())
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemDoubleClicked.connect(self.agregar_grafica_a_vista)
        self.widget_izq.layout().addWidget(self.tree_widget, 5)

        # ÁRBOL DE VISTAS
        self.treeView2 = QTreeWidget()
        self.treeView2.setStyleSheet(estilos.estilos_tree_widget_graficas())
        self.treeView2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView2.customContextMenuRequested.connect(self.handle_rightClicked)
        self.treeView2.setHeaderHidden(True)
        self.widget_izq.layout().addWidget(self.treeView2, 4)

    def descargar_manual(self):
        path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        if len(path) == 0:
            return

        shutil.copy2('./ManualPrueba.pdf', path)  # complete target filename given

    def eventFilter(self, source, event):
        if source == self.widget_der.tabBar() and \
            event.type() == event.MouseButtonPress and \
            event.button() == Qt.LeftButton:
                tab = self.widget_der.tabBar().tabAt(event.pos())
                if tab >= 0 and tab != self.widget_der.currentIndex():
                    return self.isInvalid()
        elif source == self.widget_der and \
            event.type() == event.KeyPress and \
            event.key() in (Qt.Key_Tab, Qt.Key_Backtab) and \
            event.modifiers() & Qt.ControlModifier:
                return self.isInvalid()
        return super().eventFilter(source, event)

    def isInvalid(self):
        continuar = not chequearSiEstaRecortando(self)
        if not continuar:
            #QTimer.singleShot(0, lambda: QtWidgets.QMessageBox.about(
                #self, "Warning", "You must complete the form"))
            return True
        return False

    def cerrar(self):
        sys.exit()

    def ventana_conf_archivos(self):
        ventana_conf_archivos(self).exec_()

    def ventana_conf_vistas(self):
        ventana_conf_vistas(self).exec_()

    def ventana_inicio(self):

        #SOMBRAS PARA CUADRO DE TEXTO E IMAGENES
        shadow = QGraphicsDropShadowEffect(blurRadius=20, xOffset=8, yOffset=8)
        shadow2 = QGraphicsDropShadowEffect(blurRadius=20, xOffset=6, yOffset=6)

        widget_inicio = QWidget()
        widget_inicio.setLayout(QVBoxLayout())
        widget_inicio.layout().setContentsMargins(0,0,0,0)
        widget_inicio.setStyleSheet(estilos.estilos_widget_inicio())

        widget_header = QWidget()
        widget_header.setLayout(QHBoxLayout())
        widget_header.layout().setSpacing(50)
        widget_header.layout().setAlignment(Qt.AlignHCenter)
        widget_header.setStyleSheet(estilos.estilos_widget_header_inicio())

        widget_contenido = QWidget()
        widget_contenido.setLayout(QHBoxLayout())
        widget_contenido.setStyleSheet(estilos.estilos_widget_content())
        widget_contenido.layout().setContentsMargins(6,10,0,0)
        widget_contenido.layout().setSpacing(0)

        img_ANEP_UTU = QPixmap(':/Static/img/utu.png')
        lab_ANEP_UTU = QLabel()
        lab_ANEP_UTU.setFixedWidth(img_ANEP_UTU.width())
        lab_ANEP_UTU.setPixmap(img_ANEP_UTU)

        img_LIBiAM = QPixmap(':/Static/img/LIBiAM2.jpg')
        lab_LIBiAM = QLabel()
        lab_LIBiAM.setFixedWidth(img_LIBiAM.width())
        lab_LIBiAM.setPixmap(img_LIBiAM)

        img_UDELAR = QPixmap(':/Static/img/cenur.jpg')
        lab_UDELAR = QLabel()
        lab_UDELAR.setFixedWidth(int(img_UDELAR.width()))
        lab_UDELAR.setPixmap(img_UDELAR)

        img_UTEC = QPixmap(':/Static/img/utec.png')
        lab_UTEC = QLabel()
        lab_UTEC.setFixedWidth(img_UTEC.width())
        lab_UTEC.setPixmap(img_UTEC)

        widget_header.layout().addWidget(lab_LIBiAM)
        widget_header.layout().addWidget(lab_UTEC)
        widget_header.layout().addWidget(lab_ANEP_UTU)
        widget_header.layout().addWidget(lab_UDELAR)

        widget_inicio.layout().addWidget(widget_header,1)
        widget_inicio.layout().addWidget(widget_contenido, 9)
        widget_inicio.setObjectName("Inicio")

        label1 = QLabel("LIBiAM")
        label1.setStyleSheet("color:black;font:bold 28px;")

        label2 = QLabel()
        label2.setText(strings.descripcion_de_LIBiAM() + "\n\n" + strings.descripcion_de_LIBiAM2())
        label2.setWordWrap(True)
        label2.setMinimumHeight(230)
        label2.setAlignment(Qt.AlignTop)

        widget_izquierda_section = QWidget()
        widget_izquierda_section.setLayout(QVBoxLayout())
        widget_izquierda_section.layout().setContentsMargins(8,10,10,20)
        widget_izquierda_section.layout().setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        widget_labels = QWidget()
        widget_labels.setLayout(QVBoxLayout())
        widget_labels.setMaximumWidth(600)
        widget_labels.setStyleSheet("QWidget{background-color:white;border-radius:4px} QLabel{margin:0px;}")
        widget_labels.setGraphicsEffect(shadow2)
        widget_labels.layout().setSpacing(16)
        widget_labels.layout().setAlignment(Qt.AlignHCenter)
        widget_labels.layout().setContentsMargins(14,10,10,30)

        db = QFontDatabase()
        font = db.font("Roboto Light", "Regular", 12)
        label2.setFont(font)
        widget_labels.layout().addWidget(label1)
        widget_labels.layout().addWidget(label2)

        widget_izquierda_section.layout().addWidget(widget_labels)
        widget_derecha_section = QWidget()

        widget_derecha_section.setLayout(QVBoxLayout())
        widget_derecha_section.layout().setContentsMargins(0,15,0,0)
        widget_derecha_section.layout().setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        widget_contenedor_imagenes = QWidget()
        widget_contenedor_imagenes.setFixedWidth(455)
        widget_contenedor_imagenes.setFixedHeight(305)
        widget_contenedor_imagenes.setLayout(QVBoxLayout())
        widget_contenedor_imagenes.layout().setAlignment(Qt.AlignCenter)
        widget_contenedor_imagenes.layout().setContentsMargins(0,0,0,0)

        widget_contenedor_imagenes.setGraphicsEffect(shadow)
        widget_derecha_section.layout().addWidget(widget_contenedor_imagenes)

        widget_imagenes = QWidget(widget_contenedor_imagenes)
        widget_imagenes.setFixedWidth(455)
        widget_imagenes.setFixedHeight(305)
        widget_contenedor_imagenes.layout().addWidget(widget_imagenes)

        img1 = QPixmap(':/Static/img/imglib1.png').scaled(455, 305)
        img2 = QPixmap(':/Static/img/imglib2.png').scaledToHeight(305)
        img3 = QPixmap(':/Static/img/img_content.jpg').scaledToHeight(305).scaledToWidth(455)

        lab1 = QLabel(widget_imagenes)
        lab1.setPixmap(img1)
        lab1.move(-455, 0)

        lab2 = QLabel(widget_imagenes)
        lab2.move(0,0)
        lab2.setPixmap(img2)

        lab3 = QLabel(widget_imagenes)
        lab3.move(-455, 0)
        lab3.setPixmap(img3)

        self.lista_labels.append(lab2)
        self.lista_labels.append(lab1)
        self.lista_labels.append(lab3)

        widget_contenido.layout().addWidget(widget_izquierda_section,5)
        widget_contenido.layout().addWidget(widget_derecha_section,5)

        self.widget_der.insertTab(0, widget_inicio, "Inicio")

        self.animation1 = QPropertyAnimation(self)
        self.animation1.setPropertyName(b'pos')
        self.animation1.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation1.setStartValue(QPoint(0, 0))
        self.animation1.setEndValue(QPoint(455, 0))
        self.animation1.setDuration(1000)

        self.animation2 = QPropertyAnimation(self)
        self.animation2.setPropertyName(b'pos')
        self.animation2.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation2.setStartValue(QPoint(-455, 0))
        self.animation2.setEndValue(QPoint(0, 0))
        self.animation2.setDuration(1000)

        timer = QTimer(widget_imagenes)
        timer.timeout.connect(self.animation)
        timer.start(4500)


    def get_id_grafica(self):
        id = self.id_grafica
        self.id_grafica += 1
        return id

    def animation(self):
        self.animation1.setTargetObject(self.lista_labels[self.contador])

        if self.contador == len(self.lista_labels) - 1:
            self.contador = -1

        self.animation2.setTargetObject(self.lista_labels[self.contador + 1])

        self.animation1.start()
        self.animation2.start()

        self.contador += 1


    def handle_rightClicked(self, pos):

        item = self.treeView2.itemAt(pos)
        if item is None:
            return
        menu = QtWidgets.QMenu()
        if item.parent() is not None:
            remover_grafiaca = QAction("Remover gráfica")
            remover_grafiaca.triggered.connect(lambda checked, item=item: self.remover_grafica(item))

            remover_filtro = QAction("Remover filtros")
            #remover_filtro.triggered.connect(lambda checked, item=item: self.remover_filtros())

            aplicar_filtro = QAction("Aplicar filtro")
            #aplicar_filtro.triggered.connect(lambda checked, item=item: self.aplicar_filtro())

            aplicar_valor_picos = QAction("Mostrar picos")
            #aplicar_valor_picos.triggered.connect(lambda checked, item=item: self.aplicar_valores_picos())

            menu.addAction(remover_grafiaca)
            #menu.addAction(remover_filtro)
            #menu.addAction(aplicar_filtro)
            #menu.addAction(aplicar_valor_picos)
        elif item.parent() is None:
            print_burro = QAction("Print Burro")
            print_burro.triggered.connect(lambda checked, item=item: self.print_burro())
            #menu.addAction(print_burro)
        menu.exec_(self.treeView2.viewport().mapToGlobal(pos))

    def remover_grafica(self, item : tree_widget_item_vista):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            if item is None:
                return

            for vista in self.vistas:
                graficas = vista.get_graficas()
                cantidad_graficas = len(graficas)
                for i in range(cantidad_graficas):
                    if graficas[i].get_tree_item() == item:
                        item_v : QTreeWidgetItem= vista.get_tree_widget_item()
                        item_v.removeChild(graficas[i].get_tree_item())
                        vista.get_graficas().pop(i)
                        self.listar_graficas(True,widget_tab=vista.get_widget())
                        return


    def print_burro(self):
        print("no")

    def show_graph(self, father : QMessageBox):
        print('Show Graph')
        self.msgbox_abrir_csv_antes_columnas.close()

    def agregar_csv(self):
        """
            Función para agregar archivos .csv
        :return:
        """
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            options = QFileDialog.Options()
            filepath = QFileDialog.getOpenFileName(self, "Seleccione un archivo", "", filter = f"{config.FILES_CSV}", options=options)

            # Si se cancela la ventana emergente al seleccionar un archivo .csv
            if not filepath[0]:
                return

            try:
                frame_archivo = pandas.read_csv(filepath[0], encoding=config.ENCODING, skiprows=config.ROW_COLUMNS)
            except Exception as e:

                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText('Al parecer el número de fila que especificó no es correcto.\nVerifíquelo en Configuración -> Archivos.')
                yes_button = msg.addButton('Ver ayuda', QMessageBox.YesRole)
                #yes_button.clicked.disconnect()
                #yes_button.clicked.connect(self.show_graph)
                #msg.setStyleSheet("background-color:red;")
                msg.addButton(QMessageBox.Ok)
                msg.exec_()

                if msg.clickedButton() == yes_button:
                    ventana_verayuda_antes_columnas(self).exec_()


                #QMessageBox.about(self, "Error", "")
                ventana_conf_archivos(self).exec_()
                return

            nombre_archivo = funciones.get_nombre_csv(filepath[0])
            nombre_archivo += " - A" + str(self.id_archivo)

            self.archivito = Archivo(nombre_archivo,frame_archivo)
            self.archivito.agregar_electromiografias(frame_archivo)

            if len(self.archivito.get_electromiografias()) == 0:
                QMessageBox.about(self, "Error", "Al parecer este archivo csv no es de Trigno o el número\nde fila que especificó no es correcto")
                ventana_conf_linea_archivo(self).exec_()
                if not self.seguir_proceso:
                    return
                else:
                    #dejarlo en el valor inicial
                    self.seguir_proceso = False


            self.archivos_csv.append(self.archivito)
            text_current_index = self.combo.currentText()

            if text_current_index == "Agregue un archivo csv":
                self.combo.addItem(nombre_archivo)
                self.combo.removeItem(self.combo.currentIndex())
                self.combo.setItemData(self.combo.currentIndex(), self.id_archivo)
            else:
                self.combo.addItem(nombre_archivo, self.id_archivo)
            self.id_archivo += 1

    def actualizar_tree(self):
        self.tree_widget.clear()
        nombre_archivo = self.combo.currentText()
        for archivo in self.archivos_csv:
            if nombre_archivo == archivo.get_nombre_archivo():
                for emg in archivo.get_electromiografias():
                    EMG = QTreeWidgetItem([emg.get_nombre_corto()])
                    EMG.setIcon(0, QIcon(config.ICONO_CARPETAS))
                    graficas = emg.get_graficas()
                    for grafica in graficas:
                        grafica = QTreeWidgetItem([grafica.get_nombre_columna_grafica()])
                        grafica.setIcon(0, QIcon(config.ICONO_GRAFICAS))
                        EMG.addChild(grafica)

                    self.tree_widget.addTopLevelItem(EMG)
                break

    def get_numero_grafica(self, vista : Vista, nombre_grafica, numero_archivo):
        numero_grafica = None
        existe = False
        existe_numero = False
        graficas = vista.get_graficas()
        graficas_aux = []

        for grafica in graficas:
            if nombre_grafica == grafica.get_nombre_columna_grafica() and grafica.get_numero_archivo() == numero_archivo:
                existe = True
                graficas_aux.append(grafica)

        # CÓDIGO DE LA NASA PURO PAAA
        if not existe:
            return 1
        else:
            for i in range(len(graficas_aux)):
                existe_numero = False
                numero_grafica = i + 1

                for grafica in graficas_aux:
                    if numero_grafica == grafica.get_numero_grafica():
                        existe_numero = True
                        break

                if not existe_numero:
                    break


        if existe_numero:
            return numero_grafica + 1

        return numero_grafica


    def agregar_grafica_a_vista(self, item, col):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            current_widget = self.widget_der.currentWidget()
            index = self.widget_der.indexOf(current_widget)

            if not index == -1 and item.parent() is not None:
                object_name = current_widget.objectName()
                if not object_name == "Inicio":
                    widget_tab = self.widget_der.currentWidget()
                    vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)

                    limite_graficas = config.LIMITE_GRAFICAS_POR_VISTA

                    if len(vista.get_graficas()) == limite_graficas:
                        QMessageBox.about(self, "Error", "El máximo de gráficas por vista es "+ str(limite_graficas)+ ".\nPuede modficar este limite en \nConfiguraciones -> Limite gráficas")
                        return

                    numero_archivo = self.combo.currentData()
                    numero_grafica = self.get_numero_grafica(vista, item.text(col), int(numero_archivo))

                    nombre_item = item.text(col) + " - (" + str(numero_grafica)+") A" + str(numero_archivo)
                    grafica_vista = QTreeWidgetItem([nombre_item])
                    grafica_vista.setIcon(0, QIcon(config.ICONO_GRAFICAS))
                    grafica_vista.setToolTip(0, nombre_item )

                    vista.get_tree_widget_item().addChild(grafica_vista)
                    grafica : Grafica = self.get_grafica(item.text(col), grafica_vista, nombre_item, numero_grafica, int(numero_archivo))
                    vista.agregar_grafica(grafica)
                    cant_vistas = vista.get_tree_widget_item().childCount()
                    self.listar_graficas(False)
                    self.treeView2.expandItem(vista.get_tree_widget_item())

    def setFiltros(self, datos, datosFiltrado, datosFFT):
        filter_signal = filtersHelper.butterFilter(datos, datosFiltrado)
        if filter_signal[1] == "error":  #caso que el fitro dio error en el try
            filter_signal=datos
        else:
            filter_signal = filter_signal[0]

        #Chequeo si está el fft para aplicarlo también.
        filter_signal = filtersHelper.fft(filter_signal, datosFFT)

        return filter_signal

    def recortarGraficos(self, datos, tiempo, datosRecorte):
        return filtersHelper.recortarGrafico(datos, tiempo, datosRecorte)

    def aplicarOffset(self, datos, tiempo, datosOffset):
        return filtersHelper.offsetGrafico(datos, tiempo, datosOffset)

    def mostrar_valores_picos(self, ax, _tiempo, datosOffset, valores_picos : Pico, exponente, grafica : Grafica):
        if exponente != 1:
            peaks = find_peaks(datosOffset, height=(valores_picos.get_min_height() * pow(10, int(exponente))),
                               threshold=valores_picos.get_treshold(), distance=valores_picos.get_distance())
        else:
            peaks = find_peaks(datosOffset, height=valores_picos.get_min_height(),
                               threshold=valores_picos.get_treshold(), distance=valores_picos.get_distance())

        height = peaks[1]['peak_heights']  # list of the heights of the peaks
        peak_pos = _tiempo[peaks[0]]  # list of the peaks positions
        tiempo = [0]
        for pos in peak_pos:
            tiempo.append(pos)

        for i in range(0, height.size):
            if exponente != 1:
                numeroAMostrar = str("{:.4f}".format(height[i] / (pow(10, int(exponente)))))
                ax.annotate(numeroAMostrar + "x10e" + str(exponente), xy=(tiempo[i + 1], height[i]))
            else:
                numeroAMostrar = str("{:.4f}".format(height[i]))
                ax.annotate(numeroAMostrar, xy=(tiempo[i + 1], height[i]))

            grafica.set_valores_pico_para_exportar(height)

        if height.size == 0:
            grafica.set_valores_picos(None)
            QMessageBox.information(self, "Advertencia", "No se encontró ningún valor pico")
        else:
            ax.scatter(peak_pos, height, color='r', s=15, marker='o', label='Picos')
            ax.legend()


    def mostrar_integral(self, ax, _tiempo, datos,valores_integral, exponente, grafica: Grafica):

        a, b = valores_integral[0], valores_integral[1]  # integral limits
        aux = _tiempo
        #aux_real = aux.real
        #aux_imag = aux.imag

        #xxx = []
        #yyy = []

        iy = []
        ix = []

        #ry = []
        #rx = []

        #if grafica.get_fastfouriertransform() is not None:
        #    for i in range(0, aux_real.size):
        #        if (aux_real[i] > a and aux_real[i] < b):
        #            ry.append(datos[i])
        #            rx.append(aux_real[i])

        #    for i in range(0, aux_imag.size):
        #        if (aux_imag[i] > a and aux_imag[i] < b):
        #            iy.append(datos[i])
        #            ix.append(aux_imag[i])

        #else:
        for i in range(0, aux.size):
            if (aux[i] > a and aux[i] < b):
                iy.append(datos[i])
                ix.append(aux[i])

        verts = [(a, 0), *zip(ix, iy), (b, 0)]
        poly = Polygon(verts, facecolor='limegreen', edgecolor='darkgreen',alpha = 0.5)
        ax.add_patch(poly)

        ax.set_xticks((a, b))
        ax.set_xticklabels((a, b))
        #print(exponente)
        #print("integral_antes")

        # calculo la integral
        def getVoltajeAPartirDeUnTiempo(x):
            ret=0
            for i in range(0, aux.size):
                if (aux[i] > x):
                    ret = datos[i]
                    return ret
            return ret

        totalDeLaIntegral=0
        contador=a
        calculando=True
        intervalo=0.1

        #tod  esto se hace para que se fraccione el calculo de la integral y no de error y ande mas rapido
        if (b-a)<=intervalo:                #primer caso que la integral sea menor a 0.25 segundos
            i, err = scipy.integrate.quad(getVoltajeAPartirDeUnTiempo, a, b, limit=120, epsabs = 9999999999999)
            totalDeLaIntegral = i
        else:                        #si es mayor a 0.25
            while (calculando):
                #print(contador)
                if (contador+intervalo)<b:                 #pregunto si estoy llegando al final
                    i, err = scipy.integrate.quad(getVoltajeAPartirDeUnTiempo,contador,contador+intervalo, limit=60, epsabs = 9999999999999)
                    totalDeLaIntegral = totalDeLaIntegral+i
                    contador= contador+intervalo
                else:                               #calculo el resto que me queda
                    i, err = scipy.integrate.quad(getVoltajeAPartirDeUnTiempo, contador, b, limit=50, epsabs = 9999999999999)
                    totalDeLaIntegral = totalDeLaIntegral + i
                    calculando=False
        if exponente != 1:
            numeroAMostrar = str("{:.4f}".format(totalDeLaIntegral / (pow(10, int(exponente)))))
            ax.annotate("Valor de la integral: "+numeroAMostrar+ "x10e" + str(exponente), xy=((a + b) / 2, 0),
                        xytext=((a + b) / 2, 0))
        else:
            numeroAMostrar = str("{:.4f}".format(totalDeLaIntegral))
            ax.annotate("Valor de la integral: " + numeroAMostrar, xy=((a + b) / 2, 0),
                        xytext=((a + b) / 2, 0))

        grafica.set_valor_integral_para_exportar(totalDeLaIntegral)

    def calcularYMostrar_RMS(self,axes, ax, tiempo,grafica: Grafica):
        resultado=0
        a = grafica.get_rmsLimites()[0]
        b = grafica.get_rmsLimites()[1]
        exponente=grafica.get_exponente()
        aux = filtersHelper.recortarGrafico(ax, tiempo, [a,b])[0]

        #Una poronga esto, arreglalo Chopan <3.
        resultado = np.sum(np.sqrt(np.mean(pow(aux,2))),0)

        if exponente != 1:
            numeroAMostrar = str("{:.4f}".format(resultado / (pow(10, int(exponente)))))
            axes.annotate("Valor RMS: " + numeroAMostrar + "x10e" + str(exponente), xy=((a + b) / 2, 0),
                    xytext=((a + b) / 2, resultado))
        else:
            numeroAMostrar = str("{:.4f}".format(resultado))
            axes.annotate("Valor RMS: " + numeroAMostrar, xy=((a + b) / 2, 0),
                          xytext=((a + b) / 2, resultado))

        rectangulo = plt.Rectangle((a, resultado), b-a, ((resultado/10)/((b-a)/2)), color='grey', alpha = 0.6) # esta mejorado,pero ponele el otro color
        axes.add_patch(rectangulo)
        grafica.set_rms(resultado)

    def listar_graficas(self, despues_de_filtro=False, valores_pico=False, widget_tab=None):
        global listaDeAxes
        if widget_tab is None:
            widget_tab = self.widget_der.currentWidget()

        object_name = widget_tab.objectName()
        if not object_name == "Inicio":

            vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
            cant_graficas = vista.get_tree_widget_item().childCount()
            if vista is not None:

                if cant_graficas == 1:

                    widget_tab.layout().removeWidget(vista.get_canvas())
                    if vista.get_nav_toolbar() is not None:
                        widget_tab.layout().removeWidget(vista.get_nav_toolbar())
                    widget_tab.layout().removeWidget(vista.get_scroll())

                    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(18, 4))
                    # cid = fig.canvas.mpl_connect('button_press_event', onclick)
                    fig.canvas.mpl_connect('axes_enter_event', enter_axes)

                    graficas = vista.get_graficas()
                    archivo = graficas[0].get_archivo()

                    #/########################        Aplicando valores de todas las ventanas        ########################/#

                    #aplico offset
                    conOffset= self.aplicarOffset(archivo[graficas[0].get_nombre_columna_grafica()],archivo[graficas[0].get_nombre_columna_tiempo()],graficas[0].get_offset())

                    #aplico butter y fft
                    filtrado = self.setFiltros(conOffset, graficas[0].get_filtro(), graficas[0].get_fastfouriertransform())

                    recorte = self.recortarGraficos(filtrado,
                                            archivo[graficas[0].get_nombre_columna_tiempo()],
                                            graficas[0].get_recorte())
                    #aplico recorte
                    aux= recorte[0]
                    tiempoRecortado = recorte[1]

                    # calculo y muestro valores picos
                    if graficas[0].get_valores_picos() is not None:
                        self.mostrar_valores_picos(axes, tiempoRecortado.values, aux, graficas[0].get_valores_picos(), graficas[0].get_exponente(), graficas[0])

                    # calculo y muestro integral
                    if graficas[0].get_integral()[2]:
                        self.mostrar_integral(axes, tiempoRecortado.values, aux,
                                              graficas[0].get_integral(), graficas[0].get_exponente(), graficas[0])



                    # /########################        Aplicando valores de todas las ventanas        ########################/#

                    y = aux.imag
                    x = aux.real

                    if graficas[0].get_fastfouriertransform() is not None:
                        line, = axes.plot(tiempoRecortado,
                                 y, linewidth=0.3, label=f"{graficas[0].get_nombre_columna_grafica_vista()}")

                        line, = axes.plot(tiempoRecortado,
                                          x, linewidth=0.3, label=f"{graficas[0].get_nombre_columna_grafica_vista()}")
                    else:
                        line, = axes.plot(tiempoRecortado,
                                          aux, linewidth=0.3, label=f"{graficas[0].get_nombre_columna_grafica_vista()}")

                    linebuilder = LineBuilder(line,axes,graficas[0],self)

                    plt.tight_layout()

                    exponent = axes.yaxis.get_offset_text().get_text()
                    if exponent is None or len(exponent) == 0:
                        graficas[0].set_exponente(1)
                    else:
                        exp = 0
                        #Si el exponente es negativo, entonces el primer elemento del string va a ser "-", de
                        #lo contrario va a ser cualquier otro número.
                        #Se aplica una expresión regular para reemplazar el signo de menos fake por el real.
                        shrek = re.sub(r'[^\x00-\x7F]+', '-', exponent)
                        try:
                            exponente_negativo = shrek.index('-')
                        except ValueError:
                            exponente_negativo = -1

                        if  exponente_negativo != -1:
                            #Si el exponente es negativo hay que transformar el signo de - que viene porque no lo toma
                            #como si fuera el signo de menos real.
                            exp = int(shrek.split('e')[1])
                        else:
                            #Sino queda como estaba antes que ya andaba
                            exp = int(exponent.split('e')[1])
                        graficas[0].set_exponente(exp)

                    axes.legend()

                    if graficas[0].get_rmsLimites()[2]:
                        self.calcularYMostrar_RMS(axes,aux,tiempoRecortado, graficas[0])
                    # ------------------------------------- Aspecto
                    # si no esta recortado
                    if graficas[0].get_recorte()[0] == 0 and graficas[0].get_recorte()[1] == 0:
                        axes.set(xlabel='tiempo (s)', ylabel='voltage (mV)')
                        axes.xaxis.set_minor_locator(MultipleLocator(0.5))
                        axes.xaxis.set_major_locator(MultipleLocator(1))
                        axes.tick_params(which='minor', length=5, width=1.5, color='r')
                        axes.set_xmargin(0)
                        axes.grid()
                    else:
                        axes.set(xlabel='tiempo (s)', ylabel='voltage (mV)')
                        axes.xaxis.set_minor_locator(MultipleLocator(0.125))
                        axes.xaxis.set_major_locator(MultipleLocator(0.25))
                        axes.tick_params(which='minor', length=5, width=1.5, color='r')
                        axes.set_xmargin(0)
                        axes.grid()
                    # -------------------------------------
                    plt.tight_layout()
                    plt.close(fig)

                    canvas = FigureCanvas(fig)
                    scroll_area = QScrollArea(widget_tab)
                    scroll_area.setWidget(canvas)
                    nav_toolbar = NavigationToolbar(canvas, widget_tab)

                    vista.set_canvas(canvas)
                    vista.set_scroll(scroll_area)
                    vista.set_nav_toolbar(nav_toolbar)

                    canvas.draw()
                    widget_tab.layout().addWidget(nav_toolbar)
                    widget_tab.layout().addWidget(scroll_area)

                elif cant_graficas > 1:
                    fig, axes = plt.subplots(nrows=cant_graficas, ncols=1, figsize=(18, 4 * cant_graficas))
                    # cid = fig.canvas.mpl_connect('button_press_event', onclick())
                    #fig.canvas.mpl_connect('axes_enter_event', enter_axes)
                    fig.canvas.mpl_connect('axes_enter_event', enter_axes)
                    fig.canvas.mpl_connect('axes_leave_event', leave_axes)
                    graficas = vista.get_graficas()

                    for x in range(cant_graficas):
                        archivo = graficas[x].get_archivo()

                        # /########################        Aplicando valores de todas las ventanas        ########################/#

                        # aplico offset
                        conOffset = self.aplicarOffset(archivo[graficas[x].get_nombre_columna_grafica()],
                                                       archivo[graficas[x].get_nombre_columna_tiempo()],
                                                       graficas[x].get_offset())

                        # aplico butter
                        filtrado = self.setFiltros(conOffset, graficas[x].get_filtro(),
                                                   graficas[x].get_fastfouriertransform())

                        recorte = self.recortarGraficos(filtrado,
                                                        archivo[graficas[x].get_nombre_columna_tiempo()],
                                                        graficas[x].get_recorte())
                        # aplico recorte
                        aux = recorte[0]
                        tiempoRecortado = recorte[1]

                        # calculo y muestro valores picos
                        if graficas[x].get_valores_picos() is not None:
                            self.mostrar_valores_picos(axes[x], tiempoRecortado.values, aux,
                                                       graficas[x].get_valores_picos(), graficas[x].get_exponente(),
                                                       graficas[x])
                        # calculo y muestro integral
                        if graficas[x].get_integral()[2]:
                            self.mostrar_integral(axes[x], tiempoRecortado.values, aux,
                                                      graficas[x].get_integral(), graficas[x].get_exponente(), graficas[x])

                        # /########################        Aplicando valores de todas las ventanas        ########################/#

                        imag = aux.imag
                        reales = aux.real

                        if graficas[x].get_fastfouriertransform() is not None:
                            line, = axes[x].plot(tiempoRecortado,
                                              imag, linewidth=0.3,
                                              label=f"{graficas[x].get_nombre_columna_grafica_vista()}")

                            line, = axes[x].plot(tiempoRecortado,
                                              reales, linewidth=0.3,
                                              label=f"{graficas[x].get_nombre_columna_grafica_vista()}")
                        else:
                            line, = axes[x].plot(tiempoRecortado,
                                              aux, linewidth=0.3,
                                              label=f"{graficas[x].get_nombre_columna_grafica_vista()}")

                        linebuilder = LineBuilder(line, axes[x], graficas[x], self, True)


                        # ------------------------------------- Aspecto
                        # si no esta recortado
                        if graficas[x].get_recorte()[0] == 0 and graficas[x].get_recorte()[1] == 0:
                            axes[x].set(xlabel='tiempo (s)', ylabel='voltage (mV)')
                            axes[x].xaxis.set_minor_locator(MultipleLocator(0.5))
                            axes[x].xaxis.set_major_locator(MultipleLocator(1))
                            axes[x].tick_params(which='minor', length=5, width=1.5, color='r')
                            axes[x].set_xmargin(0)
                            axes[x].grid()
                        else:
                            axes[x].set(xlabel='tiempo (s)', ylabel='voltage (mV)')
                            axes[x].xaxis.set_minor_locator(MultipleLocator(0.125))
                            axes[x].xaxis.set_major_locator(MultipleLocator(0.25))
                            axes[x].tick_params(which='minor', length=5, width=1.5, color='r')
                            axes[x].set_xmargin(0)
                            axes[x].grid()
                        # -------------------------------------
                        #VALORES PICOS DE LA GRÁFICA
                        #if graficas[x].get_valores_picos() is not None:
                        #    self.mostrar_valores_picos(axes[x], tiempoRecortado, conOffset,
                        #                               graficas[x].get_valores_picos(), graficas[x].get_exponente(),
                        #                               graficas[x])

                        axes[x].legend()
                        plt.tight_layout()
                        exponent = axes[x].yaxis.get_offset_text().get_text()
                        if exponent is None or len(exponent) == 0:
                            graficas[x].set_exponente(1)
                        else:
                            shrek = re.sub(r'[^\x00-\x7F]+', '-', exponent)
                            try:
                                exponente_negativo = shrek.index('-')
                            except ValueError:
                                exponente_negativo = -1
                            exp = 0
                            # Si el exponente es negativo, entonces el primer elemento del string va a ser "-", de
                            # lo contrario va a ser cualquier otro número.
                            if exponente_negativo != -1:
                                # Si el exponente es negativo hay que transformar el signo de - que viene porque no lo toma
                                # como si fuera el signo de menos real.
                                exp = int(shrek.split('e')[1])
                            else:
                                # Sino queda como estaba antes que ya andaba
                                exp = int(exponent.split('e')[1])
                            graficas[x].set_exponente(exp)

                        if graficas[x].get_rmsLimites()[2]:
                            self.calcularYMostrar_RMS(axes[x], aux, tiempoRecortado, graficas[x])

                    listaDeAxes = []
                    for x in range(cant_graficas):
                        listaDeAxes.append(sacarSegundoParametroAxesSubplot(str(axes[x])))

                    plt.close(fig)
                    #fig.tight_layout()

                    widget_tab.layout().removeWidget(vista.get_canvas())
                    widget_tab.layout().removeWidget(vista.get_nav_toolbar())
                    widget_tab.layout().removeWidget(vista.get_scroll())

                    canvas = FigureCanvas(fig)
                    scroll_area = QScrollArea(widget_tab)
                    scroll_area.setWidget(canvas)
                    nav_toolbar = NavigationToolbar(canvas, widget_tab)

                    vista.set_canvas(canvas)
                    vista.set_scroll(scroll_area)
                    vista.set_nav_toolbar(nav_toolbar)

                    canvas.draw()
                    widget_tab.layout().addWidget(nav_toolbar)
                    widget_tab.layout().addWidget(scroll_area)
                else:
                    widget_tab.layout().removeWidget(vista.get_canvas())
                    widget_tab.layout().removeWidget(vista.get_nav_toolbar())
                    widget_tab.layout().removeWidget(vista.get_scroll())
                    canvas = FigureCanvas()
                    scroll_area = QScrollArea()
                    scroll_area.setWidget(canvas)
                    vista.set_canvas(canvas)
                    vista.set_scroll(scroll_area)
                    canvas.draw()
                    widget_tab.layout().addWidget(scroll_area)

    def get_grafica(self, nombre_columna, tree_item_vista, nombre_columna_vista, numero_grafica, numero_archivo):
        dt_archivo = self.get_archivo_en_combobox()
        index_xs = dt_archivo.columns.get_loc(nombre_columna)-1
        nom_col = dt_archivo.columns[index_xs]
        #numero_base_grafica = self.get_numero_base_grafica(nombre_columna, nom_col, dt_archivo)
        grafica = Grafica(nombre_columna, nom_col, dt_archivo, tree_item_vista, self.get_id_grafica(), nombre_columna_vista, numero_grafica=numero_grafica, numero_archivo=numero_archivo)
        return grafica

    def get_archivo_en_combobox(self):
        nombre_archivo_en_combobox = self.combo.currentText()
        frame_archivo = None
        for archivo in self.archivos_csv:
            if nombre_archivo_en_combobox == archivo.get_nombre_archivo():
                frame_archivo = archivo.get_archivo()
                break
        return frame_archivo

    def ventana_butter(self):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            if self.widget_der.currentIndex() == -1:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")
                return

            widget_tab = self.widget_der.currentWidget()
            object_name = widget_tab.objectName()


            if not object_name == "Inicio":
                vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
                cant_graficas = vista.get_tree_widget_item().childCount()
                if cant_graficas >= 1:
                    graficas = vista.get_graficas()
                    ventana_filtro(self, graficas, self.widget_der.tabText(self.widget_der.currentIndex())).exec_()
                else:
                    QMessageBox.information(self, "Advertencia", "Debe insertar al menos una gráfica")
            else:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")

    def ventana_valores_en_grafica(self):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            if self.widget_der.currentIndex() == -1:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")
                return

            widget_tab = self.widget_der.currentWidget()
            object_name = widget_tab.objectName()

            if not object_name == "Inicio":
                vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
                cant_graficas = vista.get_tree_widget_item().childCount()
                if cant_graficas >= 1:
                    graficas = vista.get_graficas()
                    ventana_valores_en_graficas(self, graficas, self.widget_der.tabText(self.widget_der.currentIndex())).exec_()
                else:
                    QMessageBox.information(self, "Advertencia", "Debe insertar al menos una gráfica")
            else:
                QMessageBox.information(self, "Advertencia", "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")

    def ventana_comparar(self):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            if self.widget_der.currentIndex() == -1:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos 2 gráficas para comparar.")
                return

            widget_tab = self.widget_der.currentWidget()
            object_name = widget_tab.objectName()

            if not object_name == "Inicio":
                vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
                cant_graficas = vista.get_tree_widget_item().childCount()
                if cant_graficas >= 2:
                    graficas = vista.get_graficas()
                    ventana_comparar(self, graficas, self.widget_der.tabText(self.widget_der.currentIndex())).exec_()
                else:
                    QMessageBox.information(self, "Advertencia", "Debe insertar al menos dos gráficas para comparar")
            else:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos 2 gráficas para comparar.")

    def ventana_exportar_valores_pico(self):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            if self.widget_der.currentIndex() == -1:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")
                return

            widget_tab = self.widget_der.currentWidget()
            object_name = widget_tab.objectName()

            if not object_name == "Inicio":
                vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
                cant_graficas = vista.get_tree_widget_item().childCount()
                if cant_graficas >= 1:
                    graficas = vista.get_graficas()
                    ventana_exportarVP(self, graficas).exec_()
                else:
                    QMessageBox.information(self, "Advertencia", "Debe insertar al menos una gráfica")
            else:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")

    def ventana_rectificar(self):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            if self.widget_der.currentIndex() == -1:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")
                return

            widget_tab = self.widget_der.currentWidget()
            object_name = widget_tab.objectName()

            if not object_name == "Inicio":
                vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
                cant_graficas = vista.get_tree_widget_item().childCount()
                if cant_graficas >= 1:
                    graficas = vista.get_graficas()
                    ventana_rectificar(self, graficas, self.widget_der.tabText(self.widget_der.currentIndex())).exec_()
                else:
                    QMessageBox.information(self, "Advertencia", "Debe insertar al menos una gráfica.")
            else:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")

    def ventana_valoresEnBruto(self):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            if self.widget_der.currentIndex() == -1:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")
                return

            widget_tab = self.widget_der.currentWidget()
            object_name = widget_tab.objectName()

            if not object_name == "Inicio":
                vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
                cant_graficas = vista.get_tree_widget_item().childCount()
                if cant_graficas >= 1:
                    graficas = vista.get_graficas()
                    ventana_valoresEnBruto(self, graficas, self.widget_der.tabText(self.widget_der.currentIndex())).exec_()
                else:
                    QMessageBox.information(self, "Advertencia", "Debe insertar al menos una gráfica.")
            else:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")


    def ventana_cortarMain(self):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            if self.widget_der.currentIndex() == -1:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")
                return

            widget_tab = self.widget_der.currentWidget()
            object_name = widget_tab.objectName()

            if not object_name == "Inicio":
                vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
                cant_graficas = vista.get_tree_widget_item().childCount()
                if cant_graficas >= 1:
                    graficas = vista.get_graficas()
                    ventana_cortar(self, graficas, self.widget_der.tabText(self.widget_der.currentIndex())).exec_()
                else:
                    QMessageBox.information(self, "Advertencia", "Debe insertar al menos una gráfica.")
            else:
                QMessageBox.information(self, "Advertencia",
                                        "Debe crear una vista, posicionarte en ella e insertar al menos una gráfica.")

    def comparar_graficas(self, graficas):
        current_widget = self.widget_der.currentWidget()
        object_name = current_widget.objectName()
        if not object_name == "Inicio":
            widget_tab = self.widget_der.currentWidget()
            vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
            cant_graficas = len(graficas)
            if vista is not None:
                widget_tab.layout().removeWidget(vista.get_canvas())
                widget_tab.layout().removeWidget(vista.get_nav_toolbar())
                widget_tab.layout().removeWidget(vista.get_scroll())
                fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(18, 4))
                fig.canvas.mpl_connect('axes_enter_event', enter_axes)

                for x in range(cant_graficas):
                    archivo = graficas[x].get_archivo()
                    aux = self.setFiltros(archivo[graficas[x].get_nombre_columna_grafica()],
                                          graficas[x].get_filtro(),  graficas[x].get_fastfouriertransform())

                    recorte = self.recortarGraficos(aux,
                                                    archivo[graficas[x].get_nombre_columna_tiempo()],
                                                    graficas[x].get_recorte())
                    aux = recorte[0]
                    tiempoRecortado = recorte[1]

                    conOffset = self.aplicarOffset(aux, tiempoRecortado, graficas[x].get_offset())


                    line,= ax1.plot(tiempoRecortado,
                             conOffset, linewidth=0.3, label=f"{graficas[x].get_nombre_columna_grafica()}")

                    linebuilder = LineBuilder(line, ax1, graficas[x], self,True)
                    #ax1.ticklabel_format(useOffset=False, style='plain')
                    # ------------------------------------- Aspecto
                    ax1.set(xlabel='tiempo (s)', ylabel='voltage (mV)')
                    ax1.xaxis.set_minor_locator(MultipleLocator(0.5))
                    ax1.xaxis.set_major_locator(MultipleLocator(1))
                    ax1.tick_params(which='minor', length=5, width=1.5, color='r')
                    ax1.set_xmargin(0)
                    ax1.grid()
                    # -------------------------------------
                    # ax1.set_xlabel("s")
                    # ax1.set_ylabel("v")
                    ax1.legend()

                plt.close(fig)
                fig.tight_layout()

                widget_tab.layout().removeWidget(vista.get_canvas())
                widget_tab.layout().removeWidget(vista.get_nav_toolbar())
                widget_tab.layout().removeWidget(vista.get_scroll())

                canvas = FigureCanvas(fig)
                scroll_area = QScrollArea(widget_tab)
                scroll_area.setWidget(canvas)
                nav_toolbar = NavigationToolbar(canvas, widget_tab)

                vista.set_canvas(canvas)
                vista.set_scroll(scroll_area)
                vista.set_nav_toolbar(nav_toolbar)

                canvas.draw()
                widget_tab.layout().addWidget(nav_toolbar)
                widget_tab.layout().addWidget(scroll_area)

    def nueva_vista(self):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            vista = None
            widget = QWidget()
            widget.setStyleSheet(estilos.estilos_barritas_gucci_scroll_area())
            widget.setLayout(QVBoxLayout())
            widget.layout().setContentsMargins(5, 5, 5, 20)
            widget.layout().setSpacing(20)
            canvas = FigureCanvas()
            scroll_area = QScrollArea()
            scroll_area.setWidget(canvas)
            canvas.draw()
            widget.layout().addWidget(scroll_area)

            if len(self.vistas) == 0:

                widget.setObjectName("vista 1")
                self.widget_der.insertTab(1, widget, "vista 1")
                self.widget_der.setCurrentIndex(self.widget_der.count() - 1)
                item_vista = tree_widget_item_vista(name="vista 1", text="vista 1")
                item_vista.setIcon(0 , QIcon(config.ICONO_VISTA))
                vista = Vista(item_vista, widget, 1, 1)
                self.vistas.append(vista)
                self.treeView2.addTopLevelItem(item_vista)
            else:
                rango = len(self.vistas)
                bandera = False
                for i in range(rango):
                    for j in range(rango):
                        if self.vistas[j].get_numero_vista() == i + 1:
                            bandera = True
                            break
                    if bandera and rango == i + 1:
                        vista = "vista " + str(rango + 1)
                        widget.setObjectName(vista)
                        self.widget_der.insertTab(self.widget_der.count(), widget, vista)
                        self.widget_der.setCurrentIndex(self.widget_der.count() - 1)
                        item_vista = tree_widget_item_vista(name=vista, text=vista)
                        item_vista.setIcon(0, QIcon(config.ICONO_VISTA))
                        vista = Vista(item_vista, widget, rango + 1, rango + 1)
                        self.vistas.append(vista)
                        self.treeView2.addTopLevelItem(item_vista)
                        break
                    elif not bandera and rango >= i + 1:
                        vista = "vista " + str(i + 1)
                        widget.setObjectName(vista)
                        self.widget_der.insertTab(self.widget_der.count(), widget, vista)
                        self.widget_der.setCurrentIndex(self.widget_der.count() - 1)
                        item_vista = tree_widget_item_vista(name=vista, text=vista)
                        item_vista.setIcon(0, QIcon(config.ICONO_VISTA))
                        vista = Vista(item_vista, widget, i + 1, i + 1)
                        self.vistas.append(vista)
                        self.treeView2.addTopLevelItem(item_vista)
                        break
                    bandera = False
            vista.set_canvas(canvas)
            vista.set_scroll(scroll_area)
            self.vistas.sort(key=self.get_numero_vista)

            #RANCIADA PARA ORDER EL ARBOL DE LAS VISTAS *unico comentario*
            for v in self.vistas:
                self.treeView2.invisibleRootItem().removeChild(v.get_tree_widget_item())

            for v in self.vistas:
                self.treeView2.addTopLevelItem(v.get_tree_widget_item())

    def get_numero_vista(self,vista):
        return vista.get_numero_vista()

    def eliminar_csv(self):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            if not self.combo.currentText() == "Agregue un archivo csv":
                self.archivos_csv.pop(self.combo.currentIndex())
                self.combo.removeItem(self.combo.currentIndex())
                if self.combo.count() == 0:
                    self.combo.addItem("Agregue un archivo csv")

    def minimizar_panel(self):
        self.anim = QPropertyAnimation(self.widget_der, b"pos")
        self.anim.setEndValue(QPoint(20, 0))
        self.anim.setDuration(350)

        self.anim_2 = QPropertyAnimation(self.widget_der, b"size")
        self.anim_2.setEndValue(QSize(int((self.width - 15)), int(self.height * 0.9)))
        self.anim_2.setDuration(350)

        self.anim3 = QPropertyAnimation(self.widget_izq, b"pos")
        self.anim3.setEndValue(QPoint(-275, 0))
        self.anim3.setDuration(350)

        self.anim4 = QPropertyAnimation(self.widget_buttons_toggle, b"pos")
        self.anim4.setEndValue(QPoint(0, 0))
        self.anim4.setDuration(200)

        self.anim_group = QSequentialAnimationGroup()
        self.anim_group.addAnimation(self.anim3)
        self.anim_group.addAnimation(self.anim4)

        self.anim.start()
        self.anim_2.start()
        self.anim_group.start()

    def maximizar_panel(self):
        self.anim_wid_toggle_buttons = QPropertyAnimation(self.widget_buttons_toggle, b"pos")
        self.anim_wid_toggle_buttons.setEndValue(QPoint(-25, 0))
        self.anim_wid_toggle_buttons.setDuration(200)
        self.anim_wid_toggle_buttons.finished.connect(self.maximizar_panel_2)
        self.anim_wid_toggle_buttons.start()

    def maximizar_panel_2(self):
        self.anim_wid_der = QPropertyAnimation(self.widget_der, b"pos")
        self.anim_wid_der.setEndValue(QPoint(280, 0))
        self.anim_wid_der.setDuration(350)

        self.anim_2_wid_der = QPropertyAnimation(self.widget_der, b"size")
        self.anim_2_wid_der.setEndValue(QSize(int((self.width - 275)), int(self.height * 0.9)))
        self.anim_2_wid_der.setDuration(350)

        self.anim_wid_izq = QPropertyAnimation(self.widget_izq, b"pos")
        self.anim_wid_izq.setEndValue(QPoint(0, 0))
        self.anim_wid_izq.setDuration(350)

        self.anim_wid_der.start()
        self.anim_2_wid_der.start()
        self.anim_wid_izq.start()

    def eliminar_vista(self, tab_index):
        continuar = not chequearSiEstaRecortando(self)
        if continuar:
            widget = self.widget_der.widget(tab_index)
            cant_hijos = self.treeView2.topLevelItemCount()
            if widget.objectName() == "Inicio":
                self.widget_der.removeTab(tab_index)
            else:
                for x in range(cant_hijos):
                    hijo = self.treeView2.topLevelItem(x)
                    if isinstance(hijo, tree_widget_item_vista):
                        if hijo.get_name_object() == widget.objectName():
                            self.treeView2.takeTopLevelItem(self.treeView2.indexOfTopLevelItem(hijo))
                            self.eliminar_vista_de_array(widget)
                            self.widget_der.removeTab(tab_index)
                            break

    def eliminar_vista_de_array(self,widget):
        for i in range(len(self.vistas)):
            if self.vistas[i].get_widget() == widget:
                self.vistas.pop(i)
                break

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Guardar .csv", "ejemplo.csv",
                                                  "*", options=options)
        if fileName:
            return fileName


    def exportar_VP(self, graficas):
        ninguna_grafica_con_filtro = False

        if len(graficas) != 0:
            for grafica in graficas:
                if grafica.get_valores_pico_para_exportar() is None and grafica.get_valor_integral_para_exportar()\
                        is None and grafica.get_rms() is None:
                    graficas.remove(grafica)

        if len(graficas) != 0:
            if not ninguna_grafica_con_filtro:
                cabecera = []
                datos = []
                nombre = self.saveFileDialog()
                if nombre:
                    with open(nombre, 'w', newline='') as file:
                        writer = csv.writer(file)
                        for grafica in graficas:
                            writer.writerow([grafica.get_nombre_columna_grafica()])

                            if grafica.get_valores_pico_para_exportar() is not None:
                                valores_pico = grafica.get_valores_pico_para_exportar()

                                # Acá calculo el promedio usando numPy, le pasas un array y te lo calcula.
                                promedio = [f"Promedio: {np.mean(valores_pico)}"]

                                #Acá se concatenan los valores pico y el promedio así lo puedo insertar en la misma fila.
                                valores_pico_y_promedio = np.concatenate((valores_pico, promedio))
                                writer.writerow([f"Valores pico: "])
                                writer.writerow(valores_pico_y_promedio)

                            if grafica.get_valor_integral_para_exportar() is not None:
                                valor_integral = grafica.get_valor_integral_para_exportar()
                                writer.writerow([f"Valor de integral: "])
                                writer.writerow([valor_integral])

                            if grafica.get_rms() is not None:
                                valor_rms = grafica.get_rms()
                                writer.writerow([f"Valor RMS: "])
                                writer.writerow([valor_rms])

                            writer.writerow("")

                        QMessageBox.about(self, "Exito", "Se ha generado el archivo Excel correctamente.")
        else:
            QMessageBox.information(self, "Error", "Ninguna gráfica seleccionada tiene filtro.")

    def setCortandoGrafico(self,val,varios,ventanaRecortar): #esto lo uso para conectar el main con la ventana GUI
        setCortandoGraficoMain(val,varios,ventanaRecortar)

#funcion principal para cortar haciendo click
def setCortandoGraficoMain(val,varios,ventanaRecortar = None):
    global ventanaCortarInstance,cortando,min,max,cortandoVarios,graficaActual,listaDeAxes;
    cortandoVarios = varios
    if ventanaRecortar is not None:
        ventanaCortarInstance=ventanaRecortar
    cortando = val
    if not cortando and not cortandoVarios:
        ventanaCortarInstance.setRecorte(min,max)
        ventanaCortarInstance.seleccionar_todas_las_graficas()
        datosCorrectos = ventanaCortarInstance.aplicar_recorte()
        if not datosCorrectos:
            ventanaCortarInstance.show()

    elif not cortando and cortandoVarios:
        ventanaCortarInstance.setRecorte(min, max)
        num=0
        seleccionoAlguna = False
        for aux in listaDeAxes:
            if aux == graficaActual:
                ventanaCortarInstance.seleccionar_grafica(num)
                seleccionoAlguna=True
                break
            num=num+1
        if not seleccionoAlguna:
                ventanaCortarInstance.seleccionar_todas_las_graficas()
        datosCorrectos = ventanaCortarInstance.aplicar_recorte()
        if not datosCorrectos:
            ventanaCortarInstance.show()


#control para que no se haga otra cosa mientras se esta recortando
def chequearSiEstaRecortando(self):
    global cortando;
    if cortando:
        QMessageBox.information(self, "Advertencia","Termine de recortar la grafica")
        return True
    else:
        return False
#funcion para mostrar el recorte que se va a hacer, cuando se hace click
class LineBuilder:
    def __init__(self, line, axes,grafica,main,hayVarias=False):
        self.hayVarias = hayVarias
        self.main = main
        self.grafica = grafica
        self.axes = axes
        self.line = line
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)
        self.annotations = None
    def __call__(self, event):
        global cont,min,max,cortandoVarios,graficaActual

        if cortando:
            if not cortandoVarios:   #recortando una grafica
                if cont == 0 and self.grafica.get_recortandoConClick() == 0:  # inicio de recorte
                    self.grafica.set_recortandoConClick(1)
                    min = event.xdata
                    cont += 1
                    self.axes.annotate('Inicio Recorte: ' + "{0:.2f}".format(event.xdata),
                                       xy=(event.xdata, event.ydata),
                                       xytext=(event.xdata, 0))
                    ancho = (self.grafica.getLimitesTiempo()[1]-self.grafica.getLimitesTiempo()[0])/1000
                    circle1 = plt.Rectangle((event.xdata, 0), ancho, 99999, color='r',alpha = 0.7)
                    self.axes.add_patch(circle1)
                    self.line.figure.canvas.draw()
                elif cont == 1 and self.grafica.get_recortandoConClick() == 1:  # fin del recorte
                    max = event.xdata
                    self.axes.annotate('Fin Recorte: ' + "{0:.2f}".format(event.xdata), xy=(event.xdata, event.ydata),
                                       xytext=(event.xdata, 0))
                    ancho = (self.grafica.getLimitesTiempo()[1] - self.grafica.getLimitesTiempo()[0]) / 1000
                    circle1 = plt.Rectangle((event.xdata, 0), ancho, 99999, color='r',alpha = 0.7)
                    self.axes.add_patch(circle1)
                    self.line.figure.canvas.draw()
                    self.line.figure.canvas.flush_events()
                    time.sleep(1)
                    cont = 0
                    self.grafica.set_recortandoConClick(0)
                    setCortandoGraficoMain(False, cortandoVarios)
            else:               #recortando varias graficas
                if cont == 0 and self.grafica.get_recortandoConClick() == 0:  # inicio de recorte
                    if sacarSegundoParametroAxesSubplot(str(self.axes)) == graficaActual:
                        self.grafica.set_recortandoConClick(1)
                        min = event.xdata
                        cont += 1
                        self.axes.annotate('Inicio Recorte: ' + "{0:.2f}".format(event.xdata),
                                           xy=(event.xdata, event.ydata),
                                           xytext=(event.xdata, 0))
                        circle1 = plt.Rectangle((event.xdata, 0), 0.015, 99999, color='r')
                        self.axes.add_patch(circle1)
                        self.line.figure.canvas.draw()
                elif cont == 1 and self.grafica.get_recortandoConClick() == 1:  # fin del recorte
                    if sacarSegundoParametroAxesSubplot(str(self.axes)) == graficaActual:
                        max = event.xdata
                        self.axes.annotate('Fin Recorte: ' + "{0:.2f}".format(event.xdata), xy=(event.xdata, event.ydata),
                                           xytext=(event.xdata, 0))
                        circle1 = plt.Rectangle((event.xdata, 0), 0.015, 99999, color='r')
                        self.axes.add_patch(circle1)
                        self.line.figure.canvas.draw()
                        self.line.figure.canvas.flush_events()
                        time.sleep(1)
                        cont = 0
                        self.grafica.set_recortandoConClick(0)
                        setCortandoGraficoMain(False, cortandoVarios)
                elif not self.hayVarias:
                    QMessageBox.information(self.main, "Advertencia", "Termine de recortar la grafica Original")
            if event.inaxes!=self.line.axes: return



def enter_axes(event):
    global cortandoVarios,graficaActual
    if cortandoVarios:
        graficaActual=sacarSegundoParametroAxesSubplot(str(event.inaxes))
        event.canvas.draw()
    else:
        event.canvas.draw()

def leave_axes(event):
    global graficaActual
    graficaActual= None

def sacarSegundoParametroAxesSubplot(texto):
    aux = texto.split(",")
    return aux[1].split(";")[0]

def main():

    app = QApplication(sys.argv)
    pixmap = QPixmap(":/Static/img/splashscreenLibiam.jpg")
    splash = QSplashScreen(pixmap)
    splash.show()

    time.sleep(2)
    app.processEvents(QEventLoop.AllEvents)
    #cargando modulos

    ex = ventana_principal()
    splash.close()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()