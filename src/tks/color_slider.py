# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""3 element sliders to change RGB, HSV and HLS variables"""

from __future__ import print_function, division, absolute_import
import sys
import colorsys

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import ttk
else:
    import Tkinter as tk
    import ttk

import tks.colors

class ColorSlider(ttk.Frame, object):
    """Color slider base class."""

    default = (1.0, 0.0, 0.0)
    labels = ('R', 'G', 'B')

    def __init__(self, master,
                 variable=None,
                 fonts=None):
        super(ColorSlider, self).__init__(master, style='tks.TFrame')

        if variable is not None:
            self.color_var = variable
        else:
            self.color_var = tks.colors.ColorVar(value=self.default)

        self.color_var.trace_variable('w', self._color_var_changed)

        self._validate_entry = (self.register(self._tk_validate_var),
                                '%P', '%V')

        if not fonts:
            fonts = tks.load_fonts()

        elem1, elem2, elem3 = self.from_rgb(self.color_var.get())

        self._elem1_var = tk.DoubleVar(value=elem1)
        lbl = ttk.Label(self, text=self.labels[0])
        lbl.grid(row=0, column=0, padx=4)

        self._elem1_entry = ttk.Entry(self, width=4,
                                      textvariable=self._elem1_var,
                                      validate='all',
                                      validatecommand=self._validate_entry,
                                      font=fonts.monospace)
        self._elem1_entry.grid(row=0, column=1, padx=4)

        self._elem1_scale = ttk.Scale(self,
                                      to=1.0,
                                      variable=self._elem1_var,
                                      command=self._elem1_update)
        self._elem1_scale.grid(row=0, column=2, sticky=tk.EW, padx=4)

        self._elem2_var = tk.DoubleVar(value=elem2)
        lbl = ttk.Label(self, text=self.labels[1])
        lbl.grid(row=1, column=0, padx=4)

        self._elem2_number = ttk.Entry(self, width=4,
                                       textvariable=self._elem2_var,
                                       validate='all',
                                       validatecommand=self._validate_entry,
                                       font=fonts.monospace)
        self._elem2_number.grid(row=1, column=1, padx=4)

        self._elem2_scale = ttk.Scale(self,
                                      to=1.0,
                                      variable=self._elem2_var,
                                      command=self._elem2_update)
        self._elem2_scale.grid(row=1, column=2, sticky=tk.EW, padx=4)

        self._elem3_var = tk.DoubleVar(value=elem3)
        lbl = ttk.Label(self, text=self.labels[2])
        lbl.grid(row=2, column=0, padx=4)

        self._elem3_entry = ttk.Entry(self, width=4,
                                      textvariable=self._elem3_var,
                                      validate='all',
                                      validatecommand=self._validate_entry,
                                      font=fonts.monospace)
        self._elem3_entry.grid(row=2, column=1, padx=4)

        self._elem3_scale = ttk.Scale(self,
                                      to=1.0,
                                      variable=self._elem3_var,
                                      command=self._elem3_update)
        self._elem3_scale.grid(row=2, column=2, sticky=tk.EW, padx=4)

        self._elem1_var.trace_variable('w', self._color_element_var_changed)
        self._elem2_var.trace_variable('w', self._color_element_var_changed)
        self._elem3_var.trace_variable('w', self._color_element_var_changed)

        self.columnconfigure(2, weight=1)

        self._internal_color_change = False

    def from_rgb(self, rgb):
        """Convert from RGB"""

        raise NotImplementedError

    def to_rgb(self, value):
        """Convert to RGB"""

        raise NotImplementedError

    def _elem1_update(self, value):
        self._internal_color_change = True
        self._elem1_var.set(float(value))
        self._internal_color_change = False

    def _elem2_update(self, value):
        self._internal_color_change = True
        self._elem2_var.set(float(value))
        self._internal_color_change = False

    def _elem3_update(self, value):
        self._internal_color_change = True
        self._elem3_var.set(float(value))
        self._internal_color_change = False

    def _tk_validate_var(self, P, V):
        """Tkinter validation function.

        Must always return 0 or 1 or it won't get called again
        """

        rval = 1
        if V != 'focusin':
            try:
                value = float(P)
                if value > 1.0:
                    rval = 0
            except ValueError:
                rval = 0

        return rval

    def _color_element_var_changed(self, *args):
        """When an element changes value update the color variable"""

        self._internal_color_change = True
        rgb = self.to_rgb((self._elem1_var.get(),
                           self._elem2_var.get(),
                           self._elem3_var.get()))

        self.color_var.set(rgb)

    def _color_var_changed(self, *args):
        """When the color variable changes update each element"""

        if not self._internal_color_change:
            rgb = self.color_var.get()
            value = self.from_rgb(rgb)
            self._elem1_var.set(value[0])
            self._elem2_var.set(value[1])
            self._elem3_var.set(value[2])
        self._internal_color_change = False


class RGBSlider(ColorSlider):
    """An RGB Color Slider"""

    def __init__(self, master,
                 variable=None,
                 fonts=None):
        self.labels = ('R', 'G', 'B')
        self.default = (1.0, 0.0, 0.0)
        super(RGBSlider, self).__init__(master,
                                        variable,
                                        fonts=fonts)

    def from_rgb(self, rgb):
        return rgb

    def to_rgb(self, rgb):
        return rgb


class HSVSlider(ColorSlider):
    """An HSV Color Slider"""

    def __init__(self, master,
                 variable=None,
                 fonts=None):
        self.labels = ('H', 'S', 'V')
        self.default = (0.0, 1.0, 1.0)
        super(HSVSlider, self).__init__(master,
                                        variable,
                                        fonts=fonts)

    def from_rgb(self, rgb):
        return colorsys.rgb_to_hsv(*rgb)

    def to_rgb(self, hsv):
        return colorsys.hsv_to_rgb(*hsv)


class HLSSlider(ColorSlider):
    """An HLS Color Slider"""

    def __init__(self, master,
                 variable=None,
                 fonts=None):
        self.labels = ('H', 'L', 'S')
        self.default = (0.0, 0.5, 1.0)

        super(HLSSlider, self).__init__(master,
                                        variable,
                                        fonts=fonts)

    def from_rgb(self, rgb):
        return colorsys.rgb_to_hls(*rgb)

    def to_rgb(self, hls):
        return colorsys.hls_to_rgb(*hls)
