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


from Components.EquationInput.EquationInput import EquationInput
from Components.EquationTableItem.EquationTableItem import EquationTableItem
from Components.EquationTableSpacer.EquationTableSpacer import EquationTableSpacer



class EquationTable(QFrame):
    def __init__(self, linkedGraph, parent=None):
        super(EquationTable, self).__init__()

        self.linkedGraph = linkedGraph
        self.inputs = {}
        self.tableIndex = 0 # keep track of how many input boxes there are

        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding))
        self.setMaximumWidth(500)
        self.setMinimumWidth(250)

        self.spacer = EquationTableSpacer()

        self.layout = QGridLayout()
        self.layout.addWidget(self.spacer, 9999, 0)

        self.setStyleSheet("""
                            EquationTable {
                                border-right: 0.2ex dashed rgba(200,225,255,0.2);
                            }
                            """)
        self.layout.setContentsMargins(0,11,11,11)

        self.setLayout(self.layout)

    def addInputItem(self, name):
        self.inputs[name] = EquationTableItem(name, self.linkedGraph, parent=self)

        self.layout.addWidget(self.inputs[name], self.tableIndex, 0)
        self.tableIndex+=1

    def removeInputItem(self, name):
        self.layout.removeWidget(self.inputs[name])
        delete(self.inputs[name])
        self.tableIndex-=1

