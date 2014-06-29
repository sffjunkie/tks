# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

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
_ = language.gettext

from tks import color_funcs
from tks.color_var import ColorVar
from tks.color_wheel import ColorWheel
from tks.color_square import ColorSquare
from tks.color_slider import RGBSlider, HSVSlider, HLSSlider

DEFAULT_FONT = ('TkTextFont',)


class ColorEntry(ttk.Frame, object):
    """Displays an entry to enter color information and a button to display an
    entry dialog.

    :param master: Tk master widget
    :param start_color:  The starting color.

                         Colors can be specified using any of the following
                         forms ::

                             #abc or #abcdef
                             rgb(1.0, 1.0, 1.0)
                             hsv(1.0, 1.0, 1.0)
                             hls(1.0, 1.0, 1.0)
    :type start_color:   str
    """

    def __init__(self, master,
                 start_color='rgb(1.0, 0.0, 0.0)',
                 font=DEFAULT_FONT):
        super(ColorEntry, self).__init__(master, style='tks.TFrame')
        self._master = master
        self._start_color = start_color

        self.color_var = tk.StringVar()
        self._entry = ttk.Entry(self, textvariable=self.color_var,
                                font=font)
        self._entry.grid(row=0, column=0, sticky=tk.EW)

        color_info = color_funcs.color_string_to_color(start_color)
        if color_info:
            self.valid = True
        else:
            raise ValueError(_('Unrecognised start color'))

        self.color_var.set(start_color)

        btn = ttk.Button(self, text=_('Select...'), command=self._select_color)
        btn.grid(row=0, column=5, sticky=tk.E, padx=(6, 0))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

    @property
    def rgb(self):
        """RGB representation of the selected color"""

        color_info = color_funcs.color_string_to_color(self.color_var.get())
        if color_info:
            color_mode = color_info[0]
            color = color_info[1][:3]

            if color_mode in ['rgb', 'rgbhex']:
                return color
            elif color_mode == 'hsv':
                return colorsys.hsv_to_rgb(*color)
            elif color_mode == 'hls':
                return colorsys.hls_to_rgb(*color)

            self.valid = True
        else:
            self.valid = False

    @property
    def hsv(self):
        """HSV representation of the selected color"""

        color_info = color_funcs.color_string_to_color(self.color_var.get())
        if color_info:
            color_mode = color_info[0]
            color = color_info[1][:3]

            if color_mode == 'hsv':
                return color
            elif color_mode in ['rgb', 'rgbhex']:
                return colorsys.rgb_to_hsv(*color)
            elif color_mode == 'hls':
                rgb = colorsys.hls_to_rgb(*color)
                return colorsys.rgb_to_hsv(*rgb)

            self.valid = True
        else:
            self.valid = False

    @property
    def hls(self):
        """HLS representation of the selected color"""

        color_info = color_funcs.color_string_to_color(self.color_var.get())
        if color_info:
            color_mode = color_info[0]
            color = color_info[1][:3]

            if color_mode == 'hls':
                return color
            elif color_mode in ['rgb', 'rgbhex']:
                return colorsys.rgb_to_hls(*color)
            elif color_mode == 'hsv':
                rgb = colorsys.hsv_to_rgb(*color)
                return colorsys.rgb_to_hls(*rgb)

            self.valid = True
        else:
            self.valid = False

    def _select_color(self):
        """Display the color selection dialog"""

        color_info = color_funcs.color_string_to_color(self.color_var.get())
        if not color_info:
            color_info = color_funcs.color_string_to_color(self._start_color)

        color_mode = color_info[0]
        color = color_info[1][:3]
        if color_mode in ['rgb', 'rgbhex']:
            rgb = color
        elif color_mode == 'hsv':
            rgb = colorsys.hsv_to_rgb(*color)
        elif color_mode == 'hls':
            rgb = colorsys.hls_to_rgb(*color)

        dlg = ColorDialog(self, _("Select a Color"),
                          start_color=rgb)
        self.wait_window(dlg)
        if dlg.color is not None:
            if color_mode == 'rgbhex':
                self.color_var.set(color_funcs.rgb_to_hex_string(dlg.color))
            elif color_mode == 'rgb':
                self.color_var.set(color_funcs.rgb_to_rgb_string(dlg.color))
            elif color_mode == 'hsv':
                self.color_var.set(color_funcs.rgb_to_hsv_string(dlg.color))
            elif color_mode == 'hls':
                self.color_var.set(color_funcs.rgb_to_hls_string(dlg.color))


class ColorDialog(tk.Toplevel, object):
    """Display a dialog to obtain an RGB value.

    The color is returned as an (R, G, B) tuple where each component is
    between 0.0 and 1.0

    :param master:      The master widget
    :param title:       The window title
    :type title:        str
    :param start_color: The initial (R, G, B) tuple to display.

                        If any element of the tuple is greater than 1.0 then
                        it is assumed that all values need to be scaled by
                        255.0 both when setting and obtaining the color value.
    :type start_color:  tuple
    """

    def __init__(self, master, title,
                 start_color=(0.5, 0.5, 0.5)):
        super(ColorDialog, self).__init__(master)

        self.withdraw()
        self.title(title)

        self.color = None

        bg_color = ttk.Style().lookup('TFrame', 'background')
        ttk.Style().configure('tks.TFrame', background=bg_color)

        start_color, self._scaled = self._scale_color_var(start_color)
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
                               color_info=('rgbhex', 'rgb', 'hsv', 'hls'))
        self.lbl.grid(row=0, column=2, rowspan=2, padx=4, pady=4, sticky=tk.NE)

        okcancel = ttk.Frame(self, padding=(3, 3, 3, 3), style='tks.TFrame')

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
        """Respond to OK button being selected."""

        self.color = self.color_var.get()
        if self._scaled:
            self.color = tuple([elem * 255.0 for elem in self.color])
        self.grab_release()
        self.destroy()

    def _cancel(self, event=None):
        """Respond to Escape key and Cancel button being selected"""

        self.color = None
        self.grab_release()
        self.destroy()

    def _scale_color_var(self, value):
        """If any element of the color variable is > 1.0 then divide all
        elements by 255.0
        """

        scale = False
        for elem in value:
            if elem > 1.0:
                scale = True

        if scale:
            return tuple([float(e) / 255.0 for e in value]), True
        else:
            return value, False
