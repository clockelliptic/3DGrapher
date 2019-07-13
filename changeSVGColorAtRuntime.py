import sip
try:
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
except err:
    log.error(err)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
import sys

if __name__ == '__main__':

    app = QApplication(sys.argv)

    root = QFileInfo(__file__).absolutePath()

    f = QFile(root+'/icons/protractor.svg')
    if f.open(QFile.ReadOnly | QFile.Text):
        textStream = QTextStream(f)
        svgData = textStream.readAll().replace('fill="#000000"', 'fill="#eeeeee"')
        f.close()
    #print(svgData)
    #help(QImage)

    svg = QSvgRenderer(QByteArray().append(svgData))
    qim = QImage(76, 76, QImage.Format_RGBA8888)
    qim.fill(0)#QColor(qRgba(155,255,255,10)))
    painter = QPainter()

    painter.begin(qim)
    svg.render(painter)
    painter.end()

    qim.save('icons/test2.png')