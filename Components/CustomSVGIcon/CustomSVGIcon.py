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

class CustomSVGIcon():
    def __init__(self, icon_name, hex_color):
        root = QFileInfo(__file__).absolutePath()

        svg_files = os.listdir(root+"/styles/assets/icons/svg/")

        filename = "appbar."+icon_name+".svg"
        if filename in svg_files:
            f = QFile(root+'/styles/assets/icons/svg/'+filename)
            if f.open(QFile.ReadOnly | QFile.Text):
                textStream = QTextStream(f)
                svgData = textStream.readAll().replace('fill="#000000"', 'fill="{}"'.format(hex_color))
                f.close()

            svg = QSvgRenderer(QByteArray().append(svgData))

            qim = QImage(76, 76, QImage.Format_RGBA8888)
            qim.fill(0)
            painter = QPainter()
            painter.begin(qim)
            svg.render(painter)
            painter.end()

            self.icon = (QIcon(QPixmap.fromImage( qim )))

    def do(self):
        return self.icon
