#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt5.QtWidgets import QWidget,QApplication


class mainwindow(QWidget):
    def __init__(self, parent=None):
        super(mainwindow, self).__init__(parent)

    def enterEvent(self, event):
        print ("Mouse Entered")
        return super(mainwindow, self).enterEvent(event)

    def leaveEvent(self, event):
        print ("Mouse Left")
        return super(mainwindow, self).enterEvent(event)

if __name__ == "__main__":
    import sys

    app  = QApplication(sys.argv)
    main = mainwindow()
    main.show()
    sys.exit(app.exec_())