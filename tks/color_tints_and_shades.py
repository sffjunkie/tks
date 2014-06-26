# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

"""Display tints and shades of a base color.

Provides 2 concrete classes both of which display a number of
:class:`ColorSquare`\\s enclosed in a :class:`LabelFrame` along with
a scale to adjust the distance between the colors.

ColorTint - Displays a set of tints
ColorShade - Displays a set of shades
"""

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
    """Base class for display of tints and shades."""

    def __init__(self, master,
                 variable,
                 title,
                 count,
                 distance,
                 func):
        super(_TintAndShadeBase, self).__init__(master)

        self.title = title
        self.func = func

        if variable is not None:
            self.color_var = variable
            self.color_var.trace_variable('w', self._color_var_changed)
        else:
            self.color_var = ColorVar()

        self._count = count

        frame = ttk.Labelframe(self, text=self.title)

        self._tint_squares = []
        for idx in range(self._count):
            sq = ColorSquare(frame,
                             variable=self.color_var,
                             mode='w',
                             dnd_target=False)
            sq.grid(row=0, column=idx, sticky=tk.NE, padx=4, pady=4)
            self._tint_squares.append(sq)

        frame.grid(row=0, column=0, sticky=tk.EW)

        self._distance = distance[0]
        self._distance_var = tk.DoubleVar()
        self._distance_var.set(self._distance)
        txt = ttk.Label(frame, text='Strength')
        txt.grid(row=1, column=0)

        self._factor_scale = ttk.Scale(frame,
                                       from_=distance[0],
                                       to=distance[1],
                                       variable=self._distance_var,
                                       command=self._factor_update)
        self._factor_scale.grid(row=1, column=1, columnspan=self._count - 2,
                                sticky=tk.EW)
        txt = ttk.Label(frame, width=4, textvariable=self._distance_var)
        txt.grid(row=1, column=self._count - 1, sticky=tk.E)

        self._update()

    def _color_var_changed(self, *args):
        """Update our selves when the color variable changes."""

        self._update()

    def _factor_update(self, value):
        """Update for new factor."""

        self._distance = math.floor(float(value) * 20) / 20
        self._distance_var.set('%0.2f' % self._distance)
        self._update()

    def _update(self):
        """Update the color squares"""

        if callable(self.func):
            tints = self.func(self.color_var.get(),
                              self._distance,
                              self._count)

            for idx, square in enumerate(self._tint_squares):
                if idx < len(tints):
                    square.rgb = tints[idx]
                else:
                    square.rgb = None


class ColorTint(_TintAndShadeBase):
    """Displays a sequence of tints.

    :param variable: The RGB color to produce a set of tints from
    :type variable:  :class:`tks.color_var.ColorVar`
    :param count:    The number of tints to display
    :type count:     int
    :param distance:   Determines the distance between the tints specified as a
                       min and a max range. Min and max between 1.0 and 0.0
    :type distance:    tuple
    """

    def __init__(self, master,
                 variable,
                 count=5,
                 distance=(0.95, 0.7)):
        super(ColorTint, self).__init__(master, variable, 'Tints',
                                        count=count, distance=distance,
                                        func=rgb_tints)


class ColorShade(_TintAndShadeBase):
    """Displays a sequence of shades.

    :param variable: The RGB color to produce a set of shades from
    :type variable:  :class:`tks.color_var.ColorVar`
    :param count:    The number of shades to display
    :type count:     int
    :param distance:   Determines the distance between the shades specified as a
                     min and a max range. Min and max between 1.0 and 0.0
    :type distance:    tuple
    """

    def __init__(self, master,
                 variable,
                 count=5,
                 distance=(0.95, 0.7)):
        super(ColorShade, self).__init__(master, variable, 'Shades',
                                         count=count, distance=distance,
                                         func=rgb_shades)
