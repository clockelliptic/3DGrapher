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

# stylesheet
import breeze_resources


from Components.App.App import App
from Components.BigButton.BigButton import BigButton
from Components.ColormapMenu.ColormapMenu import ColormapMenu
from Components.Custom3DAxis.Custom3DAxis import Custom3DAxis
from Components.CustomGLTextItem.CustomGLTextItem import CustomGLTextItem
from Components.CustomSVGIcon.CustomSVGIcon import CustomSVGIcon
from Components.EquationInput.EquationInput import EquationInput
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




if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    # set stylesheet
    file = QFile("./styles/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    calc = App()
    calc.show()
    sys.exit(app.exec_())

    del calc