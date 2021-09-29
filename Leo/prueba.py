from sys import exit as sysExit

from PyQt5.QtWidgets import QApplication, QMessageBox

def Main():
    msgbox = QMessageBox()
    msgbox.setWindowTitle("Information")
    msgbox.setText('Test')
    msgbox.addButton(QMessageBox.Ok)
    msgbox.addButton('Ver ayuda', QMessageBox.YesRole)

    bttn = msgbox.exec_()

    if bttn == QMessageBox.Ok:
        print("Ok")
        sysExit()
    else:
        print("View Graphs")
        sysExit()

if __name__ == "__main__":
    MainThred = QApplication([])

    MainApp = Main()

    sysExit(MainThred.exec_())