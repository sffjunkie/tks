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
    
from .i18n import language
_ = language.ugettext

from tks import color_funcs
from tks.color_var import ColorVar
from tks.color_wheel import ColorWheel
from tks.color_square import ColorSquare
from tks.color_slider import RGBSlider, HSVSlider, HLSSlider

DEFAULT_FONT = ('TkTextFont',)


class ColorEntry(ttk.Frame, object):
    """Display an entry to enter color information.
    
    :param master: Tk master widget
    :param start_color:  The starting color
    
                         * #abc or #abcdef - 'rgbhex' mode
                         * rgb(1.0, 1.0, 1.0) - 'rgb' mode
                         * hsv(1.0, 1.0, 1.0) - 'hsv' mode
                         * hls(1.0, 1.0, 1.0) - 'hls' mode
    :type start_color:   str
    """

    def __init__(self, master,
                 start_color='rgb(1.0, 0.0, 0.0)',
                 text_font=DEFAULT_FONT):
        self._master = master
        ttk.Frame.__init__(self, master)
        self._start_color = start_color

        self._color_var = tk.StringVar()
        self._entry = ttk.Entry(self, textvariable=self._color_var,
                                font=text_font)
        self._entry.grid(row=0, column=0, sticky=tk.EW)

        color_info = color_funcs.color_string_to_color(start_color)
        if color_info:
            self.valid = True
        else:
            raise ValueError(_('Unrecognised start color'))

        self._color_var.set(start_color)

        btn = ttk.Button(self, text=_('Select...'), command=self.select_color)
        btn.grid(row=0, column=5, sticky=tk.E, padx=(6,0))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

    @property
    def rgb(self):
        color_info = color_funcs.color_string_to_color(self._color_var.get())
        if color_info:
            cm = color_info[0]

            if cm in ['rgb', 'rgbhex']:
                return color_info[1]
            elif cm == 'hsv':
                return colorsys.hsv_to_rgb(*color_info[1])
            elif cm == 'hls':
                return colorsys.hls_to_rgb(*color_info[1])

            self.valid = True
        else:
            self.valid = False

    @property
    def hsv(self):
        color_info = color_funcs.color_string_to_color(self._color_var.get())
        if color_info:
            cm = color_info[0]

            if cm == 'hsv':
                return color_info[1]
            elif cm in ['rgb', 'rgbhex']:
                return colorsys.rgb_to_hsv(*color_info[1])
            elif cm == 'hls':
                rgb = colorsys.hls_to_rgb(*color_info[1])
                return colorsys.rgb_to_hsv(*rgb)

            self.valid = True
        else:
            self.valid = False

    @property
    def hls(self):
        color_info = color_funcs.color_string_to_color(self._color_var.get())
        if color_info:
            cm = color_info[0]

            if cm == 'hls':
                return self._value
            elif cm in ['rgb', 'rgbhex']:
                return colorsys.rgb_to_hls(*self._value)
            elif cm == 'hsv':
                rgb = colorsys.hsv_to_rgb(*self._value)
                return colorsys.rgb_to_hls(*rgb)

            self.valid = True
        else:
            self.valid = False

    def select_color(self):
        color_info = color_funcs.color_string_to_color(self._color_var.get())
        if not color_info:
            color_info = color_funcs.color_string_to_color(self._start_color)

        cm = color_info[0]
        color = color_info[1][:3]
        if cm in ['rgb', 'rgbhex']:
            rgb = color
        elif cm == 'hsv':
            rgb = colorsys.hsv_to_rgb(*color)
        elif cm == 'hls':
            rgb = colorsys.hls_to_rgb(*color)
            
        dlg = ColorDialog(self, _("Select a color"),
                          start_color=rgb)
        self.wait_window(dlg)
        if dlg.color is not None:
            if cm == 'rgbhex':
                self._color_var.set(color_funcs.rgb_to_hex_string(dlg.color))
            elif cm == 'rgb':
                self._color_var.set(color_funcs.rgb_to_rgb_string(dlg.color))
            elif cm == 'hsv':
                self._color_var.set(color_funcs.rgb_to_hsv_string(dlg.color))
            elif cm == 'hls':
                self._color_var.set(color_funcs.rgb_to_hls_string(dlg.color))


class ColorDialog(tk.Toplevel, object):
    """Display a dialog to obtain an RGB value.
    
    The color is returned as an (R, G, B) tuple where each component is
    between 0.0 and 1.0
    
    :param master:      The master widget
    :param title:       The window title
    :type title:        str
    :param start_color: The initial (R, G, B) tuple to display
    :type start_color:  tuple
    """
    
    def __init__(self, master, title,
                 start_color=(0.5, 0.5, 0.5)):
        super(ColorDialog, self).__init__(master)

        self.withdraw()
        self.title(title)
        
        self.color_var = ColorVar(value=start_color)

        self._color_selector = ColorWheel(self, variable=self.color_var)
        self._color_selector.grid(row=0, column=0, rowspan=3,
                                  padx=4, pady=4, sticky=tk.NW)
        
        rgb_slider = RGBSlider(self, variable=self.color_var)
        rgb_slider.grid(row=0, column=1, padx=4, pady=4, sticky=tk.NSEW)
        
        hsv_slider = HSVSlider(self, variable=self.color_var)
        hsv_slider.grid(row=1, column=1, padx=4, pady=4, sticky=tk.NSEW)
        
        hls_slider = HLSSlider(self, variable=self.color_var)
        hls_slider.grid(row=2, column=1, padx=4, pady=4, sticky=tk.NSEW)
        
        self.lbl = ColorSquare(self, variable=self.color_var, mode='rw',
                               info_text=('rgbhex', 'rgb', 'hsv', 'hls'))
        self.lbl.grid(row=0, column=2, rowspan=2, padx=4, pady=4, sticky=tk.NE)
        
        okcancel = ttk.Frame(self, padding=(3,3,3,3))
        
        self.ok_btn = ttk.Button(okcancel, text=_('OK'), width=10,
                                 command=self._ok)
        self.ok_btn.grid(row=0, column=0, padx=4, pady=4)
        cancel = ttk.Button(okcancel, text=_('Cancel'), width=10,
                            command=self._cancel)
        cancel.grid(row=1, column=0, padx=4, pady=4)

        okcancel.columnconfigure(0, weight=1)
        okcancel.columnconfigure(1, weight=0)
        okcancel.columnconfigure(2, weight=0)
        
        okcancel.grid(row=2, column=2, sticky=tk.SE)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        
        self.update_idletasks()
        self.resizable(width=False, height=False)
        
        self.bind('<Escape>', self._cancel)
        self.protocol('WM_DELETE_WINDOW', self._cancel)
        self.focus()
        self.transient(master)
        self.grab_set()
        self.deiconify()

    def _ok(self, event=None):
        self.color = self.color_var.get()
        self.grab_release()
        self.destroy()
    
    def _cancel(self, event=None):
        self.color = None
        self.grab_release()
        self.destroy()
