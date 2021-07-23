from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QWidget,QAction ,QTreeWidget, QToolBar, QMenu,QComboBox, QTreeWidgetItem, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, QScrollArea)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QEvent,Qt,pyqtSignal,QPoint
import pandas
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import sys
import config
import funciones
from Static.styles import estilos
from Modelo.Archivo import Archivo
from Modelo.Grafica import Grafica
from Modelo.Vista import Vista

"""class tree_widget(QTreeWidget):
    rightClicked = pyqtSignal(QPoint)
    def __init__(self,parent=None):
        super(tree_widget, self).__init__()
        self.rightClicked.connect(self.handle_rightClicked)
"""
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
        self.vistas = []
        self.contador_vistas = 0

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
#        self.widget_izq.setMaximumHeight()
        self.widget_izq.setLayout(QVBoxLayout())
        self.widget_izq.layout().setContentsMargins(2, 0, 10, 20)
        self.widget_izq.layout().setSpacing(0)
        self.widget_content.layout().addWidget(self.widget_izq, 2)

        # CONTENEDOR DE LAS VISTAS
        self.widget_der = QTabWidget()
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
        self.widget_izq.layout().addWidget(widget_archivos_csv)

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
        self.widget_izq.layout().addWidget(self.tree_widget, 5)

        # ÁRBOL DE VISTAS
        self.treeView2 = QTreeWidget()
        self.treeView2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView2.customContextMenuRequested.connect(self.handle_rightClicked)
        self.treeView2.setStyleSheet(estilos.estilos_tree_widget_vistas())
        self.treeView2.setHeaderHidden(True)
        self.widget_izq.layout().addWidget(self.treeView2, 4)

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
        index = self.widget_der.indexOf(self.widget_der.currentWidget())
        if not index == -1 and item.parent() is not None:

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
        self.widget_der.insertTab(self.contador_vistas,widget,vista)
        self.widget_der.setCurrentIndex(self.widget_der.count()-1)

        #AGREGAR QTreeWidgetItem a Panel vista

        item_vista = QTreeWidgetItem([vista])
        self.vistas.append(Vista(item_vista,widget,self.contador_vistas))
        self.treeView2.addTopLevelItem(item_vista)


    def leo(self):
        print("xd")



    def eliminar_vista(self,tab_index):

        widget = self.widget_der.currentWidget()
        index_widget = self.widget_der.indexOf(widget)
        self.treeView2.takeTopLevelItem(index_widget).setDisabled(True)
        self.widget_der.removeTab(tab_index)

def main():
    app = QApplication(sys.argv)
    ex = ventana_principal()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()