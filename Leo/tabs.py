import sys
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QApplication, QWidget

def lol():
    print("xd")
if __name__ == '__main__':
    app = 0
    if QApplication.instance():
        app = QApplication.instance()
    else:
        app = QApplication(sys.argv)

    l1 = QTreeWidgetItem(["String A"])
    l2 = QTreeWidgetItem(["String B"])


    l1_child = QTreeWidgetItem(["Child A"])
    l1.addChild(l1_child)

    l2_child = QTreeWidgetItem(["Child B"])
    l2.addChild(l2_child)

    w = QWidget()
    w.resize(510, 210)

    tw = QTreeWidget(w)
    tw.itemChanged.connect(lol)
    tw.setAcceptDrops(True)
    tw.setDragEnabled(True)
    tw.resize(500, 200)
    tw.setHeaderHidden(True)
    tw.addTopLevelItem(l1)
    tw.addTopLevelItem(l2)

    w.show()
    sys.exit(app.exec_())