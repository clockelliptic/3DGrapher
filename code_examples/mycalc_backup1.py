#######################################################################################
#
# Separate business logic from UI objects. Increase testability and portability.
#
# Store objects as JSON wherever possible when sharing them amongst languages.
#
#######################################################################################


import traceback
import random
import scipy.interpolate
from scipy.interpolate import griddata

import numpy as np
from sympy import *

from matplotlib import cm
from matplotlib.pyplot import colormaps as mpl_cmaps

import pyqtgraph as pg
import pyqtgraph.opengl as gl

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QFile, QTextStream, QSize
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLayout, QLineEdit,
                             QSizePolicy, QToolButton, QWidget, QLabel, QCheckBox,
                             QTableView, QTableWidget, QTableWidgetItem, QToolBar, QToolBox,
                             QWidget)
from PyQt5.QtWebEngineWidgets import QWebEngineView

# stylesheet
import breeze_resources

class Button(QToolButton):
    def __init__(self, text, parent=None):
        super(Button, self).__init__(parent)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.setText(text)

class GraphView(gl.GLViewWidget):
    def __init__(self, parent=None):
        super(GraphView, self).__init__(parent)

        # set default resolution to 2
        self.resolution = 2

        # dictionary for storing all graph objects
        self.data = {}

        # style and size of the GLViewWidget
        self.sizeHint = lambda: QSize(100, 450)
        self.setMinimumWidth(500)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setBackgroundColor('#31363b')

        # add the coordinate plane box
        x0grid = gl.GLGridItem(color=[.1,.1,.1,0.1])
        x1grid = gl.GLGridItem(color=[.1,.1,.1,0.1])
        y0grid = gl.GLGridItem(color=[.1,.1,.1,0.1])
        y1grid = gl.GLGridItem(color=[.1,.1,.1,0.1])
        zgrid  = gl.GLGridItem(color=[.1,.1,.1,0.1])

        self.addItem(x0grid)
        self.addItem(y0grid)
        self.addItem(x1grid)
        self.addItem(y1grid)
        self.addItem(zgrid)

        ## make all planes perpendicular / normal to each other
        x0grid.rotate(90, 0, 1, 0)
        y0grid.rotate(90, 1, 0, 0)

        x1grid.rotate(90, 0, 1, 0)
        y1grid.rotate(90, 1, 0, 0)

        ## scale the grids and move them into place
        x0grid.translate(-10*self.resolution,0,0)
        y0grid.translate(0,-10*self.resolution,0)

        x1grid.translate(10*self.resolution,0,0)
        y1grid.translate(0,10*self.resolution,0)

        zgrid.translate(0,0,0)

        x0grid.scale(self.resolution, self.resolution, self.resolution)
        y0grid.scale(self.resolution, self.resolution, self.resolution)

        x1grid.scale(self.resolution, self.resolution, self.resolution)
        y1grid.scale(self.resolution, self.resolution, self.resolution)

        zgrid.scale(self.resolution, self.resolution, self.resolution)

        # set spacing between grid lines
        x0grid.setSpacing(20,20,20)
        y0grid.setSpacing(20,20,20)

        x1grid.setSpacing(20,20,20)
        y1grid.setSpacing(20,20,20)

        zgrid.setSpacing(20,20,20)

        self.setCameraPosition(distance=80)#, elevation=42, azimuth=42)

    def applyColormap(self):
        self.cmap = cm.get_cmap("inferno")
        self.colormap = self.cmap((self.zs - self.zs.min())/(self.zs.max() - self.zs.min()))

    def addPlotItem(self, name):
        # generate a colormap for the surface
        self.data[name] = SurfacePlot(resolution=self.resolution)

        # show the GLSurfacePlotItem in the GLViewWidget
        self.addItem(self.data[name])


class SurfacePlot(gl.GLSurfacePlotItem):
    def __init__(self, resolution,): #parent=None):
        super(SurfacePlot, self).__init__(smooth=True, shader='shaded',
                                          drawEdges=True, drawFaces=True,
                                          edgeColor=(0.3, 0.3, 0.3, 0.1))
        self.resolution = resolution

        # variable for storing current equation
        self.equation = None

        # generate default graph data
        self.xs, self.ys = np.mgrid[-5:5:int(20*self.resolution + 1)*1j, -5:5:(20*self.resolution + 1)*1j]
        self.updatePlot()

        # align the plotted data to the center of the graph
        self.translate(-10*self.resolution,-10*self.resolution,0)

        # graph aesthetics
        self.setData(z = np.zeros(shape=self.xs.shape))

        self.colormaps = [i for i in mpl_cmaps() if '_r' not in i]

        self.setShader('shaded')
        self.setGLOptions('additive')
        self.applyColormap()

    def applyColormap(self):
        self.cmap = cm.get_cmap("inferno")
        self.colors = self.cmap((self.zs - self.zs.min())/(self.zs.max() - self.zs.min()))

    def updateResolution(self, new_resolution):
        self.resolution = new_resolution
        self.xs, self.ys = np.mgrid[-5:5:int(20*self.resolution + 1)*1j, -5:5:(20*self.resolution + 1)*1j]
        self.updatePlot()

    def updatePlot(self):
        if self.equation == None:
            self.zs = np.zeros(self.xs.shape)
            self.setData(z = self.zs)
        else:
            self.zs = self.equation(self.xs, self.ys)
            self.zs = self.validateData(self.zs)
            self.setData(z = self.zs)
        self.applyColormap()

    def validateData(self, zs):
        if not np.isnan(zs.flatten()).any(0):
            return zs
        else: # interpolate missing values
            # integer arrays for indexing
            x_indx, y_indx = np.meshgrid(np.arange(0, zs.shape[1]),
                                         np.arange(0, zs.shape[0]))
            # mask all invalid values
            zs_masked = np.ma.masked_invalid(zs)
            # retrieve the valid, non-Nan, defined values
            valid_xs = x_indx[~zs_masked.mask]
            valid_ys = y_indx[~zs_masked.mask]
            valid_zs = zs_masked[~zs_masked.mask]
            # generate interpolated array of z-values
            zs_interp = scipy.interpolate.griddata((valid_xs, valid_ys), valid_zs.ravel(),
                                             (x_indx, y_indx), method='cubic')
            # finally, return the data
            return zs_interp

class EquationInputBox(QLineEdit):
    def __init__(self, parent=None):
        super(EquationInputBox, self).__init__(parent)
        self.setReadOnly(False)

        font = self.font()
        font.setPointSize(font.pointSize() + 6)
        self.setFont(font)

        self.setAlignment(Qt.AlignLeft)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.setMaximumHeight(50)

class EquationTable(QWidget):
    def __init__(self, linkedGraph, parent=None):
        super(EquationTable, self).__init__()

        self.linkedGraph = linkedGraph
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.inputs = {}

        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding))
        self.setMaximumWidth(500)
        self.setMinimumWidth(250)

    def addInputItem(self, name):
        self.inputs[name] = EquationTableItem(name, self.linkedGraph)
        self.layout.addWidget(self.inputs[name], 0, 0)

class EquationTableItem(QWidget):
    def __init__(self, name, linkedGraph, parent=None):
        super(EquationTableItem, self).__init__(parent)
        self.name = name
        self.linkedGraph = linkedGraph

        # initialize local math symbols
        self.x, self.y, self.z = symbols('x y z')
        self.phi, self.theta, self.r, self.rho = symbols('phi, theta, r, rho')
        self.i, self.j, self.k = symbols('i j k')
        self.u, self.v, self.w = symbols('u v w')

        # math expression input box
        self.display = EquationInputBox("5*sin(x)*sin(y)")
        self.display.textChanged.connect(self.showLatex)

        # option to simplify the math expression in LaTeX output
        self.simplifyExpression = QCheckBox("Simplify", self)
        self.simplifyExpression.stateChanged.connect(self.simplifyChecked)
        self.simplifyExpressionChecked = False
        self.simplifyExpression.setMaximumHeight(15)

        # plot render button
        self.plotButton = self.createButton("Plot It!", self.updateGraphView)

        # latex view
        self.webView = LatexView()
        self.webView.loadFinished.connect(self.showLatex)

        # setup input table layout and sizing
        self.setMaximumHeight(150)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.layout = QGridLayout()

        self.layout.addWidget(self.display, 0, 0, 2, 1)
        self.layout.addWidget(self.plotButton, 0, 1)
        self.layout.addWidget(self.simplifyExpression, 1, 1)
        self.layout.addWidget(self.webView, 2, 0, 1, 4)

        self.setLayout(self.layout)

    def createButton(self, text, member):
        button = Button(text)
        button.clicked.connect(member)
        return button

    def simplifyChecked(self, state):
        if state == Qt.Checked:
            self.simplifyExpressionChecked = True
        else:
            self.simplifyExpressionChecked = False
        self.showLatex()

    def validateInput(self):
        try:
            lambdify((self.x, self.y), sympify(self.display.text()))(1,1)
            self.display.setStyleSheet('''QLineEdit:hover {border: 0.2ex solid #3daee9;}
                                          QLineEdit:focus {border: 0.2ex solid #3daee9;}
            ''')
            return True
        except:
            self.display.setStyleSheet('''QLineEdit:hover {border: 0.2ex solid #ee1111;}
                                          QLineEdit:focus {border: 0.2ex solid #ee1111;}
            ''')
            return False

    def showLatex(self):
        if self.validateInput() == True:
            try:
                if self.simplifyExpressionChecked == True:
                    expressionValue = latex(sympify(self.display.text()))
                else:
                    expressionValue = latex(sympify(self.display.text(), evaluate=False))

                self.updateJax(expressionValue)

            except Exception as err:
                print(err)
        elif self.display.text() == "" or all(self.display.text()) == " ":
            self.updateJax("...")
        else:
            pass

    def updateJax(self, newMath):
            self.webView.page().runJavaScript("updateMathJax(\"$${}$$\")".format(newMath.replace("\\", "\\\\")))

    def updateGraphView(self):
        graphViewItem = self.linkedGraph.data[self.name]

        if self.validateInput() == True:
            expressionValue = sympify(self.display.text())

            graphViewItem.equation = lambdify((self.x, self.y), expressionValue)
            graphViewItem.updatePlot()

        else:
            pass

class LatexView(QWebEngineView):
    pageSource = """
                    <html style="max-height:60px; overflow:hidden;">
                    <head>
                        <meta charset="UTF-8">
                        <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
                        MathJax.Hub.Config({
                            extensions: ["tex2jax.js"],
                            jax: ["input/TeX","output/HTML-CSS"],
                            tex2jax: {inlineMath: [["$","$"],["\\(","\\)"]]}
                        });
                        </script>

                        <style>
                        .center {
                            margin: 0;
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            -ms-transform: translate(-50%, -50%);
                            transform: translate(-50%, -50%);
                        }

                        </style>
                    </head>
                    <body style="background-color: #31363b;">

                        <script>
                            function updateMathJax(TeX) {
                                /// set up new mathjax div content
                                document.getElementById("MathOutput").innerHTML = TeX;
                                /// update new mathjax div content
                                MathJax.Hub.Queue(["Typeset",MathJax.Hub,"MathOutput"]);
                            }
                        </script>

                        <div class="center">
                            <mathjax id="MathOutput" style="font-size:1.5em; color:#FFF">${}$</mathjax>
                        </div>

                    </body>
                    </html>
                    """
    def __init__(self, parent=None):
        super(LatexView, self).__init__(parent)
        self.page().setBackgroundColor(QColor('#31363b'))
        self.setMaximumHeight(80)
        self.setMinimumHeight(60)
        self.setHtml(self.pageSource)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))


class CalculatorApp(QWidget):
    def __init__(self, parent=None):
        super(CalculatorApp, self).__init__(parent)

        # window title & top-level layout
        self.setWindowTitle("SuperCalc")
        mainLayout = QGridLayout()

        # initialize reserved abstract math symbols and user-defined symbol dictionary
        self.x, self.y, self.z = symbols('x y z')
        self.phi, self.theta, self.r, self.rho = symbols('phi, theta, r, rho')
        self.i, self.j, self.k = symbols('i j k')
        self.u, self.v, self.w = symbols('u v w')
        self.usrvars = {}

        # initialize graph
        self.graphView = GraphView()

        # setup input table to contain equation entries
        self.inputTable = EquationTable(linkedGraph=self.graphView)

        # initialize default graph and its respective equation entry
        name = self.newName()
        self.graphView.addPlotItem(name=name)
        self.inputTable.addInputItem(name=name)
        self.inputTable.inputs[name].updateGraphView()

        # add all objects to main layout
        mainLayout.addWidget(self.inputTable, 0, 0,)
        mainLayout.addWidget(self.graphView, 0, 1,)

        self.setLayout(mainLayout)

    def newName(self):
        name = random.getrandbits(512)
        if name not in self.inputTable.inputs.keys():
            return name
        else:
            self.newName()

    def createButton(self, text, member):
        button = Button(text)
        button.clicked.connect(member)
        return button

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    # set stylesheet
    file = QFile(":/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    calc = CalculatorApp()
    calc.show()
    sys.exit(app.exec_())

    del calc