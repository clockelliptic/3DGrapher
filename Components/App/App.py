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
from Components.EquationTable.EquationTable import EquationTable
from Components.EquationTableItem.EquationTableItem import EquationTableItem
from Components.EquationTableSpacer.EquationTableSpacer import EquationTableSpacer
from Components.GradientIconButton.GradientIconButton import GradientIconButton
from Components.GraphView.GraphView import GraphView
from Components.InputSettingsBar.InputSettingsBar import InputSettingsBar
from Components.LatexDisplay.LatexDisplay import LatexDisplay
from Components.MainToolbar.MainToolbar import MainToolbar
from Components.MiniButton.MiniButton import MiniButton
from Components.MiniGradientButton.MiniGradientButton import MiniGradientButton
from Components.SurfacePlot.SurfacePlot import SurfacePlot



class App(QWidget):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        # window title & top-level layout
        self.setWindowTitle("SuperCalc")
        mainLayout = QGridLayout()

        # initialize reserved abstract math symbols and user-defined symbol dictionary
        self.x, self.y, self.z = sy.symbols('x y z')
        self.phi, self.theta, self.r, self.rho = sy.symbols('phi, theta, r, rho')
        self.i, self.j, self.k = sy.symbols('i j k')
        self.u, self.v, self.w = sy.symbols('u v w')
        self.usrvars = {}

        # initialize graph
        self.graphView = GraphView()

        # setup input table to contain equation entries
        self.inputTable = EquationTable(linkedGraph=self.graphView)

        # mini settings bar, including cog igon, colorpicker, etc..
        self.mainSettingsBar = MainToolbar()
        self.mainSettingsBar.addLayerButton.clicked.connect(self.addNewGraphItem)

        # add all objects to main layout
        mainLayout.addWidget(self.mainSettingsBar, 0, 0)
        mainLayout.addWidget(self.inputTable, 1, 0)
        mainLayout.addWidget(self.graphView, 1, 1)

        self.setLayout(mainLayout)

        # initialize default graph and its respective equation entry
        self.addNewGraphItem()

    def addNewGraphItem(self):
        name = self.newName()
        self.graphView.addPlotItem(name=name)
        self.inputTable.addInputItem(name=name)
        self.inputTable.inputs[name].updateGraphView()

    def newName(self):
        """
        Creates a unique hash to be used as an identifier that is passed between
        UI elements (i.e. user options, controls, etc.) that correspend to a common
        OpenGL plot item (surface plot, etc.).

        For instance, when a user selects a new cmap from the ColormapMenu this allows
        the cmap's button action to access the appropriate MeshItem data setter.
        """
        name = random.getrandbits(512)
        if name not in self.inputTable.inputs.keys():
            return name
        else:
            self.newName()
