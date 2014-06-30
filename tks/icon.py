# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

"""Set the Tkinter icon."""

from __future__ import print_function, division, absolute_import

from pkgutil import get_data

try:
    from base64 import encodebytes
except ImportError:
    from base64 import encodestring as encodebytes

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk


def set_icon(root, package, resource):
    """Set the icon for a root window to a resource

    :param root: Tkinter root window for which to set the icon.
    :param package: The package in which to find the resource
    :type package:  str
    :param resource: The name of the resource
    :type resource:  str
    """

    data = encodebytes(get_data(package, resource))
    image = tk.PhotoImage(data=data)
    root.tk.call('wm', 'iconphoto', root._w, image)
