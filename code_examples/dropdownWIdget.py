from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#ANCHOR: MiniButton
#  custom mini QBUttons for InputSettingsBar
class MiniButton(QPushButton):
    def __init__(self, iconpath, parent, onClicked):
        super(MiniButton, self).__init__(parent)
        self.clicked.connect(onClicked)
        self.setIcon(QIcon(iconpath))
        self.setFixedSize(24, 24)
        root = QFileInfo(__file__).absolutePath()
        self.setStyleSheet('''
                            MiniButton
                            {
                                background-color: transparent;
                                border: none;
                                margin: 0ex;
                                padding: 0ex;
                                icon-size:35px 35px;
                            }

                            MiniButton:hover
                            {
                                background-color: rgba(0,0,0,0.1);
                            }

                            MiniButton:pressed
                            {
                                background-color: rgba(0,0,0,0.2);
                            }

                            MiniButton::menu-indicator
                            {
                                image: none;;
                            }
                            ''')

class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QHBoxLayout(self)

        root = QFileInfo(__file__).absolutePath()
        self.button = MiniButton(root+'../../icons/cog.png',
                                         parent = self,
                                         onClicked = self.handleButton)

        self.button.setMenu(QMenu(self.button))

        self.menuBox = QFrame(self)
        self.menuBox.setMinimumSize(200,200)
        self.menuBox.setStyleSheet("background-color: #aaaaaa")
        menuBoxLayout = QGridLayout()
        self.menuBox.setLayout(menuBoxLayout)

        action = QWidgetAction(self.button)
        action.setDefaultWidget(self.menuBox)
        self.button.menu().addAction(action)

        layout.addWidget(self.button)

        self.setStyleSheet("background-color: #31363b")

    def handleButton(self):
        pass

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.resize(100, 60)
    window.show()
    sys.exit(app.exec_())