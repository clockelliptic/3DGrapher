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

class BigButton(QPushButton):
    mouseHover = pyqtSignal(bool)
    def __init__(self, icon_name, parent, onClicked = (lambda: None), base_color="#eeeeee", hover_color="#3daee9"):
        '''
        Respectively, base_color and hover_color represent the color of the button's icon when inactive
        and the color of the icon when user hovers over the button.

        These fields must be strings containing hex color codes.
        '''
        super(BigButton, self).__init__(parent)
        self.clicked.connect(onClicked)
        self.getIcon(icon_name, base_color, hover_color)
        self.setFixedSize(48, 48)
        self.setStyleSheet('''
                            QPushButton
                            {
                                background-color: none;
                                margin: 0ex;
                                padding: 0ex;
                                icon-size:48px 48px;
                            }
                            QPushButton:pressed
                            {
                                background-color: #3daee9;
                                margin: 0ex;
                                padding: 0ex;
                                icon-size:48px 48px;
                            }''')

    def getIcon(self, icon_name, base_color, hover_color):
        root = QFileInfo(__file__).absolutePath()

        svg_files = os.listdir(root+"/../../styles/assets/icons/svg/")
        filename = "appbar."+icon_name+".svg"
        if filename in svg_files:
            f = QFile(root+'/../../styles/assets/icons/svg/'+filename)
            if f.open(QFile.ReadOnly | QFile.Text):
                textStream = QTextStream(f)
                svgData = textStream.readAll().replace('fill="#000000"', 'fill="{}"'.format(base_color))
                svgData_hover = svgData.replace('fill="{}"'.format(base_color), 'fill="{}"'.format(hover_color))
                f.close()

            svg = QSvgRenderer(QByteArray().append(svgData))
            svg_hover = QSvgRenderer(QByteArray().append(svgData_hover))

            qim = QImage(76, 76, QImage.Format_RGBA8888)
            qim.fill(0)
            painter = QPainter()
            painter.begin(qim)
            svg.render(painter)
            painter.end()

            qim_hover = QImage(76, 76, QImage.Format_ARGB32)
            qim_hover.fill(0)
            painter = QPainter()
            painter.begin(qim_hover)
            svg_hover.render(painter)
            painter.end()

            self.icon = QIcon(QPixmap.fromImage( qim ))
            self.hovericon = QIcon(QPixmap.fromImage( qim_hover ))

            self.setIcon(self.icon)

        else:
            qim = QImage(76, 76, QImage.Format_RGBA8888)
            qim.fill(0)

            self.icon = QPixmap.fromImage( qim )
            self.hovericon = QPixmap.fromImage( qim )

            self.setIcon(self.icon)

    def enterEvent(self, event):
        self.mouseHover.emit(True)
        self.setIcon(self.hovericon)

    def leaveEvent(self, event):
        self.mouseHover.emit(False)
        self.setIcon(self.icon)
