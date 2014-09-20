# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""Set the Tkinter icon."""

from __future__ import print_function, division, absolute_import

import sys
from pkgutil import get_data

if sys.version_info >= (3, 0):
    from base64 import encodebytes
    import tkinter as tk
else:
    from base64 import encodestring as encodebytes
    import Tkinter as tk


def set_icon_from_data(root, image_data):
    """Set the icon for a root window from image data.

    :param root: Toplevel window for which to set the icon.
    :param image_data: The image data to use
    :type image_data:  bytes
    """

    image = tk.PhotoImage(data=encodebytes(image_data))
    root.tk.call('wm', 'iconphoto', root._w, image)


def set_icon_from_file(root, filename):
    """Set the icon for a root window from a file.

    :param root: Toplevel window for which to set the icon.
    :param filename: The filename to read the image data from
    :type filename:  str
    """

    with open(filename, 'rb') as ds:
        data = ds.read(-1)
        set_icon_from_data(root, data)


def set_icon_from_resource(root, package, resource):
    """Set the icon for a root window to a resource

    :param root: Toplevel window for which to set the icon.
    :param package: The package in which to find the resource
    :type package:  str
    :param resource: The name of the resource
    :type resource:  str
    """

    data = get_data(package, resource)
    set_icon_from_data(root, data)
