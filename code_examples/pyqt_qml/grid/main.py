import sys
import os

from PyQt5.QtCore import QObject, QUrl, Qt, pyqtSlot, pyqtSignal, pyqtProperty
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine

if __name__ == '__main__':

    # setup app window
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Expose a model to the QML code
    my_model = None

    engine.rootContext().setContextProperty("myModel", my_model)

    # Load QML file
    engine.load('./pyqt_qml/view.qml')
    if not engine.rootObjects():
        sys.exit(-1)

    # Show the window
    #engine.show()

    # Execute & cleanup
    sys.exit(app.exec_())
    del engine