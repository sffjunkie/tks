# Copyright 2009-2014, Simon Kennedy, code@sffjunkie.co.uk

from __future__ import print_function, division, absolute_import
import colorsys

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    from tkinter import ttk
except ImportError:
    import ttk

from tks.color_var import ColorVar

class ColorSlider(ttk.Frame, object):
    def __init__(self, master,
                 variable=None):
        super(ColorSlider, self).__init__(master, style='tks.TFrame')

        if variable is not None:
            self._color_var = variable
        else:
            self._color_var = ColorVar(value=self.__default__)

        self._color_var.trace_variable('w', self._color_var_changed)

        self._validate_entry = (self.register(self._tk_validate_var),
                                '%P', '%i', '%V')
    
        elem1, elem2, elem3 = self.from_rgb(self._color_var.get())
        
        self._elem1_var = tk.DoubleVar(value=elem1)
        lbl = ttk.Label(self, text=self.__labels__[0])
        lbl.grid(row=0, column=0, padx=4)
        
        self._elem1_entry = ttk.Entry(self, width=4,
                                     textvariable=self._elem1_var,
                                     validate='all',
                                     validatecommand=self._validate_entry)
        self._elem1_entry.grid(row=0, column=1, padx=4)
    
        self._elem1_scale = ttk.Scale(self,
                              to=1.0,
                              variable=self._elem1_var,
                              command=self._elem1_update)
        self._elem1_scale.grid(row=0, column=2, sticky=tk.EW, padx=4)
        
        self._elem2_var = tk.DoubleVar(value=elem2)
        lbl = ttk.Label(self, text=self.__labels__[1])
        lbl.grid(row=1, column=0, padx=4)
        
        self._elem2_number = ttk.Entry(self, width=4,
                                       textvariable=self._elem2_var,
                                       validate='all',
                                       validatecommand=self._validate_entry)
        self._elem2_number.grid(row=1, column=1, padx=4)
    
        self._elem2_scale = ttk.Scale(self,
                              to=1.0,
                              variable=self._elem2_var,
                              command=self._elem2_update)
        self._elem2_scale.grid(row=1, column=2, sticky=tk.EW, padx=4)
        
        self._elem3_var = tk.DoubleVar(value=elem3)
        lbl = ttk.Label(self, text=self.__labels__[2])
        lbl.grid(row=2, column=0, padx=4)
        
        self._elem3_entry = ttk.Entry(self, width=4,
                                      textvariable=self._elem3_var,
                                      validate='all',
                                      validatecommand=self._validate_entry)
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
    
    def _tk_validate_var(self, P, i, V):
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
        self._internal_color_change = True
        rgb = self.to_rgb((self._elem1_var.get(),
                 self._elem2_var.get(),
                 self._elem3_var.get()))

        self._color_var.set(rgb)
    
    def _color_var_changed(self, *args):
        if not self._internal_color_change:
            rgb = self._color_var.get()
            value = self.from_rgb(rgb)
            self._elem1_var.set(value[0])
            self._elem2_var.set(value[1])
            self._elem3_var.set(value[2])
        self._internal_color_change = False


class RGBSlider(ColorSlider):
    __labels__ = ('R', 'G', 'B')
    __default__ = (1.0, 0.0, 0.0)
    
    def __init__(self, master,
                 variable=None):
        super(RGBSlider, self).__init__(master, variable)
        
    def from_rgb(self, rgb):
        return rgb
        
    def to_rgb(self, rgb):
        return rgb


class HSVSlider(ColorSlider):
    __labels__ = ('H', 'S', 'V')
    __default__ = (0.0, 1.0, 1.0)
    
    def __init__(self, master,
                 variable=None):
        super(HSVSlider, self).__init__(master, variable)
        
    def from_rgb(self, rgb):
        return colorsys.rgb_to_hsv(*rgb)
        
    def to_rgb(self, hsv):
        return colorsys.hsv_to_rgb(*hsv)


class HLSSlider(ColorSlider):
    __labels__ = ('H', 'L', 'S')
    __default__ = (0.0, 0.5, 1.0)
    
    def __init__(self, master,
                 variable=None):
        super(HLSSlider, self).__init__(master, variable)
        
    def from_rgb(self, rgb):
        return colorsys.rgb_to_hls(*rgb)
        
    def to_rgb(self, hls):
        return colorsys.hls_to_rgb(*hls)
