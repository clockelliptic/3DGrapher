import traceback

from cytoolz import curry
import numpy as np
from sympy import *

from matplotlib import cm

import pyqtgraph as pg
import pyqtgraph.opengl as gl

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QFile, QTextStream, QEvent, QCoreApplication
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLayout, QLineEdit,
                             QSizePolicy, QToolButton, QWidget, QLabel, QCheckBox,
                             QSizePolicy)
from PyQt5.QtWebEngineWidgets import QWebEngineView

# stylesheets
import qdarkstyle
import breeze_resources

class Button(QToolButton):
    def __init__(self, text, parent=None):
        super(Button, self).__init__(parent)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.setText(text)

class Calculator(QWidget):

    def __init__(self, parent=None):
        super(Calculator, self).__init__(parent)

        # window title
        self.setWindowTitle("SuperCalc")

        # create main grid layout
        mainLayout = QGridLayout()
        #mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # math expression input box
        self.display = QLineEdit("20*sin(x)*sin(y)/(x*y)")
        self.display.setReadOnly(False)
        self.display.setAlignment(Qt.AlignLeft)

        font = self.display.font()
        font.setPointSize(font.pointSize() + 6)
        self.display.setFont(font)
        self.display.setSizePolicy(sizePolicy)
        self.display.setMaximumHeight(40)

        self.display.textChanged.connect(self.validateInput)

        # option to simplify the math expression in LaTeX output
        self.simplifyExpression = QCheckBox("Simplify Expression",self)
        self.simplifyExpression.stateChanged.connect(self.simplifyChecked)
        self.simplifyExpression.setMaximumHeight(15)
        self.simplifyExpressionChecked = False

        # plot and LaTeX render buttons
        self.latexButton = self.createButton("LaTeX!", self.showLatex)

        # latex view
        self.webView = QWebEngineView()
        self.webView.sizeHint = lambda: pg.QtCore.QSize(100, self.height()*0.2)
        self.showLatex()

        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.webView.setSizePolicy(sizePolicy)


        mainLayout.addWidget(self.simplifyExpression, 0, 0, 1, 3)
        mainLayout.addWidget(self.display, 2, 0)
        mainLayout.addWidget(self.latexButton, 2, 2)
        mainLayout.addWidget(self.webView, 3, 0, 1, 3)

        self.setLayout(mainLayout)

        self.x, self.y = symbols('x y')



    def validateInput(self):

        try:
            lambdify((self.x, self.y), sympify(self.display.text()))(1,1)
            self.display.setStyleSheet('''QLineEdit:hover {border: 0.2ex solid #3daee9;}
                                          QLineEdit:focus {border: 0.2ex solid #3daee9;}
            ''')
            try:
                #self.sendkeys(Qt.Key_Enter)
                #self.sendkeys(Qt.Key_Return)
                self.updateJax()
            except Exception as err:
                print(err)
        except:
            self.display.setStyleSheet('''QLineEdit:hover {border: 0.2ex solid #ee1111;}
                                          QLineEdit:focus {border: 0.2ex solid #ee1111;}
            ''')

    def simplifyChecked(self, state):
        if state == Qt.Checked:
            self.simplifyExpressionChecked = True
        else:
            self.simplifyExpressionChecked = False

    def showLatex(self):
        try:
            if self.simplifyExpressionChecked == True:
                expressionValue = latex(sympify(self.display.text()))
            else:
                expressionValue = latex(sympify(self.display.text(), evaluate=False))

            self.pageSource = """<!doctype html>
<html>
<head>
<title>MathJax Dynamic Math Test Page</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
  MathJax.Hub.Config({
    extensions: ["tex2jax.js"],
    jax: ["input/TeX","output/HTML-CSS"],
    tex2jax: {inlineMath: [["$","$"],["\\(","\\)"]]}
  });
</script>

</head>
<body>

<script>
  //
  //  Use a closure to hide the local variables from the
  //  global namespace
  //
  (function () {
    var QUEUE = MathJax.Hub.queue;  // shorthand for the queue
    var math = null;                // the element jax for the math output.

    //
    //  Get the element jax when MathJax has produced it.
    //
    QUEUE.Push(function () {
      math = MathJax.Hub.getAllJax("MathOutput")[0];
    });

    //
    //  The onchange event handler that typesets the
    //  math entered by the user
    //
     window.UpdateMath = function (TeX) {
    //set the MathOutput HTML
    document.getElementById("MathOutput").innerHTML = TeX;

    //reprocess the MathOutput Element
    MathJax.Hub.Queue(["Typeset",MathJax.Hub,"MathOutput"]);
}
  })();
</script>

Type some TeX code:
<div id="MathOutput">
You typed: ${}$
</div>

</body>
</html>"""
            self.webView.setHtml(self.pageSource)

        except Exception as err:
            print(err)

    def createButton(self, text, member):
        button = Button(text)
        button.clicked.connect(member)
        return button

    def sendkeys(self, char, modifier=Qt.NoModifier, text=None):
        if not text:
            event = QtGui.QKeyEvent(QEvent.KeyPress, char, modifier)
        else:
            event = QtGui.QKeyEvent(QEvent.KeyPress, char, modifier, text)
        QCoreApplication.postEvent(self.webView, event)

    def updateJax(self,):
        self.webView.page().runJavaScript('updateMath(\"hi\")', self.ready)

    def ready(self, returnValue):
        print(returnValue)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    # set breezestyles stylesheet
    file = QFile(":/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())

    #app.exit(-1)