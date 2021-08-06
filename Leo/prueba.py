from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QWidget,QLabel,QAction,QGraphicsDropShadowEffect,QTreeWidget,QLayout,QToolBar, QMenu,QComboBox, QTreeWidgetItem, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, QScrollArea)
from PyQt5.QtGui import QIcon,QPixmap,QFont,QFontDatabase
from PyQt5.QtCore import QSize, QEvent,Qt,pyqtSignal,QPoint,QTimer,QEasingCurve,QPropertyAnimation,QDir
import pandas
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import sys
import config
import funciones
from Static.Strings import strings
from Static.styles import estilos
from Modelo.Archivo import Archivo
from Modelo.Grafica import Grafica
from Modelo.Vista import Vista


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

        #VALORES PANEL VISTAS
        self.vistas = []
        self.contador_vistas = 0

        #VALORES DE VISTA INICIO
        self.contador = 0
        self.lista_labels = []

        # CONTENEDOR DEL TOL BAR
        self.widget_tool_bar = QWidget()
        #self.widget_tool_bar.setMaximumHeight(int)
        self.layout().addWidget(self.widget_tool_bar, 1)

        # CONTENEDOR DEL PANEL Y GRÁFICAS
        self.widget_content = QWidget()
        self.widget_content.setLayout(QHBoxLayout())
        self.widget_content.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.widget_content, 9)

        # CONTENEDOR DE TREE GRÁFICAS
        self.widget_izq = QWidget()
        self.widget_izq.setLayout(QHBoxLayout())
        self.widget_izq.setStyleSheet("background-color:white;margin:0px;padding:0px;")
        self.widget_izq.layout().setContentsMargins(0, 0, 0, 0)
        self.widget_izq.layout().setSpacing(0)
        self.widget_content.layout().addWidget(self.widget_izq, 2)

        self.widget_buttons_toggle = QWidget()
        self.widget_buttons_toggle.setStyleSheet("border:1px solid gray;")
        self.widget_buttons_toggle.setMaximumWidth(20)
        self.widget_buttons_toggle.setLayout(QVBoxLayout())

        self.widget_paneles = QWidget()
        self.widget_paneles.setLayout(QVBoxLayout())
        self.widget_paneles.layout().setContentsMargins(2, 0, 0, 20)
        self.widget_paneles.layout().setSpacing(0)

        self.widget_izq.layout().addWidget(self.widget_buttons_toggle,1)
        self.widget_izq.layout().addWidget(self.widget_paneles,9)


        # CONTENEDOR DE LAS VISTAS
        self.widget_der = QTabWidget()
        self.ventana_inicio()
        self.widget_der.setMovable(True)
        self.widget_der.setTabsClosable(True)
        self.widget_der.tabCloseRequested.connect(self.eliminar_vista)
        self.widget_content.layout().addWidget(self.widget_der, 8)

        # RANCIADA
        btn = QPushButton(self.widget_tool_bar)
        btn.setText("nueva vista")
        btn.pressed.connect(self.nueva_vista)

        #CONTENEDOR DE COMBOBOX Y TOOLBAR DE ARCHIVOS CSV
        widget_archivos_csv = QWidget()
        widget_archivos_csv.setLayout(QHBoxLayout())
        widget_archivos_csv.layout().setContentsMargins(0,0,0,0)
        widget_archivos_csv.layout().setSpacing(0)
        widget_archivos_csv.setStyleSheet("background-color:white;border:1px solid gray;border-bottom:0px;")
        widget_archivos_csv.setFixedHeight(24)
        self.widget_paneles.layout().addWidget(widget_archivos_csv)

        #CONTENEDOR DE LOS ARCHIVOS CSV
        widget_lista_archivos = QWidget()
        widget_lista_archivos.setLayout(QVBoxLayout())
        widget_lista_archivos.layout().setContentsMargins(2,2,2,2)
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
        widget_botones_csv.addAction(icono_remove, 'eliminar', self.leo)
        widget_botones_csv.addAction(icono_agregar, 'agregar', self.agregar_csv)
        widget_botones_csv.addAction(icono_hide,'ocultar',self.leo)

        widget_archivos_csv.layout().addWidget(widget_lista_archivos,7)
        widget_archivos_csv.layout().addWidget(widget_botones_csv, 3)

        #ÁRBOL DE GRÁFICAS
        self.tree_widget = QTreeWidget()
        self.tree_widget.setStyleSheet(estilos.estilos_tree_widget_graficas())
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemDoubleClicked.connect(self.agregar_grafica_a_vista)
        self.widget_paneles.layout().addWidget(self.tree_widget, 5)

        # ÁRBOL DE VISTAS
        self.treeView2 = QTreeWidget()
        self.treeView2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView2.customContextMenuRequested.connect(self.handle_rightClicked)
        self.treeView2.setStyleSheet(estilos.estilos_tree_widget_vistas())
        self.treeView2.setHeaderHidden(True)
        self.widget_paneles.layout().addWidget(self.treeView2, 4)

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
        print("Shrek")

    def print_burro(self):
        print("Burro")

    def agregar_csv(self):
        """
            Función para agregar archivos .csv
        :return:
        """

        options = QtWidgets.QFileDialog.Options()
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccione un archivo", "",config.FILES_CSV, options=options)

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
                grafica = self.get_grafica(item.text(col))
                vista.agregar_grafica(grafica)
                cant_vistas = vista.get_tree_widget_item().childCount()
                if vista is not None:

                    if cant_vistas == 1:
                        widget_tab.setLayout(QVBoxLayout())
                        widget_tab.layout().setContentsMargins(10, 10, 10, 35)
                        widget_tab.layout().setSpacing(20)
                        scroll_area = QScrollArea(widget_tab)

                        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(18, 4))
                        graficas = vista.get_graficas()
                        archivo = graficas[0].get_archivo()
                        axes.plot(archivo[graficas[0].get_nombre_columna_tiempo()],
                                  archivo[graficas[0].get_nombre_columna_grafica()], linewidth=0.3)
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

                    elif cant_vistas > 1:
                        fig, axes = plt.subplots(nrows=cant_vistas, ncols=1, figsize=(18,4* cant_vistas))
                        graficas = vista.get_graficas()


                        for x in range(cant_vistas):
                            archivo = graficas[x].get_archivo()
                            axes[x].plot(archivo[graficas[x].get_nombre_columna_tiempo()],
                                  archivo[graficas[x].get_nombre_columna_grafica()], linewidth=0.3)
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

                    self.treeView2.expandItem(self.treeView2.topLevelItem(index))

    def get_grafica(self,nombre_columna):
        dt_archivo = self.get_archivo_en_combobox()
        index_xs = dt_archivo.columns.get_loc(nombre_columna)-1
        nom_col = dt_archivo.columns[index_xs]
        return Grafica(nombre_columna,nom_col,dt_archivo)

    def get_archivo_en_combobox(self):
        nombre_archivo_en_combobox = self.combo.currentText()
        frame_archivo = None
        for archivo in self.archivos_csv:
            if nombre_archivo_en_combobox == archivo.get_nombre_archivo():
                frame_archivo = archivo.get_archivo()
                break
        return frame_archivo

    def nueva_vista(self):

        #AGREGAR NUEVO TAB A QTabWidget
        self.contador_vistas += 1
        vista = "vista " + str(self.contador_vistas)
        widget = QWidget()
        widget.setObjectName(vista)
        self.widget_der.insertTab(self.contador_vistas,widget,vista)
        self.widget_der.setCurrentIndex(self.widget_der.count()-1)

        #AGREGAR QTreeWidgetItem a Panel vista
        item_vista = tree_widget_item_vista(name=vista,text=vista)
        self.vistas.append(Vista(item_vista,widget,self.contador_vistas))
        self.treeView2.addTopLevelItem(item_vista)


    def leo(self):
        print("xd")

    def ventana_inicio(self):
        shadow = QGraphicsDropShadowEffect(blurRadius=20, xOffset=6, yOffset=6)
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
        widget_izquierda_section.layout().setAlignment(Qt.AlignTop)

        widget_labels = QWidget()
        widget_labels.setLayout(QVBoxLayout())
        widget_labels.setStyleSheet("QWidget{background-color:white;border-radius:4px} QLabel{margin:0px;}")
        widget_labels.setGraphicsEffect(shadow2)
        widget_labels.layout().setSpacing(16)
        widget_labels.layout().setContentsMargins(14,10,10,30)

        QFontDatabase.addApplicationFont("Static/fonts/Roboto-Light.ttf")
        label2.setFont(QFont('Roboto',12))

        widget_labels.layout().addWidget(label1)
        widget_labels.layout().addWidget(label2)

        widget_izquierda_section.layout().addWidget(widget_labels)
        widget_derecha_section = QWidget()

        widget_derecha_section.setLayout(QVBoxLayout())
        widget_derecha_section.layout().setContentsMargins(40,15,40,15)
        widget_derecha_section.layout().setAlignment(Qt.AlignTop)

        widget_contenedor_imagenes = QWidget()
        widget_contenedor_imagenes.setLayout(QVBoxLayout())
        widget_contenedor_imagenes.layout().setAlignment(Qt.AlignCenter)
        widget_contenedor_imagenes.layout().setContentsMargins(0,0,0,0)
        #widget_contenedor_imagenes.setStyleSheet("background-color:#FAFAFA;padding:0x;margin:0px;")

        widget_contenedor_imagenes.setGraphicsEffect(shadow)
        widget_derecha_section.layout().addWidget(widget_contenedor_imagenes)

        widget_imagenes = QWidget(widget_contenedor_imagenes)
        widget_imagenes.setFixedWidth(452)
        widget_imagenes.setFixedHeight(270)
        widget_contenedor_imagenes.layout().addWidget(widget_imagenes)

        img1 = QPixmap('Static/img/img_content3.jpg')
        img2 = QPixmap('Static/img/img_content2.jpg')
        img3 = QPixmap('Static/img/img_content1.jpg')

        lab1 = QLabel(widget_imagenes)
        lab1.setPixmap(img1)
        lab1.move(-500, 0)

        lab2 = QLabel(widget_imagenes)
        lab2.move(0,0)
        lab2.setPixmap(img2)

        lab3 = QLabel(widget_imagenes)
        lab3.move(-500, 0)
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
        self.animation1.setEndValue(QPoint(450, 0))
        self.animation1.setDuration(1000)

        self.animation2 = QPropertyAnimation(self)
        self.animation2.setPropertyName(b'pos')
        self.animation2.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation2.setStartValue(QPoint(-450, 0))
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


    def eliminar_vista(self,tab_index):

        widget = self.widget_der.widget(tab_index)
        cant_hijos = self.treeView2.topLevelItemCount()
        if widget.objectName() == "Inicio":
            self.widget_der.removeTab(tab_index)
        else:
            for x in range(cant_hijos):
                hijo = self.treeView2.topLevelItem(x)
                if isinstance(hijo,tree_widget_item_vista):
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