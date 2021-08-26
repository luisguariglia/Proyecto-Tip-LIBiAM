import os
import sys
import shutil
import threading
from PyQt5 import QtCore, QtGui, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    startMoveFilesSignal = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super(MainWindow, self).__init__()
        srcdir = "C:/Users/Leo/Videos/a"
        dstdir = "C:/Users/Leo/Desktop/abc"
        self.le_src = QtWidgets.QLineEdit(srcdir)
        self.le_dst = QtWidgets.QLineEdit(dstdir)
        self.button = QtWidgets.QPushButton("Copy")
        self.button.clicked.connect(self.archiveEntry)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QFormLayout(central_widget)
        lay.addRow("From: ", self.le_src)
        lay.addRow("To: ", self.le_dst)
        lay.addRow(self.button)

        self.progressbar = QtWidgets.QProgressDialog(self)
        self.progressbar.hide()

        thread = QtCore.QThread(self)
        thread.start()
        self.helper = MoveFileHelper()
        self.startMoveFilesSignal.connect(self.helper.moveFilesWithProgress)
        self.helper.progressChanged.connect(self.progressbar.setValue)
        self.helper.finished.connect(self.on_finished)
        self.helper.started.connect(self.progressbar.show)
        self.helper.errorOccurred.connect(self.on_errorOcurred)
        self.helper.moveToThread(thread)

    @QtCore.pyqtSlot()
    def archiveEntry(self):
        self.startMoveFilesSignal.emit(self.le_src.text(), self.le_dst.text())
        self.progressbar.hide()

    @QtCore.pyqtSlot()
    def on_finished(self):
        self.button.setText('Finished')

    @QtCore.pyqtSlot(str)
    def on_errorOcurred(self, msg):
        QtWidgets.QMessageBox.critical(self, "Error Ocurred", msg)

class MoveFileHelper(QtCore.QObject):
    progressChanged = QtCore.pyqtSignal(int)
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    errorOccurred = QtCore.pyqtSignal(str)

    def calculateAndUpdate(self, done, total):
        progress = int(round((done / float(total)) * 100))
        self.progressChanged.emit(progress)

    @staticmethod
    def countFiles(directory):
        count = 0
        if os.path.isdir(directory):
            for path, dirs, filenames in os.walk(directory):
                count += len(filenames)
        return count

    @staticmethod
    def makedirs(dest):
        if not os.path.exists(dest):
            os.makedirs(dest)

    @QtCore.pyqtSlot(str, str)
    def moveFilesWithProgress(self, src, dest):
        numFiles = MoveFileHelper.countFiles(src)
        if os.path.exists(dest):
            self.errorOccurred.emit("Dest exist")
            return

        self.started.emit()
        MoveFileHelper.makedirs(dest)
        numCopied = 0
        for path, dirs, filenames in os.walk(src):
            for directory in dirs:
                destDir = path.replace(src, dest)
                MoveFileHelper.makedirs(os.path.join(destDir, directory))

            for sfile in filenames:
                srcFile = os.path.join(path, sfile)
                destFile = os.path.join(path.replace(src, dest), sfile)
                shutil.copy(srcFile, destFile)
                numCopied += 1
                self.calculateAndUpdate(numCopied, numFiles)
        self.finished.emit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWindow()
    ex.resize(640, ex.sizeHint().height())
    ex.show()
    sys.exit(app.exec_())