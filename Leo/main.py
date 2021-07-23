import sys
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QTreeWidget,QTreeWidgetItem,QVBoxLayout,QDialog,QWidget
from PyQt5.QtCore import pyqtSignal,QPoint


class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__()

        self.tw = QtWidgets.QTreeWidget()
        self.tw.setHeaderLabels(["Name", "Cost ($)"])
        cg = QtWidgets.QTreeWidgetItem(["carrots", "0.99"])
        c1 = QtWidgets.QTreeWidgetItem(["carrot", "0.33"])
        self.tw.addTopLevelItem(cg)
        self.tw.addTopLevelItem(c1)

        self.tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tw.customContextMenuRequested.connect(self.handle_rightClicked)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tw)

    def handle_rightClicked(self, pos):
        item = self.tw.itemAt(pos)
        if item is None:
            return
        menu = QtWidgets.QMenu()
        print_action = QtWidgets.QAction("Print")
        print_action.triggered.connect(lambda checked, item=item: self.print_item(item))
        menu.addAction(print_action)
        menu.exec_(self.tw.viewport().mapToGlobal(pos))

    def print_item(self, item):
        if item is None:
            return
        texts = []
        if item.parent() is not None:
            print("Grafica")
        elif item.parent() is None:
            print("Vista")

        for i in range(item.columnCount()):
            text = item.text(i)
            texts.append(text)

        print("B: {}".format(",".join(texts)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Dialog()
    ex.show()
    sys.exit(app.exec_())