from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox
from matplotlib import pyplot as plt

from Static.styles import estilos
from Modelo.Grafica import Grafica
from Modelo.Filtro import Filtro
from Modelo.Pico import Pico


class tree_widget_item_grafica(QtWidgets.QTreeWidgetItem):
    def __init__(self, text, id):
        super(tree_widget_item_grafica, self).__init__()
        self.setText(0,text)
        self.id = id

    def get_id(self):
        return self.id

    def set_id(self,id):
        self.id = id

class ventana_filtro(QtWidgets.QDialog):
    def __init__(self,parent=None,graficas=None,v=""):

        super(ventana_filtro, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Butter Filter - " + v )
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

        label_2 = QtWidgets.QLabel("CONFIGURAR FILTRO")
        label_2.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)
        wid_derecha.layout().addWidget(label_2, 1)

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id())
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
        font = db.font("Open Sans", "Regular", 8)

        # ORDER
        wid_label_order = QtWidgets.QWidget()
        wid_label_order.setLayout(QtWidgets.QHBoxLayout())

        wid_spiner_order = QtWidgets.QWidget()
        wid_spiner_order.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_order.layout().setContentsMargins(0, 0, 0, 0)
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
        wid_order.layout().setContentsMargins(0, 0, 0, 0)
        wid_order.layout().addWidget(wid_label_order, 5)
        wid_order.layout().addWidget(wid_spiner_order, 5)

        # ARRAY LIKE
        wid_label_array_like = QtWidgets.QWidget()
        wid_label_array_like.setLayout(QtWidgets.QHBoxLayout())

        wid_spiner_array_like = QtWidgets.QWidget()
        wid_spiner_array_like.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_array_like.layout().setContentsMargins(0, 0, 0, 0)
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
        wid_array_like.layout().setContentsMargins(0, 0, 0, 0)
        wid_array_like.layout().addWidget(wid_label_array_like, 5)
        wid_array_like.layout().addWidget(wid_spiner_array_like, 5)

        # BTYPE
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
        wid_combobox_btype.layout().setContentsMargins(0, 0, 0, 0)
        wid_combobox_btype.layout().setAlignment(Qt.AlignRight)
        wid_combobox_btype.layout().addWidget(self.combobox_btype)

        wid_btype = QtWidgets.QWidget()
        wid_btype.setLayout(QtWidgets.QHBoxLayout())
        wid_btype.layout().setContentsMargins(0, 0, 0, 0)

        wid_btype.layout().addWidget(wid_label_btype, 5)
        wid_btype.layout().addWidget(wid_combobox_btype, 5)

        # ANALOG
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
        wid_combobox_analog.layout().setContentsMargins(0, 0, 0, 0)
        wid_combobox_analog.layout().setAlignment(Qt.AlignRight)
        wid_combobox_analog.layout().addWidget(self.combobox_analog)

        wid_analog = QtWidgets.QWidget()
        wid_analog.setLayout(QtWidgets.QHBoxLayout())
        wid_analog.layout().setContentsMargins(0, 0, 0, 0)

        wid_analog.layout().addWidget(wid_label_analog, 5)
        wid_analog.layout().addWidget(wid_combobox_analog, 5)

        # SE AGREGA CADA CONFIGURACIÓN EN ESTE ORDEN A LA VISTA
        wid_content_der.layout().addWidget(wid_order)
        wid_content_der.layout().addWidget(wid_array_like)
        wid_content_der.layout().addWidget(wid_btype)
        wid_content_der.layout().addWidget(wid_analog)

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

        wid_derecha.layout().addWidget(wid_content_der, 8)
        wid_derecha.layout().addWidget(wid_btn_aplicar, 1)

        self.layout().addWidget(wid_izquierda, 5)
        self.layout().addWidget(wid_derecha, 5)

    def seleccionar_todas_las_graficas(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if not hijo.checkState(0):
                    hijo.setCheckState(0, Qt.Checked)

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
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        hay_almenos_un_check = True

                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            grafica.set_filtro(Filtro(order, array_a, array_b, btype, analog))

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)
                self.close()

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
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
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id)
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

            if len(graficas) >= 2:
                self.parent.comparar_graficas(graficas)
                self.close()

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux


class ventana_valores_en_graficas(QtWidgets.QDialog):
    def __init__(self, parent=None,graficas=None,v=""):
        super(ventana_valores_en_graficas, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Valores en grafica - " + v)
        self.setFixedSize(770, 470)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10,0,10,10)
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

        wid_derecha.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        wid_derecha.setGraphicsEffect(shadow2)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 8)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")


        label_2 = QtWidgets.QLabel("CONFIGURACIONES")
        label_2.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_derecha.layout().addWidget(label_2,1)
        wid_izquierda.layout().addWidget(label_1, 1)

        wid_content_derecha = QtWidgets.QWidget()
        #wid_content_derecha.setFixedWidth(225)
        wid_content_derecha.setStyleSheet("margin-left:10px;")
        wid_content_derecha.setLayout(QtWidgets.QVBoxLayout())
        wid_content_derecha.layout().setAlignment(Qt.AlignTop)
        wid_content_derecha.layout().setSpacing(10)

        wid_derecha.layout().addWidget(wid_content_derecha, 8)

        wid_min_height = QtWidgets.QWidget()
        wid_min_height.setLayout(QtWidgets.QHBoxLayout())
        wid_min_height.layout().setContentsMargins(0, 0, 0, 0)
        wid_min_height.layout().setSpacing(0)

        label_min_height = QtWidgets.QLabel("MIN HEIGHT (^15)")
        label_min_height.setFont(font)

        self.spinbox_min_height = QtWidgets.QDoubleSpinBox()
        self.spinbox_min_height.setValue(2.0)
        self.spinbox_min_height.setMaximumWidth(90)
        self.spinbox_min_height.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_min_height.layout().addWidget(label_min_height, 5)
        wid_min_height.layout().addWidget(self.spinbox_min_height, 2)
        wid_content_derecha.layout().addWidget(wid_min_height)

        wid_threshold = QtWidgets.QWidget()
        wid_threshold.setLayout(QtWidgets.QHBoxLayout())
        wid_threshold.layout().setContentsMargins(0, 0, 0, 0)
        wid_threshold.layout().setSpacing(0)

        label_threshold = QtWidgets.QLabel("THRESHOLD")
        label_threshold.setFont(font)

        self.spinbox_threshold = QtWidgets.QDoubleSpinBox()
        self.spinbox_threshold.setValue(1.0)
        self.spinbox_threshold.setMaximumWidth(90)
        self.spinbox_threshold.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_threshold.layout().addWidget(label_threshold, 5)
        wid_threshold.layout().addWidget(self.spinbox_threshold, 2)
        wid_content_derecha.layout().addWidget(wid_threshold)

        wid_distance = QtWidgets.QWidget()
        wid_distance.setLayout(QtWidgets.QHBoxLayout())
        wid_distance.layout().setContentsMargins(0, 0, 0, 0)
        wid_distance.layout().setSpacing(0)

        label_distance = QtWidgets.QLabel("DISTANCE")
        label_distance.setFont(font)

        self.spinbox_distance = QtWidgets.QDoubleSpinBox()
        self.spinbox_distance.setMaximum(1000)
        self.spinbox_distance.setMinimum(0)
        self.spinbox_distance.setValue(400)
        self.spinbox_distance.setMaximumWidth(90)
        self.spinbox_distance.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_distance.layout().addWidget(label_distance, 5)
        wid_distance.layout().addWidget(self.spinbox_distance, 2)
        wid_content_derecha.layout().addWidget(wid_distance)

        wid_checkbox = QtWidgets.QWidget()
        wid_checkbox.setLayout(QtWidgets.QHBoxLayout())
        wid_checkbox.layout().setContentsMargins(0, 5, 0, 0)
        wid_checkbox.layout().setAlignment(Qt.AlignLeft)
        wid_checkbox.layout().setSpacing(0)

        label_checkbox = QtWidgets.QLabel("Mostrar Picos")
        label_checkbox.setFont(font)
        label_checkbox.setStyleSheet("margin:0px;")

        self.checkbox_mostrar_picos = QtWidgets.QCheckBox()
        self.checkbox_mostrar_picos.setStyleSheet("margin-left:14px;")

        wid_checkbox.layout().addWidget(self.checkbox_mostrar_picos)
        wid_checkbox.layout().addWidget(label_checkbox)
        #wid_content_derecha.layout().addWidget(wid_checkbox)

        wid_btn_aplicar = QtWidgets.QWidget()

        wid_btn_aplicar.setLayout(QtWidgets.QHBoxLayout())
        wid_btn_aplicar.layout().setContentsMargins(0, 0, 0, 0)
        wid_btn_aplicar.layout().setSpacing(0)
        wid_btn_aplicar.layout().setAlignment(Qt.AlignRight)


        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.aplicar_valores_picos)
        btn_aplicar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn_aplicar.layout().addWidget(btn_aplicar)
        wid_derecha.layout().addWidget(wid_btn_aplicar ,1)

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col,grafica.get_id())
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

    def aplicar_valores_picos(self):
        hay_almenos_un_check = False

        min_height = self.spinbox_min_height.value()
        treshold = self.spinbox_threshold.value()
        distance = self.spinbox_distance.value()

        if self.graficas is not None:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        hay_almenos_un_check = True

                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            grafica.set_valores_picos(Pico(min_height, treshold, distance))

            if hay_almenos_un_check:
                self.parent.listar_graficas(valores_pico=True)
                self.close()

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
    def __init__(self, parent=None, graficas=None):
        super(ventana_cortar, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Cortar Graficas - Vista 1")
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

        label_2 = QtWidgets.QLabel("CONFIGURAR RECORTE")
        label_2.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)
        wid_derecha.layout().addWidget(label_2, 1)

        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id())
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

        label_desde = QtWidgets.QLabel("DESDE")
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
        label_hasta = QtWidgets.QLabel("HASTA")
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

        #boton de reset
        btn_resetear = QtWidgets.QPushButton("RESETEAR")
        btn_resetear.clicked.connect(self.resetear_valores)
        btn_resetear.setFixedWidth(80)
        btn_resetear.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # SE AGREGA CADA CONFIGURACIÓN EN ESTE ORDEN A LA VISTA
        wid_content_der.layout().addWidget(wid_desde)
        wid_content_der.layout().addWidget(wid_hasta)
        wid_content_der.layout().addWidget(btn_resetear)

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

        if self.graficas is not None:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        hay_almenos_un_check = True

                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            grafica.set_recorte([desde,hasta])

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux

class ventana_rectificar(QtWidgets.QDialog):
    def __init__(self, parent=None, graficas=None):
        super(ventana_rectificar, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Rectificar Graficas - Vista 1")
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
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        if self.graficas is not None:
            for grafica in self.graficas:
                nom_col = grafica.get_nombre_columna_grafica()
                item = tree_widget_item_grafica(nom_col, grafica.get_id())
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
        label_info = QtWidgets.QLabel("Se toman los valores de voltaje desde inicio\nhasta fin y se hace un promedio para poner\nla grafica lo mas cerca del 0 posible\n"
                                      "-----\n"
                                      "Para dejar la grafica original se deben de poner\nlos valores de inicio y fin en 0")
        label_info.setFont(font)

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

        if self.graficas is not None:
            cant_hijos = self.tree_graficas.topLevelItemCount()
            for i in range(cant_hijos):
                hijo = self.tree_graficas.topLevelItem(i)
                if isinstance(hijo, tree_widget_item_grafica):
                    if hijo.checkState(0):
                        hay_almenos_un_check = True

                        grafica: Grafica = self.get_grafica(hijo.get_id())
                        if grafica is not None:
                            grafica.set_offset([desde,hasta,abs])

            if hay_almenos_un_check:
                self.parent.listar_graficas(True)

    def get_grafica(self, id_grafica):
        grafica_aux = None
        for grafica in self.graficas:
            if grafica.get_id() == id_grafica:
                grafica_aux = grafica
                break

        return grafica_aux