# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""ColorSquare displays a solid square which changes color depending on the
value of a variable. Also displays textual color information below."""

from __future__ import print_function, division, absolute_import
import sys

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import ttk
else:
    import Tkinter as tk
    import ttk

import tks.dnd
import tks.colors
import tks.tooltip
import tks.color_funcs

__all__ = ['ColorSquare']


class ColorSquare(ttk.Frame, object):
    """Displays a colored rectangle and a text description of the color
    below it. A popup menu is provided to copy the hex, RGB, HSV and HLS
    representations of the color.

    :param variable: The RGB color to display
    :type variable:  :class:`~tks.vars.ColorVar`
    :param mode:     One of `r`, `w`, `rw`. If `r` is specified then the widget
                     responds to changes in the variable. If `w` is specified
                     then the color is written to the variable on a left mouse
                     click.
    :type mode:      str
    :param color_info: The color information to display under the square as a
                       text representation of the color. The elements are
                       specified as a tuple where the following strings can be
                       provided.

                       `rgbhex`, `rgb`, `hsv`, `hls`
    :param dnd_target: If True then the square responds to colors being dropped
                       on it.
    :type dnd_target:  bool
    :param dnd_source: If True the square works as a drag and drop source.
    :type dnd_source:  bool
    """

    default = (1.0, 0.0, 0.0)

    def __init__(self, master,
                 variable=None,
                 mode='rw',
                 color_info=('rgbhex',),
                 dnd_target=True,
                 dnd_source=True,
                 fonts=None):
        self.master = master
        self.color_info = color_info
        super(ColorSquare, self).__init__(master, style='tks.TFrame')

        if not fonts:
            fonts = tks.load_fonts()

        self._canvas = tk.Canvas(self,
                                 width=100, height=100,
                                 borderwidth='1.0',
                                 relief=tk.SUNKEN)

        self._canvas.grid(row=0, column=0)
        self._canvas_cursor = None
        self._blank_label_color = self._canvas.cget('bg')

        self._tooltip = tks.tooltip.ToolTip(self._canvas,
                                            msg_func=self._color_info_func)
        self._popup = ColorPopupMenu(self)

        self._internal_color_change = False

        self._text = ttk.Label(self,
                               justify=tk.CENTER,
                               anchor=tk.CENTER,
                               font=fonts.monospace)
        self._text.grid(row=1, column=0, sticky=tk.EW)

        self.columnconfigure(0, weight=1)

        self._mode = mode
        self._variable = None

        if variable:
            self.color_var = variable
            self.rgb = variable.get()

            if 'r' in self._mode:
                self.color_var.trace_variable('w', self._color_var_changed)
        else:
            self.color_var = tks.colors.ColorVar(value=self.default)

        self._dnd_source = dnd_source
        self._dnd_target = dnd_target
        self._dnd_started = False

        self._dnd_cursor = None

        self._canvas.bind('<B1-ButtonRelease-1>', self._update_color)
        self._canvas.bind('<B1-Motion>', self._start_dnd)
        self._canvas.bind('<Button-3>', self._show_popup_menu)

    @property
    def rgb(self):
        """The RGB tuple to display. If None the the rectangle is cleared and
        the text set to the empty string."""

        return self._variable

    @rgb.setter
    def rgb(self, value):
        """Set the RGB tuple to display."""

        self._variable = value
        self._update()

    # Drag and Drop
    def _start_dnd(self, event):
        """Called to start the drag and drop operation by the binding set in
        the initialiser"""

        if self._dnd_source and self.rgb and not self._dnd_started:
            # Mouse events on Windows sometimes have `??` instead of a number
            # so force event.num to 1
            event.num = 1
            self._dnd_started = True
            tks.dnd.dnd_start(self, event)

    def dnd_accept(self, source, event):
        """Indicate that we can handle a drag and drop operation."""

        return self

    def dnd_enter(self, source, event):
        """Called by the drag and drop machinery when the mouse enters
        the canvas.
        """

        self._canvas_cursor = self._canvas['cursor']
        if self._dnd_target and source is not self and hasattr(source, 'rgb'):
            self._canvas['cursor'] = self._dnd_cursor or tks.dnd.CURSOR_WIDGET
            self._canvas['relief'] = tk.RAISED
        else:
            self._canvas['cursor'] = tks.dnd.CURSOR_FORBIDDEN
            # self._canvas.focus_set()

    def dnd_motion(self, source, event):
        """Called by the drag and drop machinery when the mouse moves within
        the canvas.
        """

    def dnd_leave(self, source, event):
        """Called by the drag and drop machinery when the mouse leaves
        the canvas.
        """

        if self._canvas_cursor:
            self._canvas['cursor'] = self._canvas_cursor
        self._canvas['relief'] = tk.SUNKEN

    def dnd_commit(self, source, event):
        """Called by the drag and drop machinery when the mouse is released
        over the canvas.
        """

        if self._dnd_target and hasattr(source, 'rgb'):
            new_rgb = source.rgb
            if new_rgb != self.rgb:
                self.rgb = new_rgb
                if 'w' in self._mode:
                    self.color_var.set(new_rgb)
        self._canvas['cursor'] = self._canvas_cursor

    def dnd_end(self, target, event):
        """Called by the drag and drop machinery to end the operation."""

        self._dnd_started = False

        if self._dnd_source and self.rgb:
            # Re-bind events that are dropped by dnd.py
            self._canvas.bind('<B1-Motion>', self._start_dnd)
            self._canvas.bind('<B1-ButtonRelease-1>', self._update_color)

    def _update_color(self, *args):
        """Update our color variable."""

        if self._variable and 'w' in self._mode and not self._dnd_started:
            self._internal_color_change = True
            self.color_var.set(self._variable)

    def _color_var_changed(self, *args):
        """Respond to changes to the color variable we're watching."""

        if not self._internal_color_change:
            self._variable = self.color_var.get()
            self._update()
        self._internal_color_change = False

    def _update(self):
        """Update for a new RGB value."""

        if self.rgb:
            self._canvas['bg'] = tks.color_funcs.rgb_to_hex_string(self.rgb)
            self._text['text'] = self._color_info_text()
        else:
            self._canvas['bg'] = self._blank_label_color
            self._text['text'] = ''

    def _color_info_text(self):
        """Generate a text representation of the color."""

        t = ''
        for info in self.color_info:
            if info == 'rgbhex':
                t1 = tks.color_funcs.rgb_to_hex_string(self.rgb)
            elif info == 'rgb':
                t1 = tks.color_funcs.rgb_to_rgb_string(self.rgb, dp=2)
            elif info == 'hsv':
                t1 = tks.color_funcs.rgb_to_hsv_string(self.rgb, dp=2)
            elif info == 'hls':
                t1 = tks.color_funcs.rgb_to_hls_string(self.rgb, dp=2)

            t = t + '%s\n' % t1

        return t

    def _color_info_func(self):
        """Called by the tooltip code to display the text representation."""

        if self.rgb is not None:
            return self._color_info_text()
        else:
            return None

    def _show_popup_menu(self, event):
        """Show the popup menu"""

        if self.rgb is not None:
            # display the popup menu
            try:
                self._popup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                # make sure to release the grab (Tk 8.0a1 only)
                self._popup.grab_release()


class ColorPopupMenu(tk.Menu, object):
    """A popup menu which displays menu items to copy a textual representation
    of the color in the square

    :param square: The square to attach the pop up menu to
    :type square:  ColorSquare
    """

    def __init__(self, square):
        self._square = square
        super(ColorPopupMenu, self).__init__(square.master, tearoff=0)

        self.add_command(label='Copy Hex Color', command=self._copy_hex)
        self.add_command(label='Copy RGB Color', command=self._copy_rgb)
        self.add_command(label='Copy HSV Color', command=self._copy_hsv)
        self.add_command(label='Copy HLS Color', command=self._copy_hls)

    def _copy_hex(self, *args):
        """Copy an RGB hex representation to the clipboard"""

        self._square.master.clipboard_clear()
        text = tks.color_funcs.rgb_to_hex_string(self._square.rgb)
        self._square.master.clipboard_append(text)

    def _copy_rgb(self, *args):
        """Copy an RGB representation to the clipboard"""

        self._square.master.clipboard_clear()
        text = tks.color_funcs.rgb_to_rgb_string(self._square.rgb)
        self._square.master.clipboard_append(text)

    def _copy_hsv(self, *args):
        """Copy an HSV representation to the clipboard"""

        self._square.master.clipboard_clear()
        text = tks.color_funcs.rgb_to_hsv_string(self._square.rgb)
        self._square.master.clipboard_append(text)

    def _copy_hls(self, *args):
        """Copy an HLS representation to the clipboard"""

        self._square.master.clipboard_clear()
        text = tks.color_funcs.rgb_to_hls_string(self._square.rgb)
        self._square.master.clipboard_append(text)
