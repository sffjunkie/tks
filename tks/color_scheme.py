# Copyright 2009-2014, Simon Kennedy, code@sffjunkie.co.uk

from collections import namedtuple

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    from tkinter import ttk
except ImportError:
    import ttk

from tks.color_square import ColorSquare

__SchemeMode = namedtuple('SchemeMode', 'MONO TRIAD')
TargetType = __SchemeMode('square', 'rectangle', 'circle')


class ColorScheme(ttk.Frame, object):
    def __init__(self, master,
                 count=5):
        super(ColorScheme, self).__init__(master)
    
        self._squares = []
        for x in range(count):
            sq = ColorSquare(self)
            sq.grid(row=0, column=x)
            