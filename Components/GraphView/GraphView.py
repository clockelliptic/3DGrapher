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


from Components.Custom3DAxis.Custom3DAxis import Custom3DAxis
from Components.SurfacePlot.SurfacePlot import SurfacePlot

class GraphView(gl.GLViewWidget):
    def __init__(self, parent=None):
        super(GraphView, self).__init__(parent)

        # default resolution and graph bounds
        self.resolution = 20
        self.xrange = 5 # +/- x-range
        self.yrange = 5 # +/- y-range

        # dictionary for storing all graph objects
        self.data = {}

        # style and size of the GLViewWidget
        self.sizeHint = lambda: QSize(100, 450)
        self.setMinimumWidth(500)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setBackgroundColor('#31363b')

        # Setup the axis and add it to the figure
        axis = Custom3DAxis(owner=self, color=(1.,1.,1.,.25))
        axis.setSize(x=self.resolution, y=self.resolution, z=self.resolution)

        axis.add_labels()
        axis.add_tick_values()
        self.addItem(axis)

        self.setCameraPosition(distance=80)#, elevation=42, azimuth=42)

    def addPlotItem(self, name):
        # generate a colormap for the surface
        self.data[name] = SurfacePlot(resolution=self.resolution, owner=self)

        # show the GLSurfacePlotItem in the GLViewWidget
        self.addItem(self.data[name])
