import os

from PyQt5.QtGui import QIcon, QPainter, QImage, QPixmap
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt, QFile, QTextStream, QFileInfo, QByteArray, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QGridLayout, QVBoxLayout, QSizePolicy,
                             QWidget, QToolButton, QScrollArea,)

# stylesheet
import breeze_resources

#ANCHOR: CustomSVGIcons
# Parse SVG icon files, set a custom fill color, return a dictionary
class CustomSVGIcons():
    def __init__(self):
        root = QFileInfo(__file__).absolutePath()

        svg_files = os.listdir(root+"/icons/svg/")

        self.images = {}

        for filename in svg_files:
            f = QFile(root+'/icons/svg/'+filename)
            if f.open(QFile.ReadOnly | QFile.Text):
                textStream = QTextStream(f)
                svgData = textStream.readAll().replace('fill="#000000"', 'fill="#eeeeee"')
                svgData_hover = svgData.replace('fill="#eeeeee"', 'fill="#3daee9"')
                f.close()

            svg = QSvgRenderer(QByteArray().append(svgData))
            svg_hover = QSvgRenderer(QByteArray().append(svgData_hover))

            qim = QImage(76, 76, QImage.Format_RGBA8888)
            qim.fill(0)
            painter = QPainter()
            painter.begin(qim)
            svg.render(painter)
            painter.end()

            qim_hover = QImage(76, 76, QImage.Format_ARGB32)
            qim_hover.fill(0)
            painter = QPainter()
            painter.begin(qim_hover)
            svg_hover.render(painter)
            painter.end()

            self.images[filename.replace("appbar.","").replace(".svg","")] = (QIcon(QPixmap.fromImage( qim )),
                                                                              QIcon(QPixmap.fromImage( qim_hover )))

    def do(self):
        return self.images

#ANCHOR: BigMiniButton
class BigMiniButton(QToolButton):
    mouseHover = pyqtSignal(bool)

    def __init__(self, text, icon, hovericon, parent, onClicked):
        super(BigMiniButton, self).__init__(parent)
        self.icon = icon
        self.hovericon = hovericon

        self.clicked.connect(onClicked)
        self.setIcon(self.icon)
        self.setText(text)
        self.setFixedSize(48, 48)

        self.setStyleSheet('''
                            BigMiniButton
                            {
                                color: #eeeeee;
                                background-color: transparent;
                                border: 0ex solid #3daee9;
                                margin: 0ex;
                                padding: 0ex;
                                icon-size:48px 48px;
                            }

                            BigMiniButton:hover
                            {
                            background-color: rgba(0,0,0,0.1);
                            color: #3daee9;
                            }

                            BigMiniButton:pressed
                            {
                            background-color: rgba(0,0,0,0.2);
                            }
                            ''')

        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setMinimumSize(75, 75)

    def enterEvent(self, event):
        self.mouseHover.emit(True)
        self.setIcon(self.hovericon)

    def leaveEvent(self, event):
        self.mouseHover.emit(False)
        self.setIcon(self.icon)

class PrintImage(QWidget):
    def __init__(self, pixmap, parent=None):
        QWidget.__init__(self, parent=parent)
        self.pixmap = pixmap
        self.setFixedSize(100,100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)

#ANCHOR: Main app
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()

        # Create SVG Icon showcase
        buttonGridContainer = QWidget()
        buttonGridContainer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        buttonGrid = QGridLayout()
        buttonGridContainer.setLayout(buttonGrid)

        scrollarea = QScrollArea()
        scrollarea.setWidget(buttonGridContainer)
        scrollarea.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea {border: none;}")

        icon_dict = CustomSVGIcons().do()
        buttons = []
        for n, i in enumerate(icon_dict.keys()):
                button = BigMiniButton(i, icon=icon_dict[i][0],
                                       hovericon=icon_dict[i][1],
                                       parent = self,
                                       onClicked = self.handleButtonClick)
                button.setToolTip(i)
                buttonGrid.addWidget(button, n//15, n%15)

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(scrollarea)
        self.setWindowIcon(icon_dict["calculator"][0])
        self.setWindowTitle("Qt Showcase: Modern UI Icons")

    def handleButtonClick(self):
        pass

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    # set stylesheet
    file = QFile(":/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    calc = MainWindow()
    calc.show()
    sys.exit(app.exec_())
