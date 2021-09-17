import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtWidgets

class MyWidget(QtWidgets.QWidget):

    def __init__(self):
        super(MyWidget, self).__init__()
        self.setGeometry(0, 0, 800, 500)
        self.setLayout(QtWidgets.QVBoxLayout())

        #flag to not show the alert when starting the program
        self.flag = True

        #changes to True when the form is completed
        self.form_completed = False

        # WIDGET TAB 1
        self.widget_form1 = QtWidgets.QWidget()
        self.widget_form1.setLayout(QtWidgets.QVBoxLayout())
        self.widget_form1.layout().setAlignment(Qt.AlignHCenter)
        label_form1 = QtWidgets.QLabel("FORM 1")
        self.widget_form1.layout().addWidget(label_form1)

        #WIDGET TAB 2
        self.widget_form2 = QtWidgets.QWidget()
        self.widget_form2.setLayout(QtWidgets.QVBoxLayout())
        self.widget_form2.layout().setAlignment(Qt.AlignHCenter)
        label_form2 = QtWidgets.QLabel("FORM 2")
        self.widget_form2.layout().addWidget(label_form2)

        #QTABWIDGET
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.widget_form1,"Form 1")
        self.tab_widget.addTab(self.widget_form2, "Form 2")
        self.tab_widget.installEventFilter(self)
        self.tab_widget.tabBar().installEventFilter(self)

        self.layout().addWidget(self.tab_widget)

    def eventFilter(self, source, event):
        if source == self.tab_widget.tabBar() and \
            event.type() == event.MouseButtonPress and \
            event.button() == Qt.LeftButton:
                tab = self.tab_widget.tabBar().tabAt(event.pos())
                if tab >= 0 and tab != self.tab_widget.currentIndex():
                    return self.isInvalid()
        elif source == self.tab_widget and \
            event.type() == event.KeyPress and \
            event.key() in (Qt.Key_Tab, Qt.Key_Backtab) and \
            event.modifiers() & Qt.ControlModifier:
                return self.isInvalid()
        return super().eventFilter(source, event)

    def isInvalid(self):
        if not self.form_completed:

            QTimer.singleShot(0, lambda: QtWidgets.QMessageBox.about(
                self, "Warning", "You must complete the form"))
            return True
        return False

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    mw = MyWidget()
    mw.show()
    sys.exit(app.exec_())