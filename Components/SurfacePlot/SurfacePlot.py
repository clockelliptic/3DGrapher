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

class SurfacePlot(gl.GLSurfacePlotItem):
    def __init__(self, resolution, owner, parent=None):
        super(SurfacePlot, self).__init__(smooth=True, shader='shaded',
                                          drawEdges=True, drawFaces=True,
                                          edgeColor=(0.3, 0.3, 0.3, 0.1))
        self.owner = owner
        self.resolution = resolution

        # variable for storing current equation
        self.equation = None

        # set default colormap
        self.setColormap("inferno")

        # generate default graph data
        self.xs, self.ys = np.mgrid[-self.owner.xrange:self.owner.xrange:int(2*self.resolution + 1)*1j,
                                    -self.owner.yrange:self.owner.yrange:int(2*self.resolution + 1)*1j]
        self.updatePlot()

        # align the plotted data to the center of the graph
        self.translate(-self.resolution,-self.resolution,0)

        # graph aesthetics
        self.setData(z = np.zeros(shape=self.xs.shape))
        self.applyColormap()

        self.setShader('shaded')
        self.setGLOptions('additive')

    def setColormap(self, cmap_name):
        self.cmap_name=(cmap_name)
        self.cmap = cm.get_cmap(cmap_name)
        try:
            self.applyColormap()
        except:
            pass

    def applyColormap(self):
        if not (self.zs.max() - self.zs.min()) == 0:
            self.colors = self.cmap((self.zs - self.zs.min())/(self.zs.max() - self.zs.min()))
        else:
            self.colors = self.cmap(self.zs)

    def updateResolution(self, new_resolution):
        self.resolution = new_resolution
        self.xs, self.ys = np.mgrid[-self.owner.xrange:self.owner.xrange:int(20*self.resolution + 1)*1j,
                                    -self.owner.yrange:self.owner.yrange:int(20*self.resolution + 1)*1j]
        self.updatePlot()

    def updatePlot(self):
        if self.equation == None:
            self.zs = np.zeros(self.xs.shape)
            self.setData(z = self.zs)
        else:
            self.zs = self.equation(self.xs, self.ys)
            if np.isscalar(self.zs):
                self.zs = np.full(self.xs.shape, self.zs)
                self.setData(z = self.zs)
            else:
                self.zs = self.validateData(self.zs)
                self.setData(z = self.zs)
        self.applyColormap()

    def validateData(self, zs):
        '''Checks for invalid values (np.nan or np.inf) and
           replaces them with interpolated numeric values.
        '''
        #TODO: Fix for sparse marices / large undefined areas
        if (not np.isnan(zs.flatten()).any(0)) and (not np.isinf(zs.flatten()).any(0)):
            return zs
        else:
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
