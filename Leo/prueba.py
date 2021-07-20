from PyQt5 import QtWidgets, QtCore,QtGui
from PyQt5.QtWidgets import (QWidget,QTreeWidget,QListView,QToolBar,QComboBox,QTreeWidgetItem,QApplication,QLabel,QHBoxLayout,QVBoxLayout,QPushButton,QTabWidget,QScrollArea)
from PyQt5.Qt import QStandardItemModel,QStandardItem
from PyQt5.QtGui import QFont,QColor,QIcon
from PyQt5.QtCore import QModelIndex,QSize
import pandas
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import sys
import config
import funciones
import estilos


class ventana_principal(QWidget):

    def __init__(self, parent=None, *args):
        super(ventana_principal,self).__init__(parent=parent)
        self.initUI()

    def initUI(self):
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowTitle("LIBiAM")
        self.setWindowIcon(QIcon("static/img/LIBiAM.jpg"))
        self.resize(700, 500)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.archivos_csv = []

        # CONTENEDOR DEL TOL BAR
        self.widget_tool_bar = QWidget()
        self.layout().addWidget(self.widget_tool_bar, 1)

        # CONTENEDOR DEL PANEL Y GRÁFICAS
        self.widget_content = QWidget()
        self.widget_content.setLayout(QHBoxLayout())
        self.widget_content.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.widget_content, 9)

        # CONTENEDOR DE TREE GRÁFICAS
        self.widget_izq = QWidget()
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
        self.combo.currentIndexChanged.connect(self.xd)
        self.combo.setStyleSheet(estilos.estilos_combobox_archivos_csv())
        widget_lista_archivos.layout().addWidget(self.combo)

        # CONTENEDOR DE BOTONES PARA LOS ARCHIVOS CSV
        widget_botones_csv = QToolBar()
        widget_botones_csv.setIconSize(QSize(14,14))
        widget_botones_csv.setStyleSheet(estilos.estilos_toolbar_archvos_csv())
        icono_hide = QIcon("static/img/hide.svg")
        icono_remove = QIcon("static/img/eliminar.svg")
        icono_agregar = QIcon("static/img/add.svg")
        widget_botones_csv.addAction(icono_remove, 'eliminar', self.leo)
        widget_botones_csv.addAction(icono_agregar, 'agregar', self.agregar_csv)
        widget_botones_csv.addAction(icono_hide,'ocultar',self.leo)

        widget_archivos_csv.layout().addWidget(widget_lista_archivos,7)
        widget_archivos_csv.layout().addWidget(widget_botones_csv, 3)

        #ÁRBOL DE GRÁFICAS
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.widget_izq.layout().addWidget(self.tree_widget, 5)

        # ÁRBOL DE VISTAS
        self.treeView2 = QTreeWidget()
        self.treeView2.setStyleSheet(estilos.estilos_tree_widget_vistas())
        self.treeView2.setHeaderHidden(True)
        self.widget_izq.layout().addWidget(self.treeView2, 4)


    def agregar_csv(self):
        """
        Función para sagregar archivos .csv
        :return:
        """

        options = QtWidgets.QFileDialog.Options()
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccione un archivo", "","Archivos CSV (*.csv);", options=options)

        # Si se cancela la ventana emergente al seleccionar un archivo .csv
        if not filepath[0]:
            return

        nombre_archivo = funciones.get_nombre_csv(filepath[0])
        nuevo_arbol = self.get_nuevo_arbol(filepath[0])

        self.archivos_csv.append([filepath[0],nombre_archivo,nuevo_arbol])
        text_current_index = self.combo.currentText()

        if self.combo.count() == 1 and text_current_index == "Agregue un archivo csv":
            self.combo.addItem(nombre_archivo)
            self.widget_izq.layout().replaceWidget(self.tree_widget, nuevo_arbol)
            self.tree_widget = nuevo_arbol
            self.combo.removeItem(self.combo.currentIndex())
        else:
            self.combo.addItem(nombre_archivo)


    def get_nuevo_arbol(self,path):
        archivo = pandas.read_csv(path, encoding=config.ENCODING, skiprows=config.ROW_COLUMNS)
        # Con esta función se traen todas las electromiografías del archivo seleccionado.
        tree_widget = self.get_QTreeWidget()
        listaEMG = funciones.listar_emg(archivo)

        for i in range(len(listaEMG)):
            EMG = QTreeWidgetItem([f"EMG {i + 1}"])
            graficas = funciones.listar_emg_especifica(str(i + 1), archivo)

            for j in range(1, len(graficas), 2):
                grafica = QTreeWidgetItem([graficas[j]])
                EMG.addChild(grafica)

            tree_widget.addTopLevelItem(EMG)
        return tree_widget

    def get_QTreeWidget(self):
        treeWidget = QTreeWidget()
        treeWidget.setStyleSheet(estilos.estilos_tree_widget_graficas())
        treeWidget.setHeaderHidden(True)
        treeWidget.itemDoubleClicked.connect(self.mostrar)
        return treeWidget

    def xd(self):
        print("xd")

    def mostrar(self, item,col):
        index = self.widget_der.currentIndex()
        if not index == -1:

            grafica_vista = QTreeWidgetItem([item.text(col)])
            self.treeView2.topLevelItem(index).addChild(grafica_vista)
            self.treeView2.expandItem(self.treeView2.topLevelItem(index))

            if self.treeView2.topLevelItem(index).childCount() == 1:
                nuevo_tab = self.widget_der.currentWidget()
                nuevo_tab.setLayout(QVBoxLayout())
                nuevo_tab.layout().setContentsMargins(10, 10, 10, 35)
                nuevo_tab.layout().setSpacing(20)

                fig, axes = plt.subplots(nrows=1,ncols=1, figsize=(18, 4))
                emg = item.text(col)

                #CREAR FUNCIÓN EN SELF QUE RETORNE EL PATH DEL ARCHIVO QUE SE ENCUENTRA EN EL COMBO
                index_columna = self.archivo.columns.get_loc(emg)
                axes.plot(self.archivo.iloc[:,index_columna-1],self.archivo[emg], linewidth=0.3)
                axes.set_xlabel("s")
                axes.set_ylabel("v")
                axes.legend()

                plt.close(fig)
                fig.tight_layout()

                canvas = FigureCanvas(fig)
                canvas.draw()

                scroll_area = QScrollArea(nuevo_tab)
                scroll_area.setWidget(canvas)
                nuevo_tab.layout().addWidget(scroll_area)


    def nueva_vista(self):

        #AGREGAR NUEVO TAB A QTabWidget
        index = self.widget_der.count()
        self.widget_der.insertTab(index, QWidget(), "Vista %d" % (index + 1))
        self.widget_der.setCurrentIndex(index)

        #AGREGAR QTreeWidgetItem a Panel vista
        item_vista = QTreeWidgetItem(["Vista" + str((index + 1))])
        self.treeView2.addTopLevelItem(item_vista)


    def leo(self):
        print("xd")


    def eliminar_vista(self,tab_index):
        self.widget_der.removeTab(tab_index)

def main():
    app = QApplication(sys.argv)
    ex = ventana_principal()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()