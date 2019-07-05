from pyqtgraph.Qt import QtGui, QtCore

import numpy as np
import pyqtgraph as pg

import pyqtgraph.opengl as gl

def DipoleData(rows, cols, func, args=None):
    verts = np.empty((rows+1, cols, 3), dtype=float)
    phi = (np.arange(rows+1) * 2*np.pi *(1+2/rows)/ rows).reshape(rows+1, 1)
    th = ((np.arange(cols) * np.pi / cols).reshape(1, cols))

    if args is not None:
        r = func(th, phi, *args)
    else:
        r = func(th, phi)
    s =  r* np.sin(th)
    verts[...,2] = r * np.cos(th)
    verts[...,0] = s * np.cos(phi)
    verts[...,1] = s * np.sin(phi)

    verts = verts.reshape((rows+1)*cols, 3)[cols-1:-(cols-1)]  ## remove redundant vertexes from top and bottom
    faces = np.empty((rows*cols*2, 3), dtype=np.uint)
    rowtemplate1 = ((np.arange(cols).reshape(cols, 1) + np.array([[0, 1, 0]])) % cols) + np.array([[0, 0, cols]])
    rowtemplate2 = ((np.arange(cols).reshape(cols, 1) + np.array([[0, 1, 1]])) % cols) + np.array([[cols, 0, cols]])
    for row in range(rows):
        start = row * cols * 2
        faces[start:start+cols] = rowtemplate1 + row * cols
        faces[start+cols:start+(cols*2)] = rowtemplate2 + row * cols
    faces = faces[cols:-cols]  ## cut off zero-area triangles at top and bottom

    ## adjust for redundant vertexes that were removed from top and bottom
    vmin = cols-1
    faces[faces<vmin] = vmin
    faces -= vmin
    vmax = verts.shape[0]-1
    faces[faces>vmax] = vmax

    return gl.MeshData(vertexes=verts, faces=faces)

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 3
w.show()
w.setWindowTitle('Half Wave Dipole Radiation Pattern')

def r_theta_phi(theta, phi, k, l):
    return np.absolute((np.cos((k*l/2)*np.cos(theta)) -np.cos(k*l/2))/np.sin(theta))

p = 2*np.pi
q = 0.5

md = DipoleData(100, 100, r_theta_phi, args=(p, q))
colors = np.ones((md.faceCount(), 4), dtype=float)
colors[:,0] = np.linspace(0.1, 0.2, colors.shape[0])
colors[:,1] = np.linspace(0.2, 0.9, colors.shape[0])
colors[:,2] = np.linspace(0.0, 0.1, colors.shape[0])
md.setFaceColors(colors)
m = gl.GLMeshItem(meshdata=md, smooth=False)
w.addItem(m)

ax = gl.GLAxisItem()
ax.setSize(100,100,100)
w.addItem(ax)

g = gl.GLGridItem()
g.scale(0.2, 0.2, 0.2)
w.addItem(g)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()