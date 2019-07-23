#######################################################################################
#
# Separate business logic from UI objects. Increase testability and portability.
#
# Store objects as JSON wherever possible when sharing them amongst languages.
#
#######################################################################################

import os
import time
import traceback
import random
import scipy.interpolate
from scipy.interpolate import griddata

from cytoolz import curry

import numpy as np
from sympy import *

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

#ANCHOR: fadeInAnimator
def fadeInAnimator(obj):
    opacity_effect = QGraphicsOpacityEffect(obj)
    opacity_effect.setOpacity(0)
    obj.setGraphicsEffect(opacity_effect)

    obj.fadeIn = QPropertyAnimation(opacity_effect, b"opacity")
    obj.fadeIn.setDuration(350)
    obj.fadeIn.setStartValue(0)
    obj.fadeIn.setEndValue(1)
    obj.fadeIn.setEasingCurve(QEasingCurve.InCubic)
    obj.fadeIn.start(QPropertyAnimation.DeleteWhenStopped)

#ANCHOR: CustomSVGIcon
# Parse SVG icon file and set a custom fill color
class CustomSVGIcon():
    def __init__(self, icon_name, hex_color):
        root = QFileInfo(__file__).absolutePath()

        svg_files = os.listdir(root+"/icons/svg/")

        filename = "appbar."+icon_name+".svg"
        if filename in svg_files:
            f = QFile(root+'/icons/svg/'+filename)
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

#ANCHOR: GradientIconGenerator
# Checks to make sure there is a PNG icon for each colormap; generates any that are missing
class GradientIconGenerator():
    """
    Uses matplotlib to generate small PNG icons representing each colormap that is available to users.

    Filters out the ugly matplotlib colormaps.
    """
    def __init__(self, parent=None):
        img_size = 35 # square dimension of output image
        data = np.mgrid[0:255:255j, 0:255][0]

        ugly_maps = ['Accent', 'Paired', 'Dark', 'Pastel', 'tab', 'Set', 'flag', '_r', 'gray', 'Greys']
        pretty_cmaps = [i for i in mpl_cmaps() if not any([(j in i) for j in ugly_maps])]

        root = QFileInfo(__file__).absolutePath()
        gradient_icons = [i.split('.')[0] for i in os.listdir(root+"/icons/gradients/")]

        for cmap_name in pretty_cmaps:
            if cmap_name not in gradient_icons:
                cmap = cm.get_cmap(cmap_name)
                sizes = np.shape(data)
                fig = plt_figure(figsize=(1,1))
                #fig.set_size_inches(1. * sizes[0] / sizes[1], 1, forward=False)
                ax = plt_Axes(fig, [0.,0.,1.,1.])
                ax.set_axis_off()
                fig.add_axes(ax)
                ax.imshow(data[::-1], cmap)
                plt_savefig("icons/gradients/{}.png".format(cmap_name), dpi=img_size)
                plt_close()

#ANCHOR: GradientIconButton
class GradientIconButton(QToolButton):
    def __init__(self, name, gradient_name, linkedGraph, parent_settings_bar, parent=None):
        super(GradientIconButton, self).__init__(parent)
        self.name = name
        self.gradient_name = gradient_name
        self.linkedGraph = linkedGraph

        imgdata = open("icons/gradients/"+gradient_name+'.png', 'rb').read()
        pixmap = self.mask_image(imgdata)

        self.setStyleSheet("""
                            GradientIconButton {
                                border: 0.5ex solid #76797c;
                                border-radius: 21.45px;
                                background-color: #76797c;
                                margin: 0ex;
                                padding: 0ex;
                                width: 35px;
                                height: 35px;
                                icon-size: 35px 35px;
                            }

                            GradientIconButton:hover {
                                border: 0.5ex solid #eeeeee;
                                background-color: #eeeeee;
                            }

                            GradientIconButton:pressed {
                                border: 0.5ex solid #3daee9;
                                background-color: #3daee9;
                            }
                           """)

        self.setIcon(QIcon(pixmap))
        self.setToolTip(gradient_name)

        self.clicked.connect(self.setColormap)
        self.clicked.connect(lambda: self.changeIndicatorIcon(parent_settings_bar, gradient_name, QIcon(pixmap)))

    def mask_image(self, imgdata, imgtype='png', size=35):
        """Return a ``QPixmap`` from *imgdata* masked with a smooth circle.

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

    def setColormap(self):
        """
        Button action. Applies colormap to respective surface plot.
        """
        self.linkedGraph.data[self.name].setColormap(cmap_name=self.gradient_name)
        self.linkedGraph.setFocus()

    def changeIndicatorIcon(self, parent_settings_bar, gradient_name, qicon):
        parent_settings_bar.colormapButton.setCustomIcon(gradient_name, qicon)

#ANCHOR: MiniGradientButton
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

        imgdata = open("icons/gradients/"+gradient_name+'.png', 'rb').read()
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


#ANCHOR: ColormapMenu
# Drop-down menu that displays all of the Gradient icons
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
        gradient_names = [filename.split('.')[0] for filename in os.listdir(root+"/icons/gradients/")]

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


#ANCHOR: Button
class Button(QToolButton):
    def __init__(self, text, parent=None):
        super(Button, self).__init__(parent)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.setText(text)


#ANCHOR: CustomGLTextItem
# OpenGL text items for axis labels and 3D text
class CustomGLTextItem(gl.GLGraphicsItem.GLGraphicsItem):
    def __init__(self, X, Y, Z, text, font = QFont('Arial', pointSize=12, weight=150)):
        gl.GLGraphicsItem.GLGraphicsItem.__init__(self)
        self.text = text
        self.X = X
        self.Y = Y
        self.Z = Z
        self.font = font

    def setGLViewWidget(self, GLViewWidget):
        self.GLViewWidget = GLViewWidget

    def setText(self, text):
        self.text = text
        self.update()

    def setX(self, X):
        self.X = X
        self.update()

    def setY(self, Y):
        self.Y = Y
        self.update()

    def setZ(self, Z):
        self.Z = Z
        self.update()

    def paint(self):
        self.GLViewWidget.qglColor(QColor(qRgba(255,255,255,0)))#QtCore.Qt.white)
        self.GLViewWidget.renderText(self.X, self.Y, self.Z, self.text, font=self.font)

#ANCHOR: Custom3DAxis
class Custom3DAxis(gl.GLAxisItem):
    """Class defined to extend 'gl.GLAxisItem'."""
    def __init__(self, parent, color = (1.0,1.0,1.0,1.0)):
        gl.GLAxisItem.__init__(self)
        self.parent = parent
        self.c = color

    def add_labels(self):
        """Adds axes labels."""
        x,y,z = self.size()

        #X labels
        self.x0Label = CustomGLTextItem(X=0, Y=-y - y/5, Z=0, text="X")
        self.x0Label.setGLViewWidget(self.parent)
        self.parent.addItem(self.x0Label)

        self.x1Label = CustomGLTextItem(X=0, Y=y + y/5, Z=0, text="X")
        self.x1Label.setGLViewWidget(self.parent)
        self.parent.addItem(self.x1Label)

        #Y labels
        self.y0Label = CustomGLTextItem(X=-x - x/5, Y=0, Z=0, text="Y")
        self.y0Label.setGLViewWidget(self.parent)
        self.parent.addItem(self.y0Label)

        self.y1Label = CustomGLTextItem(X=x + x/5, Y=0, Z=0, text="Y")
        self.y1Label.setGLViewWidget(self.parent)
        self.parent.addItem(self.y1Label)

        #Z labels
        self.zLabel = CustomGLTextItem(X=-x - x/5, Y=y + y/5 - 1, Z=0, text="Z")
        self.zLabel.setGLViewWidget(self.parent)
        self.parent.addItem(self.zLabel)

        #Z labels
        self.zLabel = CustomGLTextItem(X=x + x/5, Y=-y - y/5, Z=0, text="Z")
        self.zLabel.setGLViewWidget(self.parent)
        self.parent.addItem(self.zLabel)

    def add_tick_values(self, xticks=[], yticks=[], zticks=[]):
        """Adds ticks values."""
        x,y,z = self.size()
        xpos = np.linspace(-x, x, 11)[1:-1]
        ypos = np.linspace(-y, y, 11)[1:-1]
        zpos = np.linspace(-z, z, 11)[1:-1]
        xticks = np.linspace(-self.parent.xrange, self.parent.xrange, 11)[1:-1]
        yticks = np.linspace(-self.parent.yrange, self.parent.yrange, 11)[1:-1]
        zticks = np.linspace(-z, z, 11)[1:-1]
        tickfontsize = 8
        #X labels
        for i, xt in enumerate(xticks):
            val = CustomGLTextItem(X=xpos[i], Y=-y - y/15, Z=0, text=str(xt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)
        for i, xt in enumerate(xticks):
            val = CustomGLTextItem(X=xpos[i], Y=y + y/15, Z=0, text=str(xt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)

        #Y labels
        for i, yt in enumerate(yticks):
            val = CustomGLTextItem(X=-x - x/15, Y=ypos[i], Z=0, text=str(yt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)
        for i, yt in enumerate(yticks):
            val = CustomGLTextItem(X=x + x/15, Y=ypos[i], Z=0, text=str(yt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)

        #Z labels
        for i, zt in enumerate(zticks):
            val = CustomGLTextItem(X=-x - x/10, Y=y + y/10, Z=zpos[i], text=str(zt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)
        for i, zt in enumerate(zticks):
            val = CustomGLTextItem(X=x + x/10, Y=-y - y/10, Z=zpos[i], text=str(zt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)

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

#ANCHOR: GraphView
class GraphView(gl.GLViewWidget):
    def __init__(self, parent=None):
        super(GraphView, self).__init__(parent)

        # default resolution and graph bounds
        self.resolution = 20
        self.xrange = 5 # +/- x-range
        self.yrange = 5 # +/- y-range

        # dictionary for storing all graph objects
        self.data = {}

        # style and size of the GLViewWidget
        self.sizeHint = lambda: QSize(100, 450)
        self.setMinimumWidth(500)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setBackgroundColor('#31363b')

        # Setup the axis and add it to the figure
        axis = Custom3DAxis(self, color=(1.,1.,1.,.25))
        axis.setSize(x=self.resolution, y=self.resolution, z=self.resolution)

        axis.add_labels()
        axis.add_tick_values()
        self.addItem(axis)

        self.setCameraPosition(distance=80)#, elevation=42, azimuth=42)

    def addPlotItem(self, name):
        # generate a colormap for the surface
        self.data[name] = SurfacePlot(resolution=self.resolution, parent=self)

        # show the GLSurfacePlotItem in the GLViewWidget
        self.addItem(self.data[name])

#ANCHOR: SurfacePlot
class SurfacePlot(gl.GLSurfacePlotItem):
    def __init__(self, resolution, parent=None):
        super(SurfacePlot, self).__init__(smooth=True, shader='shaded',
                                          drawEdges=True, drawFaces=True,
                                          edgeColor=(0.3, 0.3, 0.3, 0.1))
        self.parent = parent
        self.resolution = resolution

        # variable for storing current equation
        self.equation = None

        # set default colormap
        self.setColormap("inferno")

        # generate default graph data
        self.xs, self.ys = np.mgrid[-self.parent.xrange:self.parent.xrange:int(2*self.resolution + 1)*1j,
                                    -self.parent.yrange:self.parent.yrange:int(2*self.resolution + 1)*1j]
        self.updatePlot()

        # align the plotted data to the center of the graph
        self.translate(-self.resolution,-self.resolution,0)

        # graph aesthetics
        self.setData(z = np.zeros(shape=self.xs.shape))

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
        self.colors = self.cmap((self.zs - self.zs.min())/(self.zs.max() - self.zs.min()))

    def updateResolution(self, new_resolution):
        self.resolution = new_resolution
        self.xs, self.ys = np.mgrid[-self.parent.xrange:self.parent.xrange:int(20*self.resolution + 1)*1j,
                                    -self.parent.yrange:self.parent.yrange:int(20*self.resolution + 1)*1j]
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
        if (not np.isnan(zs.flatten()).any(0)) and (not np.isinf(zs.flatten()).any(0)):
            return zs
        else: # interpolate missing values
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

#ANCHOR: EquationTable
#  custom QWidget for organizes user's graphs
class EquationTable(QFrame):
    def __init__(self, linkedGraph, parent=None):
        super(EquationTable, self).__init__()

        self.linkedGraph = linkedGraph
        self.inputs = {}
        self.tableIndex = 0 # keep track of how many input boxes there are

        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding))
        self.setMaximumWidth(500)
        self.setMinimumWidth(250)

        self.spacer = EquationTableSpacer()

        self.layout = QGridLayout()
        self.layout.addWidget(self.spacer, 9999, 0)

        self.setStyleSheet("""
                            EquationTable {
                                border-right: 0.2ex dashed rgba(200,225,255,0.2);
                            }
                            """)
        self.layout.setContentsMargins(0,11,11,11)

        self.setLayout(self.layout)

    def addInputItem(self, name):
        self.inputs[name] = EquationTableItem(name, self.linkedGraph, parent=self)

        self.layout.addWidget(self.inputs[name], self.tableIndex, 0)
        self.tableIndex+=1

    def removeInputItem(self, name):
        self.layout.removeWidget(self.inputs[name])
        delete(self.inputs[name])
        self.tableIndex-=1


#ANCHOR: EquationInputBox
# text input field, user-defined equation
class EquationInputBox(QLineEdit):
    def __init__(self, parent=None):
        super(EquationInputBox, self).__init__(parent)
        self.setReadOnly(False)

        font = self.font()
        font.setPointSize(font.pointSize() + 6)
        self.setFont(font)

        self.setAlignment(Qt.AlignLeft)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.setMaximumHeight(50)

#ANCHOR: InputSettingsBar
#  mini settings bar, accompanies each individual graph
class InputSettingsBar(QToolBar):
    def __init__(self, name, linkedGraph, parent):
        super(InputSettingsBar, self).__init__(parent)
        root = QFileInfo(__file__).absolutePath()

        self.colormapButton = MiniGradientButton(gradient_name = linkedGraph.data[name].cmap_name)

        colormapMenuDisplay = ColormapMenu(name=name, linkedGraph = linkedGraph, parent_settings_bar=self)
        self.colormapButton.setMenu(QMenu(self.colormapButton))
        showColormapMenu = QWidgetAction(self.colormapButton)
        showColormapMenu.setDefaultWidget(colormapMenuDisplay)
        self.colormapButton.menu().addAction(showColormapMenu)

        self.settingsButton = MiniButton(root+'/icons/cog.png',
                                         parent = self,
                                         onClicked = self.handleButton)
        self.deleteButton = MiniButton(root+'/icons/close.png',
                                         parent = self,
                                         onClicked = self.handleButton)
        self.hideButton = MiniButton(root+'/icons/eye.png',
                                         parent = self,
                                         onClicked = self.handleButton)
        self.plotButton = MiniButton(root+'/icons/refresh.png',
                                         parent = self,
                                         onClicked = self.handleButton)

        self.addWidget(self.colormapButton)
        self.addWidget(self.settingsButton)
        self.addWidget(self.deleteButton)
        self.addWidget(self.hideButton)
        self.addWidget(self.plotButton)
        self.setMinimumWidth(33*5)

    def handleButton(self):
        pass

#ANCHOR: MiniButton
#  custom mini QBUttons for InputSettingsBar
class MiniButton(QPushButton):
    def __init__(self, iconpath, parent, onClicked, is_gradient_icon=False):
        super(MiniButton, self).__init__(parent)
        self.clicked.connect(onClicked)

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


#ANCHOR: EquationTableSpacer
# Blank space beneath EquationTableItems
class EquationTableSpacer(QWidget):
    def __init__(self, parent=None):
        super(EquationTableSpacer, self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

#ANCHOR: EquationTableItem
#  container for user text input, mini settings bar, etc.
class EquationTableItem(QFrame):
    def __init__(self, name, linkedGraph, parent=None):
        super(EquationTableItem, self).__init__(parent)

        self.name = name
        self.linkedGraph = linkedGraph

        # initialize local math symbols
        self.x, self.y, self.z = symbols('x y z')
        self.phi, self.theta, self.r, self.rho = symbols('phi, theta, r, rho')
        self.i, self.j, self.k = symbols('i j k')
        self.u, self.v, self.w = symbols('u v w')

        # math expression input box
        self.display = EquationInputBox("")
        self.display.textChanged.connect(self.showLatex)

        # option to simplify the math expression in LaTeX output
        self.simplifyExpression = QCheckBox("Simplify", self)
        self.simplifyExpression.stateChanged.connect(self.simplifyChecked)
        self.simplifyExpressionChecked = False
        self.simplifyExpression.setMaximumHeight(15)

        # mini settings bar, including cog igon, colorpicker, etc..
        self.settingsBar = InputSettingsBar(name = self.name, linkedGraph = self.linkedGraph, parent = self)
        self.settingsBar.plotButton.clicked.connect(self.updateGraphView)
        self.settingsBar.hideButton.clicked.connect(self.hideGraphItem)
        self.settingsBar.deleteButton.clicked.connect(self.deleteGraphItem)
        self.hidden = False

        # latex view
        self.mathJaxWebView = LatexView()
        self.mathJaxWebView.loadFinished.connect(self.showLatex)

        # setup input table layout and sizing
        self.setMaximumHeight(150)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.layout = QGridLayout()

        self.layout.addWidget(self.display, 0, 0, 2, 1)
        self.layout.addWidget(self.settingsBar, 0, 1)
        self.layout.addWidget(self.simplifyExpression, 1, 1)
        self.layout.addWidget(self.mathJaxWebView, 2, 0, 3, 1)

        self.setStyleSheet("""
                            EquationTableItem {
                                border-bottom: 0.2ex dashed rgba(200,225,255,0.2);
                            }
                            """)
        self.layout.setContentsMargins(0,11,11,11)

        fadeInAnimator(self)

        self.setLayout(self.layout)
        self.display.setFocus() # bring text input box into keyboard focus

    def deleteGraphItem(self):
        self.linkedGraph.removeItem(self.linkedGraph.data[self.name])
        del self.linkedGraph.data[self.name]
        self.parent().removeInputItem(self.name)


    def hideGraphItem(self):
        if self.hidden==False:
            self.linkedGraph.removeItem(self.linkedGraph.data[self.name])
            self.hidden = True
        else:
            self.linkedGraph.addItem(self.linkedGraph.data[self.name])
            self.hidden = False

    def createButton(self, text, member):
        button = Button(text)
        button.clicked.connect(member)
        return button

    def simplifyChecked(self, state):
        '''If 'Simplify' checkbox is checked, this simplifies the
           equation before returning MathJax-rendered equation
        '''
        if state == Qt.Checked:
            self.simplifyExpressionChecked = True
        else:
            self.simplifyExpressionChecked = False
        self.showLatex()

    def validateInput(self):
        '''Checks user's equation to see if it is valid and gives visual feedback.
        '''
        try:
            lambdify((self.x, self.y), sympify(self.display.text()))(1,1)
            self.display.setStyleSheet('''QLineEdit:hover {border: 0.2ex solid #3daee9;}
                                          QLineEdit:focus {border: 0.2ex solid #3daee9;}
            ''')
            return True
        except:
            self.display.setStyleSheet('''QLineEdit:hover {border: 0.2ex solid #ee1111;}
                                          QLineEdit:focus {border: 0.2ex solid #ee1111;}
            ''')
            return False

    def showLatex(self):
        '''Renders and displays the typesetted equation if it is valid.
        '''
        if self.validateInput() == True:
            try:
                if self.simplifyExpressionChecked == True:
                    expressionValue = latex(sympify(self.display.text()))
                else:
                    expressionValue = latex(sympify(self.display.text(), evaluate=False))

                self.updateJax(expressionValue)

            except Exception as err:
                print(err)
        elif self.display.text() == "" or all(self.display.text()) == " ":
            self.updateJax("...")
        else:
            pass

    def updateJax(self, newMath):
        '''Typesets user's equation as MathJax
        '''
        self.mathJaxWebView.page().runJavaScript("updateMathJax(\"$${}$$\")".format(newMath.replace("\\", "\\\\")))

    def updateGraphView(self):
        graphViewItem = self.linkedGraph.data[self.name]

        if self.validateInput() == True:
            expressionValue = sympify(self.display.text())

            graphViewItem.equation = lambdify((self.x, self.y), expressionValue)
            graphViewItem.updatePlot()

        else:
            pass

#ANCHOR: LatexView
#  render LaTeX/MathJax beneath user text input
class LatexView(QWebEngineView):
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
        super(LatexView, self).__init__(parent)
        self.page().setBackgroundColor(QColor('#31363b'))
        self.setMaximumHeight(80)
        self.setMinimumHeight(60)
        self.setHtml(self.pageSource)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))

#ANCHOR: BigMiniButton
class BigMiniButton(QPushButton):
    mouseHover = pyqtSignal(bool)
    def __init__(self, icon_name, parent, onClicked = (lambda: None), base_color="#eeeeee", hover_color="#3daee9"):
        '''
        base_color and hover_color must be strings containing hex color codes
        '''
        super(BigMiniButton, self).__init__(parent)
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

        svg_files = os.listdir(root+"/icons/svg/")

        filename = "appbar."+icon_name+".svg"
        if filename in svg_files:
            f = QFile(root+'/icons/svg/'+filename)
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

#ANCHOR: MainSettingsBar
class MainSettingsBar(QToolBar):
    def __init__(self, parent=None):
        super(MainSettingsBar, self).__init__(parent)
        root = QFileInfo(__file__).absolutePath()

        self.saveButton = BigMiniButton("save",
                                         parent = self,
                                         onClicked = self.handleButton)
        self.settingsButton = BigMiniButton("protractor",
                                            parent = self,
                                            onClicked = self.handleButton)
        self.addLayerButton = BigMiniButton("add",
                                         parent = self,
                                         onClicked = self.handleButton)

        self.addWidget(self.saveButton)
        self.addWidget(self.settingsButton)
        self.addWidget(self.addLayerButton)
        self.setMinimumWidth(48*4)

    def handleButton(self):
        pass


#ANCHOR: Main app
class CalculatorApp(QWidget):
    def __init__(self, parent=None):
        super(CalculatorApp, self).__init__(parent)

        # window title & top-level layout
        self.setWindowTitle("SuperCalc")
        mainLayout = QGridLayout()

        # initialize reserved abstract math symbols and user-defined symbol dictionary
        self.x, self.y, self.z = symbols('x y z')
        self.phi, self.theta, self.r, self.rho = symbols('phi, theta, r, rho')
        self.i, self.j, self.k = symbols('i j k')
        self.u, self.v, self.w = symbols('u v w')
        self.usrvars = {}

        # initialize graph
        self.graphView = GraphView()

        # setup input table to contain equation entries
        self.inputTable = EquationTable(linkedGraph=self.graphView)

        # mini settings bar, including cog igon, colorpicker, etc..
        self.mainSettingsBar = MainSettingsBar()
        self.mainSettingsBar.addLayerButton.clicked.connect(self.addNewGraphItem)

        # add all objects to main layout
        mainLayout.addWidget(self.mainSettingsBar, 0, 0)
        mainLayout.addWidget(self.inputTable, 1, 0)
        mainLayout.addWidget(self.graphView, 1, 1)

        self.setLayout(mainLayout)

        # initialize default graph and its respective equation entry
        self.addNewGraphItem()

    def addNewGraphItem(self):
        name = self.newName()
        self.graphView.addPlotItem(name=name)
        self.inputTable.addInputItem(name=name)
        self.inputTable.inputs[name].updateGraphView()

    # Creates a unique name (a hash) for each unique plot
    def newName(self):
        name = random.getrandbits(512)
        if name not in self.inputTable.inputs.keys():
            return name
        else:
            self.newName()

    def createButton(self, text, member):
        button = Button(text)
        button.clicked.connect(member)
        return button

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    # set stylesheet
    file = QFile(":/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    calc = CalculatorApp()
    calc.show()
    sys.exit(app.exec_())

    del calc