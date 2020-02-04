import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np

from matplotlib import use
use('AGG')

from matplotlib.pylab import gcf


import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib.pyplot import colormaps as mpl_cmaps

import breeze_resources

class GenerateGradientIcons():
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
                fig = plt.figure(figsize=(1,1))
                #fig.set_size_inches(1. * sizes[0] / sizes[1], 1, forward=False)
                ax = plt.Axes(fig, [0.,0.,1.,1.])
                ax.set_axis_off()
                fig.add_axes(ax)
                ax.imshow(data[::-1], cmap)
                plt.savefig("icons/gradients/{}.png".format(cmap_name), dpi=img_size)
                plt.close()

def mask_image(imgdata, imgtype='png', size=35):
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


class Window(QWidget):
    def __init__(self):
        super().__init__()

        root = QFileInfo(__file__).absolutePath()
        gradient_icons = os.listdir(root+"/icons/gradients/")

        iconGridContainer = QWidget()
        iconGridContainer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        iconGrid=QGridLayout(iconGridContainer)
        ilabels = {}

        for n, gradient_icon in enumerate(gradient_icons):
            gradient_name = gradient_icon.split('.')[0]

            imgdata = open("icons/gradients/"+gradient_icon, 'rb').read()
            pixmap = mask_image(imgdata)
            del imgdata

            ilabels[gradient_name] = QToolButton()
            ilabels[gradient_name].setIcon(QIcon(pixmap))
            ilabels[gradient_name].setToolTip(gradient_name)

            container=QFrame()
            layout = QVBoxLayout(container)
            layout.addWidget(ilabels[gradient_name], 0, Qt.AlignCenter)

            ilabels[gradient_name].setStyleSheet("""
                                                QToolButton {
                                                    border: 0.5ex solid #76797c;
                                                    border-radius: 21.45px;
                                                    background-color: #76797c;
                                                    margin: 0ex;
                                                    padding: 0ex;
                                                    width: 35px;
                                                    height: 35px;
                                                    icon-size: 35px 35px;
                                                }
                                                QToolButton:hover {
                                                    border: 0.5ex solid #eeeeee;
                                                    background-color: #eeeeee;
                                                }

                                                QToolButton:pressed {
                                                    border: 0.5ex solid #3daee9;
                                                    background-color: #3daee9;
                                                }
                                             """)

            iconGrid.addWidget(container, n//6, n%6) # 6-column layout

        '''
        # Create SVG Icon showcase
        buttonGridContainer = QWidget()
        buttonGridContainer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        buttonGrid = QGridLayout()
        buttonGridContainer.setLayout(buttonGrid)'''

        scrollarea = QScrollArea()
        scrollarea.setWidget(iconGridContainer)
        scrollarea.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea {border: none;}")

        mainLayout = QGridLayout()
        mainLayout.addWidget(scrollarea)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    GenerateGradientIcons()
    app = QApplication(sys.argv)

        # set stylesheet
    file = QFile(":/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

    w = Window()
    w.show()
    sys.exit(app.exec_())