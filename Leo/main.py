from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem,QPushButton,QHBoxLayout,QVBoxLayout,QWidget
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup, QPoint, QSize
from PyQt5.Qt import Qt

import sys


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.title = "PyQt5 QGraphicView"
        self.setWindowState(Qt.WindowMaximized)

        self.InitWindow()

    def InitWindow(self):
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setLayout(QHBoxLayout())

        width = self.screen().geometry().width()
        height = self.screen().geometry().height()

        wid_izq = QWidget(self)
        wid_izq.setStyleSheet("background-color:yellow;")
        wid_izq.setGeometry(0,0,30,height)
        wid_izq.move(-30,0)
        wid_izq.setLayout(QHBoxLayout())
        wid_izq.layout().setContentsMargins(0,0,0,0)
        wid_izq.layout().setSpacing(0)
        wid_izq.layout().setAlignment(Qt.AlignTop)

        wid_medio = QWidget(self)
        wid_medio.setStyleSheet("background-color:blue")
        wid_medio.setGeometry(0,0,int((width * 0.3)),height)
        # RANCIADA
        self.scene = QGraphicsScene()

        graphicView = QGraphicsView(self.scene, self)
        graphicView.setContentsMargins(0,0,0,0)
        graphicView.setMaximumHeight(400)
        graphicView.setAlignment(Qt.AlignTop)
        self.shapes()

        wid_izq.layout().addWidget(graphicView)

        # RANCIADA


        wid_der = QWidget(self)
        wid_der.setStyleSheet("background-color:green;")
        wid_der.setGeometry(int((width - (width * 0.7))),0,int((width * 0.8)),height)
        #self.createGraphicView()


        #ANIMACIONES

        self.anim = QPropertyAnimation(wid_der, b"pos")
        self.anim.setEndValue(QPoint(30, 0))
        self.anim.setDuration(500)

        self.anim_2 = QPropertyAnimation(wid_der, b"size")
        self.anim_2.setEndValue(QSize(int((width - 30)), height))
        self.anim_2.setDuration(500)

        self.anim3 = QPropertyAnimation(wid_medio, b"pos")
        self.anim3.setEndValue(QPoint(-1 * int(width * 0.3), 0))
        self.anim3.setDuration(500)

        self.anim4 = QPropertyAnimation(wid_izq, b"pos")
        self.anim4.setEndValue(QPoint(0, 0))
        self.anim4.setDuration(400)

        self.anim_group = QSequentialAnimationGroup()
        self.anim_group.addAnimation(self.anim3)
        self.anim_group.addAnimation(self.anim4)
        #self.anim_group.start()

        self.anim.start()
        self.anim_2.start()
        self.anim_group.start()



        self.show()

    def shapes(self):

        wid = QWidget()

        wid.setLayout(QHBoxLayout())
        bt = QPushButton("Panel")

        bt.setFixedHeight(23)
        bt.setFixedWidth(75)



        #wid.setStyleSheet("background-color:yellow;margin:0px;padding:2px;")
        wid.layout().setContentsMargins(0,0,0,0)
        wid.layout().setSpacing(20)
        wid.layout().addWidget(bt)

        wid1 = self.scene.addWidget(wid)

        wid1.setRotation(-90)
        wid1.setPos(50,50)


App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())