# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

"""A 3 element color variable"""

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    StringType = basestring
except NameError:
    StringType = str


class ColorVar(tk.Variable, object):
    """A 3 element color variable"""

    def __init__(self, master=None, value=None, name=None):
        if value is not None:
            value = tuple([float(x) for x in value[:3]])
        else:
            value = (1.0, 0.0, 0.0)

        super(ColorVar, self).__init__(master, value, name)

    def get(self):
        value = self._tk.globalgetvar(self._name)
        if isinstance(value, tuple):
            return value
        else:
            return eval(str(value))

    def set(self, value):
        if isinstance(value, StringType):
            value = eval(value)

        value = tuple([float(x) for x in value[:3]])
        return tk.Variable.set(self, str(value))
