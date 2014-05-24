# Copyright 2009-2014, Simon Kennedy, code@sffjunkie.co.uk

from __future__ import print_function, division, absolute_import
import math

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    from tkinter import ttk
except ImportError:
    import ttk

from tks.color_var import ColorVar
from tks.color_square import ColorSquare
from tks.color_funcs import rgb_tints, rgb_shades

__all__ = ['ColorTint', 'ColorShade']


class _TintAndShadeBase(ttk.Frame, object):
    def __init__(self, master,
                 variable,
                 count,
                 factor):
        super(_TintAndShadeBase, self).__init__(master)

        if variable is not None:
            self._color_var = variable
            self._color_var.trace_variable('w', self._color_var_changed)
        else:
            self._color_var = ColorVar()
        
        self._count = count

        frame = ttk.Labelframe(self, text=self._title)
        
        self._tint_squares = []
        for idx in range(self._count):
            sq = ColorSquare(frame,
                             variable=self._color_var,
                             mode='w',
                             dnd_target=False)
            sq.grid(row=0, column=idx, sticky=tk.NE, padx=4, pady=4)
            self._tint_squares.append(sq)

        frame.grid(row=0, column=0, sticky=tk.EW)
        
        self._factor = factor[0]
        self._factor_var = tk.DoubleVar()
        self._factor_var.set(self._factor)
        txt = ttk.Label(frame, text='Strength')
        txt.grid(row=1, column=0)
                
        self._factor_scale = ttk.Scale(frame,
                                       from_=factor[0],
                                       to=factor[1],
                                       variable=self._factor_var,
                                       command=self._factor_update)
        self._factor_scale.grid(row=1, column=1, columnspan=self._count - 2,
                                sticky=tk.EW)
        txt = ttk.Label(frame, width=4, textvariable=self._factor_var)
        txt.grid(row=1, column=self._count - 1, sticky=tk.E)
        
        self._update()
    
    def _color_var_changed(self, *args):
        self._update()
        
    def _update(self):
        tints = self._func(self._color_var.get(),
                          self._factor,
                          self._count)

        for idx, square in enumerate(self._tint_squares):
            if idx < len(tints):
                square.rgb = tints[idx]
            else:
                square.rgb = None

    def _factor_update(self, value):
        self._factor = math.floor(float(value) * 20) / 20
        self._factor_var.set('%0.2f' % self._factor)
        self._update()


class ColorTint(_TintAndShadeBase):
    """Displays a sequence of tints.
    
    :param variable: The RGB color to produce a set of tints from
    :type variable:  :class:`tks.color_var.ColorVar`
    :param count:    The number of tints to display
    :type count:     int
    :param factor:   Determines the distance between the tints specified as a
                     min and a max range. Min and max between 1.0 and 0.0
    :type factor:    tuple
    """
    
    def __init__(self, master,
                 variable,
                 count=5,
                 factor=(0.95, 0.7)):
        self._title = 'Tints'
        self._func = rgb_tints
        super(ColorTint, self).__init__(master, variable,
                                        count=count, factor=factor)


class ColorShade(_TintAndShadeBase):
    """Displays a sequence of shades.
    
    :param variable: The RGB color to produce a set of shades from
    :type variable:  :class:`tks.color_var.ColorVar`
    :param count:    The number of shades to display
    :type count:     int
    :param factor:   Determines the distance between the shades specified as a
                     min and a max range. Min and max between 1.0 and 0.0
    :type factor:    tuple
    """
    
    def __init__(self, master,
                 variable,
                 count=5,
                 factor=(0.95, 0.7)):
        self._title = 'Shades'
        self._func = rgb_shades
        super(ColorShade, self).__init__(master, variable,
                                        count=count, factor=factor)
    