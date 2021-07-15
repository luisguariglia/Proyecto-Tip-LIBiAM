from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QWidget, QApplication,QLabel,QVBoxLayout,QPushButton,QTreeView,QFormLayout,QGroupBox,QScrollArea)
from PyQt5.Qt import QStandardItemModel,QStandardItem
from PyQt5.QtGui import QFont,QColor
import sys

class StandarItem(QStandardItem):
    def __init__(self,txt='',font_size=12,set_bold=False,color=QColor(0,0,0)):
        super(StandarItem, self).__init__()
        fnt = QFont('Open Sans',font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)


class Example(QtWidgets.QMainWindow):

    def __init__(self, parent=None, *args):
        super(Example,self).__init__(parent=parent)
        self.initUI()

    def initUI(self):

        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.widget = QWidget(self)
        self.resize(700,500)
        self.widget.setStyleSheet("background-color: yellow;")
        self.setCentralWidget(self.widget)

        width = self.screen().geometry().width()
        height = self.screen().geometry().height()
        alto_tool_bar = 70
        largo_widget_izq = round((width*20)/100)
        largo_widget_der = round((width*80)/100)
        posicion_widget_der = largo_widget_izq

        self.widget_tool_bar = QWidget(self.widget)
        self.widget_tool_bar.setGeometry(0, 0, width,alto_tool_bar)
        self.widget_tool_bar.setStyleSheet("background-color: green;")

        self.widget_izq = QWidget(self.widget)
        self.widget_izq.setGeometry(0,alto_tool_bar,largo_widget_izq,height-alto_tool_bar)
        self.widget_izq.setStyleSheet("background-color: white;")

        self.widget_der = QWidget(self.widget)
        self.widget_der.setGeometry(posicion_widget_der,alto_tool_bar,largo_widget_der,height-alto_tool_bar)
        self.widget_der.setStyleSheet("background-color: red;")

        form_layout = QFormLayout()
        group_box = QGroupBox("This is Group Box")

        label_list = []
        button_list = []

        for i in range(20):
            label_list.append(QLabel("Label"))
            button_list.append(QPushButton("Click Me"))
            form_layout.addRow(label_list[i],button_list[i])

        group_box.setLayout(form_layout)
        scroll_area = QScrollArea(self.widget_der)
        scroll_area.setWidget(group_box)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(300)
        scroll_area.setFixedWidth(largo_widget_der)


        self.treeView = QTreeView(self.widget_izq)
        self.treeView.setHeaderHidden(True)
        treeModel = QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        america = StandarItem('EMG 1',12,set_bold=False)
        california = StandarItem('EMG',10)
        texas = StandarItem('Aceleración',10)
        america.appendRow(california)
        america.appendRow(texas)

        rootNode.appendRow(america)
        self.treeView.setModel(treeModel)

def main():
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()