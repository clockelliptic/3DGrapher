import os

import numpy as np

from matplotlib import cm
from matplotlib.pyplot import colormaps as mpl_cmaps
from matplotlib.pyplot import figure as plt_figure, Axes as plt_Axes, savefig as plt_savefig, close as plt_close

from PyQt5.QtCore import (QFileInfo)

# Checks to make sure there is a PNG icon for each colormap; generates any that are missing
class GradientIconGenerator():
    """
    Uses matplotlib to generate small PNG preview icons of each colormap.
    These icons are used as the background of the buttons in the ColormapMenu.

    Note: Redundant or ugly matplotlib colormaps are not made available to the user.
    """
    def __init__(self, parent=None):
        img_size = 35 # square dimension of output image
        data = np.mgrid[0:255:255j, 0:255][0]

        removed_cmaps = ['Accent', 'Paired', 'Dark', 'Pastel', 'tab', 'Set', 'flag', '_r', 'gray', 'Greys']
        kept_cmaps = [i for i in mpl_cmaps() if not any([(j in i) for j in removed_cmaps])]

        root = QFileInfo(__file__).absolutePath()
        gradient_icons = [i.split('.')[0] for i in os.listdir(root+"/../../styles/assets/icons/gradients/")]

        for cmap_name in kept_cmaps:
            if cmap_name not in gradient_icons:
                cmap = cm.get_cmap(cmap_name)
                sizes = np.shape(data)
                fig = plt_figure(figsize=(1,1))
                #fig.set_size_inches(1. * sizes[0] / sizes[1], 1, forward=False)
                ax = plt_Axes(fig, [0.,0.,1.,1.])
                ax.set_axis_off()
                fig.add_axes(ax)
                ax.imshow(data[::-1], cmap)
                plt_savefig("../../styles/assets/icons/gradients/{}.png".format(cmap_name), dpi=img_size)
                plt_close()


