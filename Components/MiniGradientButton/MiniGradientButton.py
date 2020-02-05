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



class MiniGradientButton(QPushButton):
    def __init__(self, gradient_name, parent=None):
        super(MiniGradientButton, self).__init__(parent)

        self.setFixedSize(28, 28)
        self.setStyleSheet("""
                            MiniGradientButton {
                                border: 0.1ex solid #76797c;
                                border-radius: 12.75px;
                                background-color: #76797c;
                                margin: 0ex;
                                padding: 0ex;
                                icon-size: 22px 22px;
                            }

                            MiniGradientButton:hover {
                                border: 0.1ex solid #eeeeee;
                                background-color: #eeeeee;
                            }

                            MiniGradientButton:pressed {
                                border: 0.1ex solid #3daee9;
                                background-color: #3daee9;
                            }

                            MiniGradientButton::menu-indicator { image: none; }
                           """)

        imgdata = open("styles/assets/icons/gradients/"+gradient_name+'.png', 'rb').read()
        pixmap = self.mask_image(imgdata)
        self.setCustomIcon(gradient_name, QIcon(pixmap))
        del imgdata; del pixmap

    def setCustomIcon(self, gradient_name, qicon):
        self.setIcon(qicon)
        self.setToolTip(gradient_name)

    def mask_image(self, imgdata, imgtype='png', size=35):
        """
        Return a ``QPixmap`` from *imgdata* masked with a smooth circle.

        *imgdata* are the raw image bytes, *imgtype* denotes the image type.

        The returned image will have a size of *size* × *size* pixels.
        """
        # Load image and convert to 32-bit ARGB (adds an alpha channel):
        image = QImage.fromData(imgdata, imgtype)
        image.convertToFormat(QImage.Format_ARGB32)

        # Crop image to a square:
        imgsize = min(image.width(), image.height())
        rect = QRect(
            (image.width() - imgsize) / 2,
            (image.height() - imgsize) / 2,
            imgsize,
            imgsize,
        )
        image = image.copy(rect)

        # Create the output image with the same dimensions and an alpha channel
        # and make it completely transparent:
        out_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
        out_img.fill(Qt.transparent)

        # Create a texture brush and paint a circle with the original image onto
        # the output image:
        brush = QBrush(image)        # Create texture brush
        painter = QPainter(out_img)  # Paint the output image
        painter.setBrush(brush)      # Use the image texture brush
        painter.setPen(Qt.NoPen)     # Don't draw an outline
        painter.setRenderHint(QPainter.Antialiasing, True)  # Use AA
        painter.drawEllipse(0, 0, imgsize, imgsize)  # Actually draw the circle
        painter.end()                # We are done (segfault if you forget this)

        # Convert the image to a pixmap and rescale it.  Take pixel ratio into
        # account to get a sharp image on retina displays:
        pr = QWindow().devicePixelRatio()
        pm = QPixmap.fromImage(out_img)
        pm.setDevicePixelRatio(pr)
        size *= pr
        pm = pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        return pm