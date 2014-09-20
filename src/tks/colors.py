# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

""":mod:`tks.colors` provides 3 classes to obtain a color from a user.

:class:`ColorVar`
    A Tk variable which holds an RGB color.

:class:`ColorEntry`
    Displays an entry box to enter a color as well as a button to
    display a color selection dialog.

:class:`ColorDialog`
    Displays a dialog window allowing the user to select a color using a
    color wheel or sliders.
"""

from __future__ import print_function, division, absolute_import
import sys
import colorsys

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import ttk
else:
    import Tkinter as tk
    import ttk

from .i18n import language
_ = language.gettext

import tks
import tks.color_funcs
import tks.color_wheel
import tks.color_square
import tks.color_slider

DEFAULT_RGB = (1.0, 0.0, 0.0)


class ColorVar(tks.PickleVar):
    """A Tkinter Variable subclass to store an RGB color tuple."""

    def __init__(self, master=None, value=None, name=None):
        if value is not None:
            if sys.version_info >= (3, 0):
                value = self.__transform_value(value)
            else:
                value = tuple([float(x) for x in value[:3]])
        else:
            value = DEFAULT_RGB

        super(ColorVar, self).__init__(master, value, name)

    def set(self, value):
        """Set the color tuple to be stored."""

        value = self.__transform_value(value)
        return super(ColorVar, self).set(value)

    def __transform_value(self, value):
        """If any element of the tuple is greater than 1.0 then all values
        will be divided by 255.0
        """
        value = [float(x) for x in value[:3]]

        if any([x > 1.0 for x in value]):
            value = [x / 255.0 for x in value]

        return tuple(value)


class ColorEntry(ttk.Frame, object):
    """Displays an entry to enter color information and a button to display a
    selection dialog.

    :param master: Tk master widget
    :param variable: The variable which hold the color to display in
                     the entry box.
    :type variable:  :class:`tks.colors.ColorVar`
    :param color_format: How to display the color in the entry box. One of the
                         following ``rgbhex``, ``rgb``, ``hsv`` or ``hls``
    :type color_format:  str
    :param fonts:    Fonts to use
    :type font:      :class:`~tks.DefaultFonts`
    """

    def __init__(self, master,
                 variable=None,
                 color_format='rgbhex',
                 fonts=None,
                 colors=None):
        super(ColorEntry, self).__init__(master, style='tks.TFrame')

        if variable:
            if not isinstance(variable, ColorVar):
                raise ValueError('"variable" argument must be a ColorVar')

            self._variable = variable
        else:
            self._variable = ColorVar()

        if not fonts:
            fonts = tks.load_fonts()

        if not colors:
            self.colors = tks.load_colors()

        self._color_format = color_format
        self._valid = True

        self._text_var = tk.StringVar()
        self._entry = ttk.Entry(self, textvariable=self._text_var,
                                font=fonts.text)
        self._entry.grid(row=0, column=0, sticky=tk.EW)

        btn = ttk.Button(self, text=_('Select...'), command=self._select_color)
        btn.grid(row=0, column=5, sticky=tk.E, padx=(6, 0))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        txt = self._color_to_text()
        self._text_var.set(txt)
        self.valid = True

        self._variable.trace_variable('w', self._variable_changed)
        self._text_var.trace_variable('w', self._text_changed)

    @property
    def rgb(self):
        """RGB representation of the selected color"""

        return self._variable.get()

    @property
    def hsv(self):
        """HSV representation of the selected color"""

        color = self._variable.get()
        return colorsys.rgb_to_hsv(*color)

    @property
    def hls(self):
        """HLS representation of the selected color"""

        color = self._variable.get()
        return colorsys.rgb_to_hls(*color)

    @property
    def value(self):
        return self._variable.get()

    @value.setter
    def value(self, value):
        return self._variable.set(value)

    @property
    def valid(self):
        return self._valid

    @valid.setter
    def valid(self, value):
        if value:
            self._entry.configure(foreground='black')
        else:
            self._entry.configure(foreground=self.colors.invalid)

    def _variable_changed(self, *args):
        txt = self._color_to_text()
        self._text_var.set(txt)

    def _color_to_text(self):
        color = self._variable.get()

        if self._color_format == 'rgbhex':
            txt = tks.color_funcs.rgb_to_hex_string(color)
        elif self._color_format == 'rgb':
            txt = tks.color_funcs.rgb_to_rgb_string(color)
        elif self._color_format == 'hsv':
            txt = tks.color_funcs.rgb_to_hsv_string(color)
        elif self._color_format == 'hls':
            txt = tks.color_funcs.rgb_to_hls_string(color)

        return txt

    def _text_changed(self, *args):
        value = self._text_var.get()
        ci = tks.color_funcs.color_string_to_color(value,
                                                   allow_short_hex=False)
        self._color_format = ci[0]
        if ci[1] != None:
            self._variable.set(ci[1])
            self.valid = True
        else:
            self.valid = False

    def _select_color(self):
        """Display the color selection dialog"""

        value = self._text_var.get()
        color_info = tks.color_funcs.color_string_to_color(value)

        if color_info[1]:
            color_format = color_info[0]
            color = color_info[1]
            if color_format in ['rgb', 'rgbhex']:
                rgb = color
            elif color_format == 'hsv':
                rgb = colorsys.hsv_to_rgb(*color)
            elif color_format == 'hls':
                rgb = colorsys.hls_to_rgb(*color)
        else:
            rgb = DEFAULT_RGB

        self._color_format = color_format

        dlg = ColorDialog(self, _("Select a Color"),
                          start_color=rgb)
        self.wait_window(dlg)
        if dlg.color is not None:
            self._variable.set(dlg.color)


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
                 start_color=(0.5, 0.5, 0.5),
                 fonts=None):
        super(ColorDialog, self).__init__(master)

        self.withdraw()
        self.title(title)

        if not fonts:
            fonts = tks.load_fonts()

        self.color = None

        bg_color = ttk.Style().lookup('TFrame', 'background')
        ttk.Style().configure('tks.TFrame', background=bg_color)

        start_color, self._scaled = self._scale_color_var(start_color)
        self.color_var = ColorVar(value=start_color)

        self._color_selector = tks.color_wheel.ColorWheel(self, variable=self.color_var)
        self._color_selector.grid(row=0, column=0, rowspan=3,
                                  padx=4, pady=4, sticky=tk.NW)

        rgb_slider = tks.color_slider.RGBSlider(self,
                                                variable=self.color_var,
                                                fonts=fonts)
        rgb_slider.grid(row=0, column=1, padx=4, pady=4, sticky=tk.NSEW)

        hsv_slider = tks.color_slider.HSVSlider(self,
                                                variable=self.color_var,
                                                fonts=fonts)
        hsv_slider.grid(row=1, column=1, padx=4, pady=4, sticky=tk.NSEW)

        hls_slider = tks.color_slider.HLSSlider(self,
                                                variable=self.color_var,
                                                fonts=fonts)
        hls_slider.grid(row=2, column=1, padx=4, pady=4, sticky=tk.NSEW)

        self.lbl = tks.color_square.ColorSquare(self, variable=self.color_var,
                                                mode='rw',
                                                color_info=('rgbhex', 'rgb',
                                                            'hsv', 'hls'),
                                                fonts=fonts)
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
