# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""Display tints and shades of a base color. This module
provides 2 classes both of which display a number of
:class:`ColorSquare`\\s enclosed in a :class:`LabelFrame` along with
a scale to adjust the percent between the colors.

:class:`ColorTint`
    Displays a set of tints

:class:`ColorShade`
    Displays a set of shades
"""

from __future__ import print_function, division, absolute_import
import sys
import math

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import ttk
else:
    import Tkinter as tk
    import ttk

from .i18n import language
_ = language.gettext

import tks.colors
import tks.color_funcs
import tks.color_square

__all__ = ['ColorTint', 'ColorShade']


class _TintAndShadeBase(ttk.Frame, object):
    """Base class for display of tints and shades."""

    def __init__(self, master,
                 variable,
                 title,
                 count,
                 percent,
                 func):
        super(_TintAndShadeBase, self).__init__(master)

        self.title = title
        self.func = func

        if variable is not None:
            self.color_var = variable
            self.color_var.trace_variable('w', self._color_var_changed)
        else:
            self.color_var = tks.colors.ColorVar()

        self._count = count

        frame = ttk.Labelframe(self, text=self.title)

        self._tint_squares = []
        for idx in range(self._count):
            sq = tks.color_square.ColorSquare(frame,
                                              variable=self.color_var,
                                              mode='w',
                                              dnd_target=False)
            sq.grid(row=0, column=idx, sticky=tk.NE, padx=4, pady=4)
            self._tint_squares.append(sq)

        frame.grid(row=0, column=0, sticky=tk.EW)

        self._percent = percent[0]
        self._percent_var = tk.DoubleVar()
        self._percent_var.set(self._percent)
        txt = ttk.Label(frame, text=_('Distance'))
        txt.grid(row=1, column=0)

        self._factor_scale = ttk.Scale(frame,
                                       from_=percent[0],
                                       to=percent[1],
                                       variable=self._percent_var,
                                       command=self._percent_update)
        self._factor_scale.grid(row=1, column=1, columnspan=self._count - 2,
                                sticky=tk.EW)
        txt = ttk.Label(frame, width=4, textvariable=self._percent_var,
                        anchor=tk.W, padding=(6, 0))
        txt.grid(row=1, column=self._count - 1, sticky=tk.EW)


        self._update()

    def _color_var_changed(self, *args):
        """Update our selves when the color variable changes."""

        self._update()

    def _percent_update(self, value):
        """Update for new factor."""

        new_percent = math.floor(float(value))
        self._percent_var.set('%d' % new_percent)
        if new_percent != self._percent:
            self._percent = new_percent
            self._update()

    def _update(self):
        """Update the color squares"""

        if callable(self.func):
            tints = self.func(self.color_var.get(),
                              self._percent,
                              self._count)

            for idx, square in enumerate(self._tint_squares):
                if idx < len(tints):
                    square.rgb = tints[idx]
                else:
                    square.rgb = None


class ColorTint(_TintAndShadeBase):
    """Displays a sequence of tints.

    :param variable: The RGB color to produce a set of tints from
    :type variable:  :class:`tks.vars.ColorVar`
    :param count:    The number of tints to display
    :type count:     int
    :param percent: Determines the percent between the tints specified as a
                     min and a max range.
    :type percent:  tuple
    """

    def __init__(self, master,
                 variable,
                 count=5,
                 percent=(1, 5)):
        super(ColorTint, self).__init__(master, variable, _('Tints'),
                                        count=count,
                                        percent=percent,
                                        func=tks.color_funcs.rgb_tints)


class ColorShade(_TintAndShadeBase):
    """Displays a sequence of shades.

    :param variable: The RGB color to produce a set of shades from
    :type variable:  :class:`tks.vars.ColorVar`
    :param count:    The number of shades to display
    :type count:     int
    :param percent: Determines the percentage percent between the shades
                     specified as a min and a max range.
    :type percent:  tuple
    """

    def __init__(self, master,
                 variable,
                 count=5,
                 percent=(1, 5)):
        super(ColorShade, self).__init__(master, variable, _('Shades'),
                                         count=count,
                                         percent=percent,
                                         func=tks.color_funcs.rgb_shades)
