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

from Components.utils.GradientIconGenerator import GradientIconGenerator
from Components.GradientIconButton.GradientIconButton import GradientIconButton

class ColormapMenu(QFrame):
    """
    QFrame containing scroll area drop-down menu displaying colormap icons.

    Allows user to select a colormap for a given graph.
    """
    def __init__(self, name, linkedGraph, parent_settings_bar, parent=None):
        super(ColormapMenu, self).__init__(parent)

        # Make sure we have a PNG icon for each colormap then locate the icons
        GradientIconGenerator()
        root = QFileInfo(__file__).absolutePath()
        gradient_names = [filename.split('.')[0] for filename in os.listdir(root+"/../../styles/assets/icons/gradients/")]

        iconGridContainer = QWidget()
        iconGridContainer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        iconGrid=QGridLayout(iconGridContainer)

        # dict for holding all of the colormap icons, indexed by their respective names
        ilabels = {}

        for n, gradient_name in enumerate(gradient_names):

            ilabels[gradient_name] = GradientIconButton(name = name,
                                                        gradient_name = gradient_name,
                                                        linkedGraph = linkedGraph,
                                                        parent_settings_bar=parent_settings_bar)

            container=QFrame()
            layout = QVBoxLayout(container)
            layout.addWidget(ilabels[gradient_name], 0, Qt.AlignCenter)

            iconGrid.addWidget(container, n//6, n%6) # 6-column layout

        scrollarea = QScrollArea()
        scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollarea.setWidget(iconGridContainer)
        scrollarea.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea {border: none;}")

        mainLayout = QGridLayout()
        mainLayout.addWidget(scrollarea)
        self.setLayout(mainLayout)