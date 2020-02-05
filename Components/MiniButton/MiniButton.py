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



#  custom mini QBUttons for InputSettingsBar
class MiniButton(QPushButton):
    def __init__(self, iconpath, parent, is_gradient_icon=False):
        super(MiniButton, self).__init__(parent)
        self.setStyleSheet('''
                                MiniButton
                                {
                                    background-color: transparent;
                                    border: 0ex;
                                    margin: 0ex;
                                    padding: 0ex;
                                    icon-size:42px 42px;
                                }

                                MiniButton:hover
                                {
                                    background-color: rgba(0,0,0,0.1);
                                }

                                MiniButton:pressed
                                {
                                    background-color: rgba(0,0,0,0.2);
                                }

                                MiniButton::menu-indicator
                                {
                                    image: none;;
                                }
                                ''')

        if not is_gradient_icon:
            self.setIcon(QIcon(iconpath))
            self.setFixedSize(32, 32)
            root = QFileInfo(__file__).absolutePath()

        else:
            self.setIcon(QIcon(iconpath))
            self.setFixedSize(32, 32)
            root = QFileInfo(__file__).absolutePath()
