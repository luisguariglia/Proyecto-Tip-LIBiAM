import sys
from PyQt5.QtCore import Qt
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
        self.tab_widget.currentChanged.connect(self.changed)
        self.tab_widget.addTab(self.widget_form1,"Form 1")
        self.tab_widget.addTab(self.widget_form2, "Form 2")

        self.layout().addWidget(self.tab_widget)

    def changed(self,index):
        if self.flag:
            self.flag = False
            return

        if not self.form_completed:
            QtWidgets.QMessageBox.about(self, "Warning", "You must complete the form")
            return

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    mw = MyWidget()
    mw.show()
    sys.exit(app.exec_())