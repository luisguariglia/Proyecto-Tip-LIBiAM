from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout
from PyQt5.QtCore import QVariant
from matplotlib import pyplot as plt

import config
from BD.Queries import Conexion
from Static.styles import estilos
from Modelo.Grafica import Grafica
from Modelo.Filtro import Filtro
from Modelo.Pico import Pico





class tree_widget_item_grafica(QtWidgets.QTreeWidgetItem):
    def __init__(self, text, id=None):
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
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Butter Filter - " + v )
        self.setFixedSize(770, 500)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10, 0, 10, 10)
        self.layout().setSpacing(15)

        # PARAMETROS
        self.parent = parent
        self.graficas = graficas

        wid_izquierda = QtWidgets.QWidget()
        wid_derecha = QtWidgets.QWidget()
        wid_filtro2 = QtWidgets.QWidget()

        # SOMBRAS
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        wid_izquierda.setGraphicsEffect(shadow)
        wid_derecha.setGraphicsEffect(shadow2)
        wid_filtro2.setGraphicsEffect(shadow2)
        # ESTILOS
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")
        wid_derecha.setStyleSheet("background-color:white; border-radius:4px;")
        wid_filtro2.setStyleSheet("background-color:white; border-radius:4px;")

        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())
        wid_derecha.setLayout(QtWidgets.QVBoxLayout())
        wid_filtro2.setLayout(QtWidgets.QVBoxLayout())

        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        label_2 = QtWidgets.QLabel("CONFIGURAR FILTRO 1")
        label_2.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        label_3 = QtWidgets.QLabel("CONFIGURAR FILTRO 2")
        label_3.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)
        wid_derecha.layout().addWidget(label_2, 1)
        wid_filtro2.layout().addWidget(label_3, 1)
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

        # YO

        # GROUP BOX VALORES FILTRO
        wid_content_der = QtWidgets.QWidget()
        wid_content_der.setLayout(QtWidgets.QVBoxLayout())
        wid_content_der.layout().setAlignment(Qt.AlignTop)
        wid_content_der.layout().setContentsMargins(10, 0, 0, 0)
        wid_content_der.layout().setSpacing(15)

        db = QtGui.QFontDatabase()
        font = db.font("Open Sans", "Regular", 10)



        # ORDER
        wid_label_order = QtWidgets.QWidget()
        wid_label_order.setLayout(QtWidgets.QHBoxLayout())

        wid_spiner_order = QtWidgets.QWidget()
        wid_spiner_order.setLayout(QtWidgets.QHBoxLayout())
        wid_spiner_order.layout().setContentsMargins(0, 0, 0, 0)
        wid_spiner_order.layout().setAlignment(Qt.AlignRight)

        label_order = QtWidgets.QLabel("Orden del filtro")
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

        label_array_like = QtWidgets.QLabel("Frecuencias críticas")
        label_array_like.setFont(font)

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
        wid_label_array_like.layout().addWidget(label_array_like)

        wid_array_like = QtWidgets.QWidget()
        wid_array_like.setLayout(QtWidgets.QHBoxLayout())
        wid_array_like.layout().setContentsMargins(0, 0, 0, 0)
        wid_array_like.layout().addWidget(wid_label_array_like, 5)
        wid_array_like.layout().addWidget(wid_spiner_array_like, 5)

        # BTYPE
        label_btype = QtWidgets.QLabel("Tipo de filtro")
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
        label_analog = QtWidgets.QLabel("Analógico")
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

        # "lowpass")
        # self.combobox_btype.addItem("highpass")
        # self.combobox_btype.addItem("bandpass")
        # self.combobox_btype.addItem("bandstop")
        #   infooo
        label_info = QtWidgets.QLabel("<br>"
                                      "<span style='font-weight: bold'>Frecuencias críticas: </span> La frecuencia o frecuencias críticas. Indicadas en Hz"
                                      "<br><span style='font-weight: bold'>Tipo de Filtro: </span> el tipo de filtro. El valor predeterminado es 'Butterworth'."
                                      "<br><span style='font-weight: bold'>Analogico: </span>Cuando es Verdadero, devuelve un filtro analógico; de lo contrario, se devuelve un filtro digital."
                                      "<br>"
                                      )
        # order- arraylike - btype - analog
        label_info.setFont(font)
        label_info.setWordWrap(True);
        # SE AGREGA CADA CONFIGURACIÓN EN ESTE ORDEN A LA VISTA
        wid_content_der.layout().addWidget(wid_order)
        wid_content_der.layout().addWidget(wid_array_like)
        wid_content_der.layout().addWidget(wid_btype)
        wid_content_der.layout().addWidget(wid_analog)
        wid_content_der.layout().addWidget(label_info)

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
        array_a = int(self.spiner_array_a.value()) * 0.001
        array_b = int(self.spiner_array_b.value()) * 0.001
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
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
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
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Valores en grafica - " + v)
        self.setFixedSize(770, 470*1.5)
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
        font = db.font("Open Sans", "Regular", 10)

        label_1 = QtWidgets.QLabel("SELECCIONAR GRÁFICAS")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")


        label_2 = QtWidgets.QLabel("Valores Picos")
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

        label_min_height = QtWidgets.QLabel("Altura Minima (^15)")
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

        label_threshold = QtWidgets.QLabel("Umbral")
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

        label_distance = QtWidgets.QLabel("Distancia")
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

        #   infooo
        label_info = QtWidgets.QLabel("<br>"
            "<span style='font-weight: bold'>Altura Minima:</span> altura minima requerida"
            "<br><span style='font-weight: bold'>Umbral:</span> Umbral minimo requerido, distancia vertical a sus muestras vecinas. "
            "<br><span style='font-weight: bold'>Distancia:</span>Distancia horizontal mínima requerida (>=1) en muestras entre picos vecinos. "
            "Los picos más pequeños se eliminan primero hasta que se cumpla la condición para todos los picos restantes."
            "<br>"
            )
        label_info.setFont(font)
        label_info.setWordWrap(True);
        wid_checkbox.layout().addWidget(self.checkbox_mostrar_picos)
        wid_checkbox.layout().addWidget(label_checkbox)
        wid_content_derecha.layout().addWidget(wid_checkbox)
        wid_content_derecha.layout().addWidget(label_info)

        # -------------------------------------------------------------------------------INTEGRAL-----------------------------------------------------------------

        label_3 = QtWidgets.QLabel("Integral")
        label_3.setStyleSheet("font:14px bold; margin:5px;")
        wid_content_derecha.layout().addWidget(label_3)

        wid_inicio = QtWidgets.QWidget()
        wid_inicio.setLayout(QtWidgets.QHBoxLayout())
        wid_inicio.layout().setContentsMargins(0, 0, 0, 0)
        wid_inicio.layout().setSpacing(0)

        label_inicio = QtWidgets.QLabel("Valor inicial")
        label_inicio.setFont(font)

        self.spinbox_inicio = QtWidgets.QDoubleSpinBox()
        self.spinbox_inicio.setValue(0.0)
        self.spinbox_inicio.setMaximumWidth(90)
        self.spinbox_inicio.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_inicio.layout().addWidget(label_inicio, 5)
        wid_inicio.layout().addWidget(self.spinbox_inicio, 2)
        wid_content_derecha.layout().addWidget(wid_inicio)

        # segundo parametro
        wid_fin = QtWidgets.QWidget()
        wid_fin.setLayout(QtWidgets.QHBoxLayout())
        wid_fin.layout().setContentsMargins(0, 0, 0, 0)
        wid_fin.layout().setSpacing(0)

        label_fin = QtWidgets.QLabel("Valor final")
        label_fin.setFont(font)

        self.spinbox_fin = QtWidgets.QDoubleSpinBox()
        self.spinbox_fin.setValue(0.0)
        self.spinbox_fin.setMaximumWidth(90)
        self.spinbox_fin.setStyleSheet(estilos.estilos_double_spinbox_filtros())

        wid_fin.layout().addWidget(label_fin, 5)
        wid_fin.layout().addWidget(self.spinbox_fin, 2)
        wid_content_derecha.layout().addWidget(wid_fin)

        # checkbox
        wid_checkbox_integral = QtWidgets.QWidget()
        wid_checkbox_integral.setLayout(QtWidgets.QHBoxLayout())
        wid_checkbox_integral.layout().setContentsMargins(0, 5, 0, 0)
        wid_checkbox_integral.layout().setAlignment(Qt.AlignLeft)
        wid_checkbox_integral.layout().setSpacing(0)

        label_checkbox_integral = QtWidgets.QLabel("Mostrar Integral")
        label_checkbox_integral.setFont(font)
        label_checkbox_integral.setStyleSheet("margin:0px;")

        self.checkbox_mostrar_integral = QtWidgets.QCheckBox()
        self.checkbox_mostrar_integral.setStyleSheet("margin-left:14px;")

        wid_checkbox_integral.layout().addWidget(self.checkbox_mostrar_integral)
        wid_checkbox_integral.layout().addWidget(label_checkbox_integral)
        wid_content_derecha.layout().addWidget(wid_checkbox_integral)
        # -------------------------------------------------------------------------------INTEGRAL-----------------------------------------------------------------
        wid_btn_aplicar = QtWidgets.QWidget()

        wid_btn_aplicar.setLayout(QtWidgets.QHBoxLayout())
        wid_btn_aplicar.layout().setContentsMargins(0, 0, 0, 0)
        wid_btn_aplicar.layout().setSpacing(0)
        wid_btn_aplicar.layout().setAlignment(Qt.AlignRight)


        btn_aplicar = QtWidgets.QPushButton("APLICAR")
        btn_aplicar.clicked.connect(self.aplicar_valores)
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

    def aplicar_valores(self):
        hay_almenos_un_check = False

        min_height = self.spinbox_min_height.value()
        treshold = self.spinbox_threshold.value()
        distance = self.spinbox_distance.value()
        mostrarPicos = self.checkbox_mostrar_picos.isChecked()


        inicio = self.spinbox_inicio.value()
        fin = self.spinbox_fin.value()
        mostrarIntegral = self.checkbox_mostrar_integral.isChecked()

        if self.graficas is not None:
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
                            grafica.set_integral(([inicio,fin,mostrarIntegral]))

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
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
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

        #boton de reset
        btn_resetear = QtWidgets.QPushButton("Resetear")
        btn_resetear.clicked.connect(self.resetear_valores)
        btn_resetear.setFixedWidth(80)
        btn_resetear.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        #   infooo
        label_info = QtWidgets.QLabel("<br>"
                                      "Se cortan las graficas desde un determinado valor de tiempo en segundos hasta otro valor"
                                      "<br>"
                                      "Para dejar la grafica original se deben de poner los valores de desde y hasta en 0"
                                      "<br>")
        label_info.setFont(font)
        label_info.setWordWrap(True);
        # SE AGREGA CADA CONFIGURACIÓN EN ESTE ORDEN A LA VISTA
        wid_content_der.layout().addWidget(wid_desde)
        wid_content_der.layout().addWidget(wid_hasta)
        wid_content_der.layout().addWidget(btn_resetear)
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
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
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
        label_info = QtWidgets.QLabel("<br>"
                                      "Se toman los valores de voltaje desde inicio hasta fin y se hace un promedio para poner la grafica lo mas cerca del 0 posible"
                                      "<br>"
                                      "Para dejar la grafica original se deben de poner los valores de inicio y fin en 0"
                                      "<br>")
        label_info.setFont(font)
        label_info.setWordWrap(True);


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

class ventana_conf_vistas(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ventana_conf_vistas, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
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

    def guardar_conf(self):
        dato = self.spinbox_limite_vistas.value()
        dato_int = int(dato)

        config.LIMITE_GRAFICAS_POR_VISTA = dato_int
        Conexion.set_limite_graficas(dato_int)
        self.close()

class ventana_exportarVP(QtWidgets.QDialog):
    def __init__(self, parent=None, graficas=None):
        super(ventana_exportarVP, self).__init__()
        self.setWindowIcon(QtGui.QIcon(":/Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Exportar valores pico")
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

        label_1 = QtWidgets.QLabel("EXPORTAR VALORES PICO")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)

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
        if self.graficas is not None:
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
        self.spinbox_row_column.setMinimum(0)
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
    def __init__(self, parent=None, archivo=None):
        super(ventana_conf_linea_archivo, self).__init__()
        self.setWindowIcon(QtGui.QIcon("Static/img/LIBiAM.jpg"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Configuraciones de columnas de información")
        self.setFixedSize(770, 500)
        self.setStyleSheet("background-color:#FAFAFA;")
        self.setLayout(QtWidgets.QHBoxLayout())
        self.setContentsMargins(10, 0, 10, 10)
        self.layout().setSpacing(15)



        # PARAMETROS
        self.parent = parent
        self.archivo = archivo

        wid_izquierda = QtWidgets.QWidget()
        wid_derecha = QtWidgets.QWidget()
        wid_filtro2 = QtWidgets.QWidget()

        # SOMBRAS
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)
        shadow2 = QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=1, yOffset=1)

        wid_izquierda.setGraphicsEffect(shadow)
        wid_derecha.setGraphicsEffect(shadow2)
        #wid_filtro2.setGraphicsEffect(shadow2)
        # ESTILOS
        wid_izquierda.setStyleSheet("background-color:white; border-radius:4px;")
        wid_derecha.setStyleSheet("background-color:white; border-radius:4px;")
        wid_filtro2.setStyleSheet("background-color:white; border-radius:4px;")

        wid_izquierda.setLayout(QtWidgets.QVBoxLayout())
        wid_derecha.setLayout(QtWidgets.QVBoxLayout())
        wid_filtro2.setLayout(QtWidgets.QVBoxLayout())

        wid_izquierda.layout().setSpacing(20)
        wid_izquierda.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)

        label_1 = QtWidgets.QLabel("COLUMNAS DEL ARCHIVO")
        label_1.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        label_2 = QtWidgets.QLabel("FILTRAR COLUMNAS")
        label_2.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;margin-bottom:16px;")

        label_3 = QtWidgets.QLabel("CONFIGURAR FILTRO 2")
        label_3.setStyleSheet("font:14px bold; margin-left:5px;margin-top:10px;")

        wid_izquierda.layout().addWidget(label_1, 1)
        wid_derecha.layout().addWidget(label_2, 1)
        wid_filtro2.layout().addWidget(label_3, 1)
        # GRAFICAS
        self.tree_graficas = QtWidgets.QTreeWidget()
        self.tree_graficas.setFixedWidth(300)
        self.tree_graficas.setHeaderHidden(True)

        columnas = self.archivo.get_archivo().columns
        for x in range(1, len(columnas), 2):

            item = tree_widget_item_grafica(columnas[x])
            self.tree_graficas.addTopLevelItem(item)

        btn_aplicar_a_todas = QtWidgets.QPushButton("SELECCIONAR TODAS")
        btn_aplicar_a_todas.clicked.connect(self.seleccionar_todas_las_graficas)
        btn_aplicar_a_todas.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        btn_seleccionar = QtWidgets.QPushButton("SELECCIONAR")
        btn_seleccionar.clicked.connect(self.seleccionar)
        btn_seleccionar.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        # CONTENEDOR BOTON,POR SI PINTA MOVERLO DE LUGAR
        wid_btn = QtWidgets.QWidget()
        wid_btn.setStyleSheet("QWidget{margin-left:5px;")

        wid_btn.setFixedWidth(350)
        wid_btn.setLayout(QtWidgets.QHBoxLayout())
        wid_btn.layout().setAlignment(Qt.AlignLeft)
        wid_btn.layout().addWidget(btn_aplicar_a_todas)
        wid_btn.layout().addWidget(btn_seleccionar)

        wid_izquierda.layout().addWidget(self.tree_graficas, 8)
        wid_izquierda.layout().addWidget(wid_btn, 1)

        # YO

        # GROUP BOX VALORES FILTRO
        wid_content_der = QtWidgets.QWidget()
        wid_content_der.setLayout(QtWidgets.QVBoxLayout())
        wid_content_der.layout().setAlignment(Qt.AlignTop)
        wid_content_der.layout().setContentsMargins(10, 0, 0, 0)
        wid_content_der.layout().setSpacing(20)

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

        wid_btn = QtWidgets.QWidget()
        wid_btn.setLayout(QtWidgets.QHBoxLayout())
        wid_btn.layout().setContentsMargins(0, 10, 0, 0)
        wid_btn.layout().setAlignment(Qt.AlignRight)

        btn = QtWidgets.QPushButton("FILTRAR")
        btn.clicked.connect(self.filtrar_por_caracteres)
        btn.setStyleSheet(estilos.estilos_btn_aplicar_a_todas())

        wid_btn.layout().addWidget(btn)
        wid_filtrar_content.layout().addWidget(wid_btn)

        # BTYPE
        label_btype = QtWidgets.QLabel("Tipo de filtro")
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
        label_analog = QtWidgets.QLabel("Analógico")
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

        # "lowpass")
        # self.combobox_btype.addItem("highpass")
        # self.combobox_btype.addItem("bandpass")
        # self.combobox_btype.addItem("bandstop")
        #   infooo
        label_info = QtWidgets.QLabel("")
        # order- arraylike - btype - analog
        label_info.setFont(font)
        label_info.setWordWrap(True);
        # SE AGREGA CADA CONFIGURACIÓN EN ESTE ORDEN A LA VISTA
        wid_content_der.layout().addWidget(wid_order)
        wid_content_der.layout().addWidget(wid_filtrar_content)
        wid_content_der.layout().addWidget(wid_btype)
        wid_content_der.layout().addWidget(wid_analog)
        wid_content_der.layout().addWidget(label_info)

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

    def seleccionar(self):
        cant_hijos = self.tree_graficas.topLevelItemCount()
        for i in range(cant_hijos):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                if not hijo.checkState(0):
                    hijo.setCheckState(0, Qt.Unchecked)

    def filtrar_no_seleccionados(self):

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

        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                hijo.setData(0,Qt.CheckStateRole, None)

    def filtrar_seleccionados(self):

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

        for i in range(self.tree_graficas.topLevelItemCount()):
            hijo = self.tree_graficas.topLevelItem(i)
            if isinstance(hijo, tree_widget_item_grafica):
                hijo.setData(0,Qt.CheckStateRole, None)

    def filtrar_por_caracteres(self):
        if len(self.checkbox.text()) == 0:
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
