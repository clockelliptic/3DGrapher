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


class LatexDisplay(QWebEngineView):
    pageSource = """
                    <html style="max-height:60px; overflow:hidden;">
                    <head>
                        <meta charset="UTF-8">
                        <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
                        MathJax.Hub.Config({
                            extensions: ["tex2jax.js"],
                            jax: ["input/TeX","output/HTML-CSS"],
                            tex2jax: {inlineMath: [["$","$"],["\\(","\\)"]]}
                        });
                        </script>

                        <style>
                        .center {
                            margin: 0;
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            -ms-transform: translate(-50%, -50%);
                            transform: translate(-50%, -50%);
                        }

                        </style>
                    </head>
                    <body style="background-color: #31363b;">

                        <script>
                            function updateMathJax(TeX) {
                                /// set up new mathjax div content
                                document.getElementById("MathOutput").innerHTML = TeX;
                                /// update new mathjax div content
                                MathJax.Hub.Queue(["Typeset",MathJax.Hub,"MathOutput"]);
                            }
                        </script>

                        <div class="center">
                            <mathjax id="MathOutput" style="font-size:1.5em; color:#FFF">${}$</mathjax>
                        </div>

                    </body>
                    </html>
                    """
    def __init__(self, parent=None):
        super(LatexDisplay, self).__init__(parent)
        self.page().setBackgroundColor(QColor('#31363b'))
        self.setMaximumHeight(80)
        self.setMinimumHeight(60)
        self.setHtml(self.pageSource)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
