from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from matplotlib import pyplot as plt

from Static.styles import estilos
from Modelo.Grafica import Grafica
from Modelo.Filtro import Filtro


class ventana_filtro(QtWidgets.QDialog):
    def __init__(self, parent=None,graficas=None):
        super(ventana_filtro, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Butter Filter - Vista 1")
        self.setFixedSize(770, 470)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10,0,10,10)
        self.layout().setSpacing(15)

        #PARAMETROS
        self.parent = parent
        self.graficas = graficas

        wid_izquierda = QtWidgets.QWidget()
        wid_derecha = QtWidgets.QWidget()

        #SOMBRAS
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        wid_izquierda.setGraphicsEffect(shadow)
        wid_derecha.setGraphicsEffect(shadow2)

        #ESTILOS
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")
        wid_derecha.setStyleSheet("background-color:white; border-radius:4px;")

        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())
        wid_derecha.setLayout(QtWidgets.QVBoxLayout())

        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        label_2 = QtWidgets.QLabel("CONFIGURAR FILTRO")
        label_2.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)
        wid_derecha.layout().addWidget(label_2,1)

        #GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = QtWidgets.QTreeWidgetItem([nom_col])
                item.setCheckState(0,Qt.Unchecked)
                self.tree_graficas.addTopLevelItem(item)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        #CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()
        wid_btn.setStyleSheet("QWidget{margin-left:5px;")

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QVBoxLayout())
        wid_btn.layout().setAlignment(Qt.AlignLeft)
        wid_btn.layout().addWidget(btn_aplicar_a_todas)

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        #GROUP BOX VALORES FILTRO
        wid_content_der = QtWidgets.QWidget()
        wid_content_der.setLayout(QtWidgets.QVBoxLayout())
        wid_content_der.layout().setAlignment(Qt.AlignTop)
        wid_content_der.layout().setContentsMargins(10,0,0,0)
        wid_content_der.layout().setSpacing(15)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)

        #ORDER
        wid_label_order = QtWidgets.QWidget()
        wid_label_order.setLayout(QtWidgets.QHBoxLayout())

        wid_spiner_order = QtWidgets.QWidget()
        wid_spiner_order.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_order.layout().setContentsMargins(0,0,0,0)
        wid_spiner_order.layout().setAlignment(Qt.AlignRight)

        label_order = QtWidgets.QLabel("ORDER OF THE FILTER")
        label_order.setFont(font)
        wid_label_order.layout().addWidget(label_order)

        self.spin_box = QtWidgets.QSpinBox()
        self.spin_box.setFixedWidth(60)
        self.spin_box.setValue(3)
        self.spin_box.setStyleSheet(estilos.estilos_spinbox_filtros())

        wid_label_order.layout().addWidget(label_order)
        wid_spiner_order.layout().addWidget(self.spin_box)

        wid_order = QtWidgets.QWidget()
        wid_order.setLayout(QtWidgets.QHBoxLayout())
        wid_order.layout().setContentsMargins(0,0,0,0)
        wid_order.layout().addWidget(wid_label_order, 5)
        wid_order.layout().addWidget(wid_spiner_order, 5)

        #ARRAY LIKE
        wid_label_array_like = QtWidgets.QWidget()
        wid_label_array_like.setLayout(QtWidgets.QHBoxLayout())

        wid_spiner_array_like = QtWidgets.QWidget()
        wid_spiner_array_like.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_array_like.layout().setContentsMargins(0,0,0,0)
        wid_spiner_array_like.layout().setSpacing(8)
        wid_spiner_array_like.layout().setAlignment(Qt.AlignRight)


        label_array_like = QtWidgets.QLabel("ARRAY LIKE")
        label_array_like.setFont(font)

        self.spiner_array_a = QtWidgets.QDoubleSpinBox()
        self.spiner_array_a.setFixedWidth(60)
        self.spiner_array_a.setValue(0.02)
        self.spiner_array_a.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        self.spiner_array_b = QtWidgets.QDoubleSpinBox()
        self.spiner_array_b.setFixedWidth(60)
        self.spiner_array_b.setValue(0.4)
        self.spiner_array_b.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_spiner_array_like.layout().addWidget(self.spiner_array_a)
        wid_spiner_array_like.layout().addWidget(self.spiner_array_b)
        wid_label_array_like.layout().addWidget(label_array_like)

        wid_array_like = QtWidgets.QWidget()
        wid_array_like.setLayout(QtWidgets.QHBoxLayout())
        wid_array_like.layout().setContentsMargins(0,0,0,0)
        wid_array_like.layout().addWidget(wid_label_array_like, 5)
        wid_array_like.layout().addWidget(wid_spiner_array_like, 5)

        #BTYPE
        label_btype = QtWidgets.QLabel("BTYPE")
        label_btype.setFont(font)
        wid_label_btype = QtWidgets.QWidget()
        wid_label_btype.setLayout(QtWidgets.QHBoxLayout())
        wid_label_btype.layout().addWidget(label_btype)

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
        wid_combobox_btype.layout().setContentsMargins(0,0,0,0)
        wid_combobox_btype.layout().setAlignment(Qt.AlignRight)
        wid_combobox_btype.layout().addWidget(self.combobox_btype)

        wid_btype = QtWidgets.QWidget()
        wid_btype.setLayout(QtWidgets.QHBoxLayout())
        wid_btype.layout().setContentsMargins(0,0,0,0)

        wid_btype.layout().addWidget(wid_label_btype, 5)
        wid_btype.layout().addWidget(wid_combobox_btype ,5)

        #ANALOG
        label_analog = QtWidgets.QLabel("ANALOG")
        label_analog.setFont(font)

        wid_label_analog = QtWidgets.QWidget()
        wid_label_analog.setLayout(QtWidgets.QHBoxLayout())
        wid_label_analog.layout().addWidget(label_analog)

        self.combobox_analog = QtWidgets.QComboBox()
        self.combobox_analog.setFixedWidth(150)
        self.combobox_analog.setStyleSheet(estilos.estilos_combobox_filtro())
        self.combobox_analog.addItem("True")
        self.combobox_analog.addItem("False")
        self.combobox_analog.setCurrentIndex(0)

        wid_combobox_analog = QtWidgets.QWidget()
        wid_combobox_analog.setLayout(QtWidgets.QHBoxLayout())
        wid_combobox_analog.layout().setContentsMargins(0,0,0,0)
        wid_combobox_analog.layout().setAlignment(Qt.AlignRight)
        wid_combobox_analog.layout().addWidget(self.combobox_analog)

        wid_analog = QtWidgets.QWidget()
        wid_analog.setLayout(QtWidgets.QHBoxLayout())
        wid_analog.layout().setContentsMargins(0,0,0,0)

        wid_analog.layout().addWidget(wid_label_analog, 5)
        wid_analog.layout().addWidget(wid_combobox_analog, 5)

        #SE AGREGA CADA CONFIGURACIÓN EN ESTE ORDEN A LA VISTA
        wid_content_der.layout().addWidget(wid_order)
        wid_content_der.layout().addWidget(wid_array_like)
        wid_content_der.layout().addWidget(wid_btype)
        wid_content_der.layout().addWidget(wid_analog)

        #BOTÓN APLICAR FILTROS
        wid_btn_aplicar = QtWidgets.QWidget()
        wid_btn_aplicar.setLayout(QtWidgets.QHBoxLayout())
        wid_btn_aplicar.layout().setContentsMargins(0,0,0,0)
        wid_btn_aplicar.layout().setAlignment(Qt.AlignRight)

        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.aplicar_valores_filtro)
        btn_aplicar.setFixedWidth(80)
        btn_aplicar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn_aplicar.layout().addWidget(btn_aplicar)

        wid_derecha.layout().addWidget(wid_content_der,8)
        wid_derecha.layout().addWidget(wid_btn_aplicar,1)

        self.layout().addWidget(wid_izquierda, 5)
        self.layout().addWidget(wid_derecha, 5)


    def seleccionar_todas_las_graficas(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, QtWidgets.QTreeWidgetItem):
                if not hijo.checkState(0):
                    hijo.setCheckState(0,Qt.Checked)


    def aplicar_valores_filtro(self):
        hay_almenos_un_check = False
        order = self.spin_box.value()
        array_a = self.spiner_array_a.value()
        array_b = self.spiner_array_b.value()
        btype = self.combobox_btype.currentText()
        analog = None
        if self.combobox_analog.currentText() == "True":
            analog = True
        else:
            analog = False

        if self.graficas is not None:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, QtWidgets.QTreeWidgetItem):
                    if hijo.checkState(0):
                        hay_almenos_un_check = True
                        grafica : Grafica= self.get_grafica(hijo.text(0))
                        if grafica is not None:
                            grafica.set_filtro(Filtro(order, array_a, array_b, btype, analog))

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)



    def get_grafica(self,nombre_columna):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_nombre_columna_grafica() == nombre_columna:
                grafica_aux = grafica
                break

        return grafica_aux


class ventana_comparar(QtWidgets.QDialog):
    def __init__(self, parent=None, graficas=None):
        super(ventana_comparar, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Comparar gráficas")
        self.setFixedSize(420, 470)
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
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = QtWidgets.QTreeWidgetItem([nom_col])
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
            if isinstance(hijo, QtWidgets.QTreeWidgetItem):
                if not hijo.checkState(0):
                    hijo.setCheckState(0,Qt.Checked)


    def mostrar_comparacion_graficas(self):
        hay_almenos_un_check = False
        if self.graficas is not None:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(18, 4))
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, QtWidgets.QTreeWidgetItem):
                    if hijo.checkState(0):
                        hay_almenos_un_check = True
                        grafica : Grafica= self.get_grafica(hijo.text(0))
                        if grafica is not None:
                            archivo = grafica.get_archivo()
                            print(grafica.get_nombre_columna_tiempo(), grafica.get_nombre_columna_grafica())
                            axes.plot(archivo[grafica.get_nombre_columna_tiempo()],
                                      archivo[grafica.get_nombre_columna_grafica()],
                                      linewidth=0.3, label=f"{grafica.get_nombre_columna_grafica()}")
                            plt.legend()
                            fig.tight_layout()
                            fig.show()

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)
                self.close()


    def get_grafica(self,nombre_columna):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_nombre_columna_grafica() == nombre_columna:
                grafica_aux = grafica
                break

        return grafica_aux




