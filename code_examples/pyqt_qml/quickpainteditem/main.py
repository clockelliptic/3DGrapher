import sys
import os

from PyQt5.QtQuick import QQuickPaintedItem, QQuickView
from PyQt5.QtCore import QObject, QUrl, Qt, pyqtSlot, pyqtSignal, pyqtProperty
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType
from PyQt5.QtGui import (QGuiApplication, QPen, QPainter, QColor,
                         QOpenGLFramebufferObject)

# This overrides the QQuickPaintedItem.paint() method to draw simple pie chart.
# The color is defined as property so that it is exposed to Qt.

class PieChart (QQuickPaintedItem):
    def __init__(self, parent = None):
        QQuickPaintedItem.__init__(self, parent)
        self.color = QColor()

    def paint(self, painter):
        pen = QPen(self.color, 2)
        painter.setPen(pen);
        painter.setRenderHints(QPainter.Antialiasing, True);
        # From drawPie(const QRect &rect, int startAngle, int spanAngle)
        painter.drawPie(self.boundingRect().adjusted(1,1,-1,-1),
            90 * 16, 290 * 16);

    def getColor(self):
        return self.color

    def setColor(self, value):
        if value != self.color:
            self.color = value
            self.update()
            self.colorChanged.emit()

    colorChanged = pyqtSignal()
    color = pyqtProperty(QColor, getColor, setColor, notify=colorChanged)



if __name__ == '__main__':

    # setup app window
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

    app = QGuiApplication(sys.argv)

    # To make a type known to QML, register it right after instantiating the app:
    qmlRegisterType(PieChart, 'Charts', 1, 0, 'PieChart');

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)

    current_path = os.path.abspath(os.path.dirname(__file__))
    qml_file = os.path.join(current_path, 'view.qml')
    view.setSource(QUrl.fromLocalFile(qml_file))
    if view.status() == QQuickView.Error:
        sys.exit(-1)


    # Show the window
    view.show()

    # Execute & cleanup
    res = app.exec_()
    del view
    sys.exit(res)