from PyQt5 import QtCore, QtGui,QtWidgets

class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.view = QtWidgets.QTreeView(self)
        self.view.setMouseTracking(True)
        self.view.entered.connect(self.handleItemEntered)
        model = QtGui.QStandardItemModel(self)
        for text in 'One Two Three Four Five'.split():
            model.appendRow(QtGui.QStandardItem(text))
        self.view.setModel(model)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)

    def handleItemEntered(self, index):
        if index.isValid():
            QtWidgets.QToolTip.showText(
                QtGui.QCursor.pos(),
                index.data(),
                self.view.viewport(),
                self.view.visualRect(index)
                )

if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(500, 300, 200, 200)
    window.show()
    sys.exit(app.exec_())