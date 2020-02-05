import os
import time
import traceback
import random

import scipy.interpolate
from scipy.interpolate import griddata

from cytoolz import curry

import numpy as np
from sympy import *
import sympy as sy

from matplotlib import cm
from matplotlib.pyplot import colormaps as mpl_cmaps
from matplotlib.pyplot import figure as plt_figure, Axes as plt_Axes, savefig as plt_savefig, close as plt_close

import pyqtgraph as pg
import pyqtgraph.opengl as gl
import OpenGL.GL as ogl

from sip import delete
from PyQt5.QtGui import (QPalette, QColor, QFont, qRgba, QIcon, QImage, QPainter, QPixmap,
                         QBrush, QWindow)
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import (Qt, QFile, QTextStream, QSize, QFileInfo, QByteArray, pyqtSignal,
                          QTimer, QPropertyAnimation, QEasingCurve, QRect)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLayout, QLineEdit,
                             QSizePolicy, QToolButton, QWidget, QLabel, QCheckBox,
                             QTableView, QTableWidget, QTableWidgetItem, QToolBar,
                             QToolBox, QWidget, QPushButton, QFrame, QGraphicsOpacityEffect,
                             QMenu, QVBoxLayout, QScrollArea, QWidgetAction)

from PyQt5.QtWebEngineWidgets import QWebEngineView


from Components.BigButton.BigButton import BigButton
from Components.ColormapMenu.ColormapMenu import ColormapMenu
from Components.Custom3DAxis.Custom3DAxis import Custom3DAxis
from Components.CustomGLTextItem.CustomGLTextItem import CustomGLTextItem
from Components.CustomSVGIcon.CustomSVGIcon import CustomSVGIcon
from Components.EquationInput.EquationInput import EquationInput
from Components.EquationTableSpacer.EquationTableSpacer import EquationTableSpacer
from Components.GradientIconButton.GradientIconButton import GradientIconButton
from Components.InputSettingsBar.InputSettingsBar import InputSettingsBar
from Components.LatexDisplay.LatexDisplay import LatexDisplay
from Components.MainToolbar.MainToolbar import MainToolbar
from Components.MiniButton.MiniButton import MiniButton
from Components.MiniGradientButton.MiniGradientButton import MiniGradientButton
from Components.SurfacePlot.SurfacePlot import SurfacePlot



class EquationTableItem(QFrame):
    def __init__(self, name, linkedGraph, parent=None):
        super(EquationTableItem, self).__init__(parent)

        self.name = name
        self.linkedGraph = linkedGraph

        # initialize local math symbols
        self.x, self.y, self.z = sy.symbols('x y z')
        self.phi, self.theta, self.r, self.rho = sy.symbols('phi, theta, r, rho')
        self.i, self.j, self.k = sy.symbols('i j k')
        self.u, self.v, self.w = sy.symbols('u v w')

        # math expression input box
        self.display = EquationInput("")
        self.display.textChanged.connect(self.showLatex)

        # option to simplify the math expression in LaTeX output
        self.simplifyExpression = QCheckBox("Simplify", self)
        self.simplifyExpression.stateChanged.connect(self.simplifyChecked)
        self.simplifyExpressionChecked = False
        self.simplifyExpression.setMaximumHeight(15)

        # mini settings bar, including cog igon, colorpicker, etc..
        self.settingsBar = InputSettingsBar(name = self.name, linkedGraph = self.linkedGraph, parent = self)
        self.settingsBar.plotButton.clicked.connect(self.updateGraphView)
        self.settingsBar.hideButton.clicked.connect(self.hideGraphItem)
        self.settingsBar.deleteButton.clicked.connect(self.deleteGraphItem)
        self.hidden = False

        # latex view
        self.mathJaxWebView = LatexDisplay()
        self.mathJaxWebView.loadFinished.connect(self.showLatex)

        # setup input table layout and sizing
        self.setMaximumHeight(150)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.layout = QGridLayout()

        self.layout.addWidget(self.display, 0, 0, 2, 1)
        self.layout.addWidget(self.settingsBar, 0, 1)
        self.layout.addWidget(self.simplifyExpression, 1, 1)
        self.layout.addWidget(self.mathJaxWebView, 2, 0, 3, 1)

        self.setStyleSheet("""
                            EquationTableItem {
                                border-bottom: 0.2ex dashed rgba(200,225,255,0.2);
                            }
                            """)
        self.layout.setContentsMargins(0,11,11,11)

        #fadeInAnimator(self)

        self.setLayout(self.layout)
        self.display.setFocus() # bring text input box into keyboard focus

    def fadeInAnimator(obj):
        opacity_effect = QGraphicsOpacityEffect(self)
        opacity_effect.setOpacity(0)
        self.setGraphicsEffect(opacity_effect)

        self.fadeIn = QPropertyAnimation(opacity_effect, b"opacity")
        self.fadeIn.setDuration(350)
        self.fadeIn.setStartValue(0)
        self.fadeIn.setEndValue(1)
        self.fadeIn.setEasingCurve(QEasingCurve.InCubic)
        self.fadeIn.start(QPropertyAnimation.DeleteWhenStopped)

    def deleteGraphItem(self):
        self.linkedGraph.removeItem(self.linkedGraph.data[self.name])
        del self.linkedGraph.data[self.name]
        self.parent().removeInputItem(self.name)


    def hideGraphItem(self):
        if self.hidden==False:
            self.linkedGraph.removeItem(self.linkedGraph.data[self.name])
            self.hidden = True
        else:
            self.linkedGraph.addItem(self.linkedGraph.data[self.name])
            self.hidden = False

    def simplifyChecked(self, state):
        '''If 'Simplify' checkbox is checked, this simplifies the
           equation before returning MathJax-rendered equation
        '''
        if state == Qt.Checked:
            self.simplifyExpressionChecked = True
        else:
            self.simplifyExpressionChecked = False
        self.showLatex()

    def validateInput(self):
        '''Checks user's equation to see if it is valid and gives visual feedback.
        '''
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
        '''Renders and displays the typesetted equation if user input is valid.
        '''
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
        '''Sends user's equation as string to JS MathJax renderer in LatexDisplay.
        '''
        self.mathJaxWebView.page().runJavaScript("updateMathJax(\"$${}$$\")".format(newMath.replace("\\", "\\\\")))

    def updateGraphView(self):
        graphViewItem = self.linkedGraph.data[self.name]

        if self.validateInput() == True:
            try:
                expressionValue = sympify(self.display.text())

                graphViewItem.equation = lambdify((self.x, self.y), expressionValue)
                graphViewItem.updatePlot()
            except Exception:
                traceback.print_exc()

        else:
            pass
