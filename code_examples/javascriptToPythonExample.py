import sys
from PyQt5.QtCore import pyqtSlot, QUrl, QObject, QSize
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLayout, QLineEdit,
                             QSizePolicy, QToolButton, QWidget, QLabel, QCheckBox,
                             QSizePolicy)
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


class MainAppWindow(QWidget):

    pageSource = '''
    <html>
        <head>
        </head>
        <body>
            <script src='https://ajax.googleapis.com/ajax/libs/jquery/1.12.2/jquery.min.js'</script>
            <script src='qrc:///qtwebchannel/qwebchannel.js'></script>
        <h1>hello</h1>
        <ul>
            <li>list item 1</li>
            <li>list item 2</li>
        </ul>
        <a href='#go'>GO</a>

    </body>
    '''

    def __init__(self, parent=None):
        super(MainAppWindow, self).__init__(parent)
        self.setWindowTitle("Fancy Business")

        self.webView = QWebEngineView()
        self.webView.sizeHint = lambda: QSize(400, 150)
        self.webView.setHtml(self.pageSource)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.webView, 0, 0)

        self.channel = QWebChannel(self.webView.page())
        self.webView.page().setWebChannel(self.channel)

        self.helper_bridge = Bridge()
        self.channel.registerObject("helperBridge", self.helper_bridge)



class Bridge(QObject):
    @pyqtSlot()
    def some_slot():
        print("SUCCESS")


if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    view = MainAppWindow()
    view.webView.show()
    app.exec_()