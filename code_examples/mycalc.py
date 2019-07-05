import traceback

from cytoolz import curry
import numpy as np
from sympy import *

from matplotlib import cm

import pyqtgraph as pg
import pyqtgraph.opengl as gl

from PyQt5.QtCore import Qt, QFile, QTextStream
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
        self.plotButton = self.createButton("Plot It!", self.updatePlot)
        self.latexButton = self.createButton("LaTeX!", self.showLatex)

        # latex view
        self.webView = QWebEngineView()
        self.webView.sizeHint = lambda: pg.QtCore.QSize(100, self.height()*0.2)
        self.showLatex()

        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.webView.setSizePolicy(sizePolicy)

        # add 3D plot frame
        self.glvw = gl.GLViewWidget()
        self.glvw.sizeHint = lambda: pg.QtCore.QSize(100, 450)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.webView.setSizePolicy(sizePolicy)
        self.glvw.setBackgroundColor('k')


        # add the coordinate planes

        ## create three grids, add each to the view
        x0grid = gl.GLGridItem(color=[.1,.1,.1,0.1])
        x1grid = gl.GLGridItem(color=[.1,.1,.1,0.1])
        y0grid = gl.GLGridItem(color=[.1,.1,.1,0.1])
        y1grid = gl.GLGridItem(color=[.1,.1,.1,0.1])
        zgrid = gl.GLGridItem(color=[.1,.1,.1,0.1])

        self.glvw.addItem(x0grid)
        self.glvw.addItem(y0grid)
        self.glvw.addItem(x1grid)
        self.glvw.addItem(y1grid)
        self.glvw.addItem(zgrid)

        ## rotate x and y grids to face the correct direction
        x0grid.rotate(90, 0, 1, 0)
        y0grid.rotate(90, 1, 0, 0)

        x1grid.rotate(90, 0, 1, 0)
        y1grid.rotate(90, 1, 0, 0)

        x0grid.translate(-25,0,0)
        y0grid.translate(0,-25,0)

        x1grid.translate(25,0,0)
        y1grid.translate(0,25,0)

        zgrid.translate(0,0,0)

        ## scale each grid
        x0grid.scale(2.5, 2.5, 2.5)
        y0grid.scale(2.5, 2.5, 2.5)

        x1grid.scale(2.5, 2.5, 2.5)
        y1grid.scale(2.5, 2.5, 2.5)

        zgrid.scale(2.5, 2.5, 2.5)

        x0grid.setSpacing(20,20,20)
        y0grid.setSpacing(20,20,20)

        x1grid.setSpacing(20,20,20)
        y1grid.setSpacing(20,20,20)

        zgrid.setSpacing(20,20,20)


        # initialize data and plot example graph
        self.xs, self.ys = np.mgrid[-5:5:int(12*3)*1j, -5:5:(12*3)*1j]
        self.zs = (5*np.sin(self.xs)*np.sin(self.ys))/(self.xs*self.ys)

        self.data0 = gl.GLSurfacePlotItem(z=self.zs, shader='shaded', smooth=True,
                                          drawEdges=True, edgeColor=(0., 0.3, 0.3, 0.5),
                                          drawFaces=True)
        self.data0.setColor([0.3,0.2,0.9,0.75])
        self.data0.setDepthValue(0)
        self.data0.setGLOptions('additive')

        self.data0.translate(-25,-25,0)

        self.glvw.addItem(self.data0)


        mainLayout.addWidget(self.simplifyExpression, 0, 0, 1, 3)
        mainLayout.addWidget(self.display, 2, 0)
        mainLayout.addWidget(self.plotButton, 2, 1)
        mainLayout.addWidget(self.latexButton, 2, 2)
        mainLayout.addWidget(self.webView, 3, 0, 1, 3)
        mainLayout.addWidget(self.glvw, 4, 0, 1, 3)


        self.setLayout(mainLayout)

        self.x, self.y = symbols('x y')



    def validateInput(self):

        try:
            lambdify((self.x, self.y), sympify(self.display.text()))(1,1)
            self.display.setStyleSheet('''QLineEdit:hover {border: 0.2ex solid #3daee9;}
                                          QLineEdit:focus {border: 0.2ex solid #3daee9;}
            ''')
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

            self.pageSource = """
                <html><head><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
                </script></head><body style="background-color: #31363b;"><p><mathjax style="font-size:1.5em; color:#FFF">$${}$$</mathjax></p></body></html>
                """.format(str(expressionValue))

            self.webView.setHtml(self.pageSource)
            print(expressionValue)

        except Exception as err:
            print(err)

    def createButton(self, text, member):
        button = Button(text)
        button.clicked.connect(member)
        return button

    def updatePlot(self):
        try:
            expressionValue = sympify(self.display.text())

            self.zs = lambdify((self.x, self.y), expressionValue)(self.xs, self.ys)
            self.data0.setData(z=self.zs)

        except:
            pass

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