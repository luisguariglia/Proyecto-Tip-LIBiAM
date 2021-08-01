from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import (QLabel,QGraphicsDropShadowEffect,QMenuBar,QFileDialog,QWidget,QAction, QGraphicsScene, QGraphicsView ,QTreeWidget, QToolBar, QMenu,QComboBox, QTreeWidgetItem, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, QScrollArea)
from PyQt5.QtGui import QIcon,QFont,QFontDatabase,QPixmap
from PyQt5.QtCore import QSize, QEvent,Qt,pyqtSignal,QPoint,QEasingCurve,QPropertyAnimation,QDir
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
import pandas
import os
import config
import funciones
import sys
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from ConfigVentanas.butterConfig import butterConfigClass
from ConfigVentanas.ValoresEnGrafica import valoresEnGraficaClass
from Helpers import filtersHelper
from Static.Strings import strings
from Static.styles import estilos
from Modelo.Vista import Vista
from Modelo.Archivo import Archivo
from Modelo.Grafica import Grafica
from GUI.GUI import ventana_filtro



def load_fonts_from_dir(directory):
    families = set()
    for fi in QDir(directory).entryInfoList(["*.ttf"]):
        _id = QFontDatabase.addApplicationFont(fi.absoluteFilePath())
        families |= set(QFontDatabase.applicationFontFamilies(_id))
    return families


class tree_widget_item_vista(QTreeWidgetItem):
    def __init__(self,text,name):
        super(tree_widget_item_vista, self).__init__()
        self.setText(0,text)
        self.name = name


    def set_name_object(self,name):
        self.name = name

    def get_name_object(self):
        return self.name

class ventana_principal(QWidget):

    def __init__(self, parent=None, *args):
        super(ventana_principal,self).__init__(parent=parent)
        self.initUI()

    def initUI(self):
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowTitle("LIBiAM")
        self.setWindowIcon(QIcon("Static/img/LIBiAM.jpg"))
        self.resize(700, 500)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.archivos_csv = []

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

        Guardar = QAction("Guardar", self)
        # Nuevo.triggered.connect(quit)
        Guardar.setEnabled(False)
        actionFile.addAction(Guardar)


        actionFile.addSeparator()
        Salir = QAction("Salir", self)
        Salir.triggered.connect(quit)
        actionFile.addAction(Salir)

        editarMenu=menubar.addMenu("Editar")
        # editarMenu.addAction("")

        filtradoMenu = menubar.addMenu("Filtrado")

        Config = QAction("Configuracion", self)
        # Nuevo.triggered.connect(quit)
        Config.setEnabled(False)
        filtradoMenu.addAction(Config)

        vista=menubar.addMenu("Vista")
        nuevaV = QAction("Nueva Vista", self)
        nuevaV.triggered.connect(self.nueva_vista)
        vista.addAction(nuevaV)

        ayudaMenu=menubar.addMenu("Ayuda")
        Doc = QAction("Documentacion", self)
        # Nuevo.triggered.connect(quit)
        Doc.setEnabled(False)
        ayudaMenu.addAction(Doc)

        Sobre = QAction("Sobre Nosotros", self)
        Sobre.triggered.connect(self.ventana_inicio)
        Sobre.setEnabled(False)
        ayudaMenu.addAction(Sobre)

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
        btn_butter_filter = QPushButton("Butter Filter")
        btn_butter_filter.clicked.connect(self.ventana_butter)
        btn_butter_filter.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        btn_valores_en_grafica = QPushButton("Valores en Gráfica")
        btn_valores_en_grafica.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())
        btn_cortar = QPushButton("Cortar")
        btn_cortar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())
        btn_rectificar = QPushButton("Rectificar")
        btn_rectificar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())


        wid_derecha_toolbar.layout().addWidget(btn_butter_filter)
        wid_derecha_toolbar.layout().addWidget(btn_valores_en_grafica)
        wid_derecha_toolbar.layout().addWidget(btn_cortar)
        wid_derecha_toolbar.layout().addWidget(btn_rectificar)

        self.widget_toolbar.layout().addWidget(wid_izquierda_toolbar, 2)
        self.widget_toolbar.layout().addWidget(wid_derecha_toolbar, 8)

        botonesFiltrado = uic.loadUi('Static/uiFiles/botonesGraficado.ui')

        self.layout().addWidget(self.widget_toolbar, 1)



        # CONTENEDOR DEL PANEL Y GRÁFICAS
        self.widget_content = QWidget()
        self.widget_content.setLayout(QHBoxLayout())
        self.widget_content.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.widget_content, 9)

        self.width = self.widget_content.screen().geometry().width()
        self.height = self.widget_content.screen().geometry().height()

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
        self.widget_buttons_toggle.setStyleSheet("QWidget{border:0px solid black;}")
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
        icono_hide = QIcon("Static/img/hide.svg")
        icono_remove = QIcon("Static/img/eliminar.svg")
        icono_agregar = QIcon("Static/img/add.svg")
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
        self.treeView2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView2.customContextMenuRequested.connect(self.handle_rightClicked)
        self.treeView2.setStyleSheet(estilos.estilos_tree_widget_vistas())
        self.treeView2.setHeaderHidden(True)
        self.widget_izq.layout().addWidget(self.treeView2, 4)

        """# filtros
        self.ventanaConfig = butterConfigClass(self)
        self.button = self.findChild(QPushButton, 'butterBtn')
        self.button.clicked.connect(self.ventanaConfig.mostrar)

        # picos
        self.picosConfig = valoresEnGraficaClass(self)
        self.buttonPícos = self.findChild(QtWidgets.QPushButton, 'valoresGraficaBtn')
        self.buttonPícos.clicked.connect(self.picosConfig.mostrar)"""

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
        widget_header.layout().setAlignment(Qt.AlignLeft)
        widget_header.setStyleSheet(estilos.estilos_widget_header_inicio())

        widget_contenido = QWidget()
        widget_contenido.setLayout(QHBoxLayout())
        widget_contenido.setStyleSheet(estilos.estilos_widget_content())
        widget_contenido.layout().setContentsMargins(6,10,0,0)
        widget_contenido.layout().setSpacing(0)

        img_ANEP_UTU = QPixmap('Static/img/utu.png')
        lab_ANEP_UTU = QLabel()
        lab_ANEP_UTU.setFixedWidth(img_ANEP_UTU.width())
        lab_ANEP_UTU.setPixmap(img_ANEP_UTU)

        img_LIBiAM = QPixmap('Static/img/LIBiAM2.jpg')
        lab_LIBiAM = QLabel()
        lab_LIBiAM.setFixedWidth(img_LIBiAM.width())
        lab_LIBiAM.setPixmap(img_LIBiAM)

        img_UDELAR = QPixmap('Static/img/udelar2.png')
        lab_UDELAR = QLabel()
        lab_UDELAR.setFixedWidth(img_UDELAR.width())
        lab_UDELAR.setPixmap(img_UDELAR)

        img_UTEC = QPixmap('Static/img/utec.png')
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

        img1 = QPixmap('Static/img/img_content3.jpg')
        img2 = QPixmap('Static/img/img_content2.jpg')
        img3 = QPixmap('Static/img/img_content.jpg')

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
            print_shrek = QAction("Print Shrek")
            print_shrek.triggered.connect(lambda checked, item=item: self.print_shrek())
            menu.addAction(print_shrek)
        elif item.parent() is None:
            print_burro = QAction("Print Burro")
            print_burro.triggered.connect(lambda checked, item=item: self.print_burro())
            menu.addAction(print_burro)
        menu.exec_(self.treeView2.viewport().mapToGlobal(pos))

    def print_shrek(self):
        print("                           \n"
        "⢀⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠸⡇⠀⠿⡀⠀⠀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀\n"
        " ⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆\n"
        "⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠁⠸⣼⡿\n"
        "⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉⠀⠀⠀⠀⠀\n"
        "⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀\n"
        "⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀\n"
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⠿⠿⠿⠛⠉"
              )
    def print_burro(self):
        print("Burro")

    def agregar_csv(self):
        """
            Función para agregar archivos .csv
        :return:
        """

        options = QFileDialog.Options()
        filepath = QFileDialog.getOpenFileName(self, "Seleccione un archivo", "",config.FILES_CSV, options=options)

        # Si se cancela la ventana emergente al seleccionar un archivo .csv
        if not filepath[0]:
            return

        nombre_archivo = funciones.get_nombre_csv(filepath[0])
        frame_archivo = pandas.read_csv(filepath[0], encoding=config.ENCODING, skiprows=config.ROW_COLUMNS)
        archivo = Archivo(nombre_archivo,frame_archivo)
        archivo.agregar_electromiografias(frame_archivo)

        self.archivos_csv.append(archivo)
        text_current_index = self.combo.currentText()

        if text_current_index == "Agregue un archivo csv":
            self.combo.addItem(nombre_archivo)
            self.combo.removeItem(self.combo.currentIndex())
        else:
            self.combo.addItem(nombre_archivo)

    def rectificarEMG(self):
        print("Texto de Ejemplo")

    def actualizar_tree(self):
        self.tree_widget.clear()
        nombre_archivo = self.combo.currentText()
        for archivo in self.archivos_csv:
            if nombre_archivo == archivo.get_nombre_archivo():
                for emg in archivo.get_electromiografias():
                    EMG = QTreeWidgetItem([emg.get_nombre_corto()])

                    graficas = emg.get_graficas()
                    for grafica in graficas:
                        grafica = QTreeWidgetItem([grafica.get_nombre_columna_grafica()])
                        EMG.addChild(grafica)

                    self.tree_widget.addTopLevelItem(EMG)


    def agregar_grafica_a_vista(self, item, col):
        current_widget = self.widget_der.currentWidget()
        index = self.widget_der.indexOf(current_widget)

        if not index == -1 and item.parent() is not None:
            object_name = current_widget.objectName()
            if not object_name == "Inicio":

                grafica_vista = QTreeWidgetItem([item.text(col)])
                widget_tab = self.widget_der.currentWidget()
                vista : Vista = Vista.get_vista_by_widget(self.vistas,widget_tab)
                vista.get_tree_widget_item().addChild(grafica_vista)
                grafica : Grafica = self.get_grafica(item.text(col))
                vista.agregar_grafica(grafica)
                cant_vistas = vista.get_tree_widget_item().childCount()
                self.listar_graficas(False)

                self.treeView2.expandItem(vista.get_tree_widget_item())


    def setFiltros(self, datos, datosFiltrado):
        # self.leerDatos()  # esto hay que hacerlo mas eficiente
        filter_signal = filtersHelper.butterFilter(datos, datosFiltrado)
        filter_signal = filtersHelper.butterFilterDos(filter_signal)
        filter_signal = filtersHelper.RMS(filter_signal)
        return filter_signal


    def listar_graficas(self, despues_de_filtro):
        current_widget = self.widget_der.currentWidget()
        object_name = current_widget.objectName()
        if not object_name == "Inicio":
            widget_tab = self.widget_der.currentWidget()
            vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
            cant_graficas = vista.get_tree_widget_item().childCount()
            if vista is not None:

                if cant_graficas == 1:

                    if despues_de_filtro:
                        widget_tab.layout().removeWidget(vista.get_canvas())
                        widget_tab.layout().removeWidget(vista.get_nav_toolbar())
                        widget_tab.layout().removeWidget(vista.get_scroll())

                    widget_tab.setLayout(QVBoxLayout())
                    widget_tab.layout().setContentsMargins(10, 10, 10, 35)
                    widget_tab.layout().setSpacing(20)
                    scroll_area = QScrollArea(widget_tab)

                    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(18, 4))
                    graficas = vista.get_graficas()
                    archivo = graficas[0].get_archivo()
                    aux = self.setFiltros(archivo[graficas[0].get_nombre_columna_grafica()], graficas[0].get_filtro())
                    axes.plot(archivo[graficas[0].get_nombre_columna_tiempo()],
                              aux, linewidth=0.3)
                    plt.close(fig)
                    fig.tight_layout()

                    canvas = FigureCanvas(fig)
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
                    graficas = vista.get_graficas()

                    for x in range(cant_graficas):
                        archivo = graficas[x].get_archivo()
                        aux = self.setFiltros(archivo[graficas[x].get_nombre_columna_grafica()], graficas[x].get_filtro())
                        axes[x].plot(archivo[graficas[x].get_nombre_columna_tiempo()],
                                     aux, linewidth=0.3)
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


    def get_grafica(self,nombre_columna):
        dt_archivo = self.get_archivo_en_combobox()
        index_xs = dt_archivo.columns.get_loc(nombre_columna)-1
        nom_col = dt_archivo.columns[index_xs]
        grafica = Grafica(nombre_columna,nom_col,dt_archivo)
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
        widget_tab = self.widget_der.currentWidget()
        object_name = widget_tab.objectName()

        if not object_name == "Inicio":
            vista: Vista = Vista.get_vista_by_widget(self.vistas, widget_tab)
            graficas = vista.get_graficas()
            ventana_filtro(self, graficas).exec_()
        else:
            ventana_filtro(self).exec_()


    def nueva_vista(self):
        # AGREGAR NUEVO TAB A QTabWidget
        self.contador_vistas += 1
        vista = "vista " + str(self.contador_vistas)
        widget = QWidget()
        widget.setObjectName(vista)
        self.widget_der.insertTab(self.contador_vistas, widget, vista)
        self.widget_der.setCurrentIndex(self.widget_der.count() - 1)

        # AGREGAR QTreeWidgetItem a Panel vista
        item_vista = tree_widget_item_vista(name=vista, text=vista)
        self.vistas.append(Vista(item_vista, widget, self.contador_vistas))
        self.treeView2.addTopLevelItem(item_vista)


    def eliminar_csv(self):
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
        self.anim4.setDuration(450)

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


def main():
    app = QApplication(sys.argv)
    ex = ventana_principal()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()