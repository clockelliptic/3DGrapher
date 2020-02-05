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


from Components.MiniGradientButton.MiniGradientButton import MiniGradientButton
from Components.ColormapMenu.ColormapMenu import ColormapMenu
from Components.MiniButton.MiniButton import MiniButton

class InputSettingsBar(QToolBar):
    def __init__(self, name, linkedGraph, parent):
        super(InputSettingsBar, self).__init__(parent)
        root = QFileInfo(__file__).absolutePath()

        self.cmapButton = MiniGradientButton(gradient_name = linkedGraph.data[name].cmap_name)

        self.cmapMenuDisplay = ColormapMenu(name=name, linkedGraph = linkedGraph, parent_settings_bar=self)
        self.cmapButton.setMenu(QMenu(self.cmapButton))
        showColormapMenu = QWidgetAction(self.cmapButton)
        showColormapMenu.setDefaultWidget(self.cmapMenuDisplay)
        self.cmapButton.menu().addAction(showColormapMenu)

        self.settingsButton = MiniButton(root+'/../../styles/assets/icons/cog.png',
                                         parent = self)
        self.deleteButton = MiniButton(root+'/../../styles/assets/icons/close.png',
                                         parent = self)
        self.hideButton = MiniButton(root+'/../../styles/assets/icons/eye.png',
                                         parent = self)
        self.plotButton = MiniButton(root+'/../../styles/assets/icons/refresh.png',
                                         parent = self)

        self.addWidget(self.cmapButton)
        self.addWidget(self.settingsButton)
        self.addWidget(self.deleteButton)
        self.addWidget(self.hideButton)
        self.addWidget(self.plotButton)
        self.setMinimumWidth(33*5)