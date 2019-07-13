from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QColor, QRgba64, qRgba
from PyQt5.QtGui import QFont
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import OpenGL.GL as ogl
import numpy as np

class CustomTextItem(gl.GLGraphicsItem.GLGraphicsItem):
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


class Custom3DAxis(gl.GLAxisItem):
    """Class defined to extend 'gl.GLGridItem'."""
    def __init__(self, parent, color = (1.0,1.0,1.0,1.0)):
        gl.GLAxisItem.__init__(self)
        self.parent = parent
        self.c = color

    def add_labels(self):
        """Adds axes labels."""
        x,y,z = self.size()

        #X labels
        self.x0Label = CustomTextItem(X=0, Y=-y - y/5, Z=0, text="X")
        self.x0Label.setGLViewWidget(self.parent)
        self.parent.addItem(self.x0Label)

        self.x1Label = CustomTextItem(X=0, Y=y + y/5, Z=0, text="X")
        self.x1Label.setGLViewWidget(self.parent)
        self.parent.addItem(self.x1Label)

        #Y labels
        self.y0Label = CustomTextItem(X=-x - x/5, Y=0, Z=0, text="Y")
        self.y0Label.setGLViewWidget(self.parent)
        self.parent.addItem(self.y0Label)

        self.y1Label = CustomTextItem(X=x + x/5, Y=0, Z=0, text="Y")
        self.y1Label.setGLViewWidget(self.parent)
        self.parent.addItem(self.y1Label)

        #Z labels
        self.zLabel = CustomTextItem(X=-x - x/5, Y=y + y/5 - 1, Z=0, text="Z")
        self.zLabel.setGLViewWidget(self.parent)
        self.parent.addItem(self.zLabel)

        #Z labels
        self.zLabel = CustomTextItem(X=x + x/5, Y=-y - y/5, Z=0, text="Z")
        self.zLabel.setGLViewWidget(self.parent)
        self.parent.addItem(self.zLabel)

    def add_tick_values(self, xticks=[], yticks=[], zticks=[]):
        """Adds ticks values."""
        x,y,z = self.size()
        xticks = np.linspace(-x, x, 11)[1:-1]
        yticks = np.linspace(-y, y, 11)[1:-1]
        zticks = np.linspace(-z, z, 11)[1:-1]
        tickfontsize = 8
        #X labels
        for i, xt in enumerate(xticks):
            val = CustomTextItem(X=xticks[i], Y=-y - y/15, Z=0, text=str(xt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)
        for i, xt in enumerate(xticks):
            val = CustomTextItem(X=xticks[i], Y=y + y/15, Z=0, text=str(xt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)

        #Y labels
        for i, yt in enumerate(yticks):
            val = CustomTextItem(X=-x - x/15, Y=yticks[i], Z=0, text=str(yt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)
        for i, yt in enumerate(yticks):
            val = CustomTextItem(X=x + x/15, Y=yticks[i], Z=0, text=str(yt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)

        #Z labels
        for i, zt in enumerate(zticks):
            val = CustomTextItem(X=-x - x/10, Y=y + y/10, Z=zticks[i], text=str(zt.round(3)),
                                 font=QFont('Arial', pointSize=tickfontsize, weight=50))
            val.setGLViewWidget(self.parent)
            self.parent.addItem(val)
        for i, zt in enumerate(zticks):
            val = CustomTextItem(X=x + x/10, Y=-y - y/10, Z=zticks[i], text=str(zt.round(3)),
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


app = QtGui.QApplication([])
fig1 = gl.GLViewWidget()
fig1.setBackgroundColor('#31363b')

n = 51
y = np.linspace(-10,10,n)
x = np.linspace(-10,10,100)
for i in range(n):
    yi = np.array([y[i]]*100)
    d = (x**2 + yi**2)**0.5
    z = 10 * np.cos(d) / (d+1)
    pts = np.vstack([x,yi,z]).transpose()
    plt = gl.GLLinePlotItem(pos=pts, color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
    fig1.addItem(plt)


axis = Custom3DAxis(fig1, color=(1.,1.,1.,.25))
axis.setSize(x=12, y=12, z=12)

# Setup the axis and add it to the figure
axis.add_labels()
axis.add_tick_values(xticks=[0,4,8,12], yticks=[0,6,12], zticks=[0,3,6,9,12])
fig1.addItem(axis)
fig1.opts['distance'] = 40

fig1.show()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()