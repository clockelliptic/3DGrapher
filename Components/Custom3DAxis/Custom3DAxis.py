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


from Components.CustomGLTextItem.CustomGLTextItem import CustomGLTextItem
class Custom3DAxis(gl.GLAxisItem):
    """Class defined to extend 'gl.GLAxisItem'."""
    def __init__(self, owner, color = (1.0,1.0,1.0,1.0)):
        super(Custom3DAxis, self).__init__()
        self.owner = owner
        self.c = color

    def add_labels(self):
        """Adds axes labels."""
        x,y,z = self.size()

        #X labels
        x0Label = CustomGLTextItem(X=0, Y=-y - y/5, Z=0, text="X")
        x0Label.setGLViewWidget(self.owner)
        self.owner.addItem(x0Label)

        x1Label = CustomGLTextItem(X=0, Y=y + y/5, Z=0, text="X")
        x1Label.setGLViewWidget(self.owner)
        self.owner.addItem(x1Label)

        #Y labels
        y0Label = CustomGLTextItem(X=-x - x/5, Y=0, Z=0, text="Y")
        y0Label.setGLViewWidget(self.owner)
        self.owner.addItem(y0Label)

        y1Label = CustomGLTextItem(X=x + x/5, Y=0, Z=0, text="Y")
        y1Label.setGLViewWidget(self.owner)
        self.owner.addItem(y1Label)

        #Z labels
        zLabel = CustomGLTextItem(X=-x - x/5, Y=y + y/5 - 1, Z=0, text="Z")
        zLabel.setGLViewWidget(self.owner)
        self.owner.addItem(zLabel)

        #Z labels
        zLabel = CustomGLTextItem(X=x + x/5, Y=-y - y/5, Z=0, text="Z")
        zLabel.setGLViewWidget(self.owner)
        self.owner.addItem(zLabel)

    def add_tick_values(self, xticks=[], yticks=[], zticks=[]):
        """Adds ticks values."""
        x,y,z = self.size()
        xpos = np.linspace(-x, x, 11)[1:-1]
        ypos = np.linspace(-y, y, 11)[1:-1]
        zpos = np.linspace(-z, z, 11)[1:-1]
        xticks = np.linspace(-self.owner.xrange, self.owner.xrange, 11)[1:-1]
        yticks = np.linspace(-self.owner.yrange, self.owner.yrange, 11)[1:-1]
        zticks = np.linspace(-z, z, 11)[1:-1]
        tickfontsize = 8
        #X labels
        for i, xt in enumerate(xticks):
            val = CustomGLTextItem(X=xpos[i], Y=-y - y/15, Z=0, text=str(xt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.owner)
            self.owner.addItem(val)
        for i, xt in enumerate(xticks):
            val = CustomGLTextItem(X=xpos[i], Y=y + y/15, Z=0, text=str(xt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.owner)
            self.owner.addItem(val)

        #Y labels
        for i, yt in enumerate(yticks):
            val = CustomGLTextItem(X=-x - x/15, Y=ypos[i], Z=0, text=str(yt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.owner)
            self.owner.addItem(val)
        for i, yt in enumerate(yticks):
            val = CustomGLTextItem(X=x + x/15, Y=ypos[i], Z=0, text=str(yt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.owner)
            self.owner.addItem(val)

        #Z labels
        for i, zt in enumerate(zticks):
            val = CustomGLTextItem(X=-x - x/10, Y=y + y/10, Z=zpos[i], text=str(zt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.owner)
            self.owner.addItem(val)
        for i, zt in enumerate(zticks):
            val = CustomGLTextItem(X=x + x/10, Y=-y - y/10, Z=zpos[i], text=str(zt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.owner)
            self.owner.addItem(val)

    def paint(self):
        self.setupGLState()
        if self.antialias:
            ogl.glEnable(ogl.GL_LINE_SMOOTH)
            ogl.glHint(ogl.GL_LINE_SMOOTH_HINT, ogl.GL_NICEST)
        ogl.glBegin(ogl.GL_LINES)

        x,y,z = self.size()

        # vertices
        v = [(-x, -y,  0),(x, -y, 0),(x, y, 0),(-x, y, 0),
             (-x, -y,  z),(x, -y, z),(x, y, z),(-x, y, z),
             (-x, -y, -z),(x, -y,-z),(x, y,-z),(-x, y,-z)]

        # HORIZONTAL AXIS AT Z = 0
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[0][0],v[0][1],v[0][2])
        ogl.glVertex3f(v[1][0],v[1][1],v[1][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[1][0],v[1][1],v[1][2])
        ogl.glVertex3f(v[2][0],v[2][1],v[2][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[2][0],v[2][1],v[2][2])
        ogl.glVertex3f(v[3][0],v[3][1],v[3][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[3][0],v[3][1],v[3][2])
        ogl.glVertex3f(v[0][0],v[0][1],v[0][2])

        # HORIZONTAL AXIS AT Z = z
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[4][0],v[4][1],v[4][2])
        ogl.glVertex3f(v[5][0],v[5][1],v[5][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[5][0],v[5][1],v[5][2])
        ogl.glVertex3f(v[6][0],v[6][1],v[6][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[6][0],v[6][1],v[6][2])
        ogl.glVertex3f(v[7][0],v[7][1],v[7][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[7][0],v[7][1],v[7][2])
        ogl.glVertex3f(v[4][0],v[4][1],v[4][2])

        # HORIZONTAL AXIS AT Z = -z
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[8][0],v[8][1],v[8][2])
        ogl.glVertex3f(v[9][0],v[9][1],v[9][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[9][0],v[9][1],v[9][2])
        ogl.glVertex3f(v[10][0],v[10][1],v[10][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[10][0],v[10][1],v[10][2])
        ogl.glVertex3f(v[11][0],v[11][1],v[11][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[11][0],v[11][1],v[11][2])
        ogl.glVertex3f(v[8][0],v[8][1],v[8][2])

        # UPPER Z-AXES
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[0][0],v[0][1],v[0][2])
        ogl.glVertex3f(v[4][0],v[4][1],v[4][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[1][0],v[1][1],v[1][2])
        ogl.glVertex3f(v[5][0],v[5][1],v[5][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[2][0],v[2][1],v[2][2])
        ogl.glVertex3f(v[6][0],v[6][1],v[6][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[3][0],v[3][1],v[3][2])
        ogl.glVertex3f(v[7][0],v[7][1],v[7][2])

        # LOWER Z-AXES
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[0][0],v[0][1],v[0][2])
        ogl.glVertex3f(v[8][0],v[8][1],v[8][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[1][0],v[1][1],v[1][2])
        ogl.glVertex3f(v[9][0],v[9][1],v[9][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[2][0],v[2][1],v[2][2])
        ogl.glVertex3f(v[10][0],v[10][1],v[10][2])
        ogl.glColor4f(self.c[0], self.c[1], self.c[2], self.c[3])
        ogl.glVertex3f(v[3][0],v[3][1],v[3][2])
        ogl.glVertex3f(v[11][0],v[11][1],v[11][2])

        ogl.glEnd()
