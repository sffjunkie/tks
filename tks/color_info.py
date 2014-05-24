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


class ColorInfo(ttk.Frame):
    def __init__(self, master,
                 variable):
        ttk.Frame.__init__(self, master)
                
        ttk.Style().configure('nchInfo.TLabel',
                              relief=tk.SUNKEN)
        
        self._color_var = variable
        self._color_var.trace_variable('w', self._color_var_changed)
        
        self._color_info_var = tk.StringVar(value='')
        
        l = ttk.Label(self, anchor=tk.W,
                      textvariable=self._color_info_var,
                      style='nchInfo.TLabel')
        l.grid(row=0, column=0, sticky=tk.NSEW, padx=2, pady=2)

    def _color_var_changed(self, *args):
        info = self._color_info()
        self._color_info_var.set(info)

    def _color_info(self):
        rgb = self._color_var.get()
        hsv = colorsys.rgb_to_hsv(*rgb)
        yiq = colorsys.rgb_to_yiq(*rgb)
        hls = colorsys.rgb_to_hls(*rgb)
        
        hex_color = '#%02x%02x%02x' % tuple([int(x * 255) for x in rgb])
        
        return hsv, yiq, hls, hex_color
