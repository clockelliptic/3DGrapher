from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QWidget, QApplication, QHBoxLayout,
                             QToolButton, QMenu, QTextBrowser, QWidgetAction)

class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QHBoxLayout(self)
        self.button = QToolButton(self)
        self.button.setPopupMode(QToolButton.MenuButtonPopup)
        self.button.setMenu(QMenu(self.button))
        self.textBox = QTextBrowser(self)
        action = QWidgetAction(self.button)
        action.setDefaultWidget(self.textBox)
        self.button.menu().addAction(action)
        layout.addWidget(self.button)

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.resize(100, 60)
    window.show()
    sys.exit(app.exec_())