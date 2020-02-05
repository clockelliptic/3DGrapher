from PyQt5.QtCore import (QFile, QTextStream)
from PyQt5.QtWidgets import (QApplication)


# stylesheet
import breeze_resources


from Components.App.App import App



if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    # set stylesheet
    file = QFile("./styles/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    calc = App()
    calc.show()
    sys.exit(app.exec_())

    del calc