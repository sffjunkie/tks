# Copyright 2009-2014, Simon Kennedy, code@sffjunkie.co.uk

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    StringType = basestring
except:
    StringType = str


class ColorVar(tk.Variable):
    def __init__(self, master=None, value=None, name=None):
        if value is not None:
            value = tuple(map(float, value))
        else:
            value = (1.0, 0.0, 0.0)
            
        tk.Variable.__init__(self, master, value, name)

    def get(self):
        value = self._tk.globalgetvar(self._name)
        if isinstance(value, tuple):
            return value
        else:
            return eval(str(value))

    def set(self, value):
        if isinstance(value, StringType):
            value = eval(value)
        
        value = tuple(map(float, value))
        return tk.Variable.set(self, str(value))
