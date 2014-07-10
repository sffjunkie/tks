# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""tks variable classes.

ColorVar
    An RGB color

DateTimeVar

"""

import pickle

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    StringType = basestring
except NameError:
    StringType = str


class PickleVar(tk.Variable, object):
    def __init__(self, master=None, value=None, name=None):
        super(PickleVar, self).__init__(master, value, name)

    def get(self):
        """Get the stored value."""

        value = self._tk.globalgetvar(self._name)
        return pickle.loads(value)

    def set(self, value):
        return tk.Variable.set(self, pickle.dumps(value))


class ColorVar(PickleVar):
    """A Tkinter Variable subclass to store an RGB color value."""

    def __init__(self, master=None, value=None, name=None):
        if value is not None:
            value = tuple([float(x) for x in value[:3]])
        else:
            value = (1.0, 0.0, 0.0)

        super(ColorVar, self).__init__(master, value, name)

    def set(self, value):
        """Set the color tuple to be stored."""

        value = tuple([float(x) for x in value[:3]])

        factorize = False
        for elem in value:
            if elem > 1.0:
                factorize = True
                break

        if factorize:
            value = tuple([x / 255.0 for x in value])

        return super(ColorVar, self).set(value)
