# Copyright 2009-2014, Simon Kennedy, code@sffjunkie.co.uk

from __future__ import print_function, division, absolute_import

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    from tkinter import ttk
except ImportError:
    import ttk

from tks import color_funcs, dnd
from tks.tooltip import ToolTip

__all__ = ['ColorSquare']


class ColorSquare(ttk.Frame, object):
    """Displays a colored rectangle and a text description of the color
    below it. A popup menu is provided to copy the hex, RGB, HSV and HLS
    representations of the color.
    
    :param variable: The RGB color to display
    :type variable:  :class:`tks.color_var.ColorVar`
    :param mode:     One of 'r', 'w', 'rw'. If 'r' is specified then the widget
                     responds to changes in the variable. If 'w' is specified
                     then the color is written to the variable on a mouse
                     click.
    :type mode:      str
    :param color_info: The color information to display under the square as a
                       text representation of the color. The elements are
                       specified as a tuple where the following strings can be
                       provided
                       
                       'rgbhex', 'rgb', 'hsv', 'hls' 
    :param dnd_target: If True then the square ersponds to colors being dropped
                       on
    :type dnd_target:  bool
    :param dnd_source: If True the square works as a drag and drop source
    :type dnd_source:  bool
    """
    def __init__(self, master,
                 variable=None,
                 mode='rw',
                 color_info=('rgbhex',),
                 dnd_target=True,
                 dnd_source=True):
        self.master = master
        self.color_info = color_info
        super(ColorSquare, self).__init__(master, style='tks.TFrame')
        
        self._canvas = tk.Canvas(self,
                                 width=100, height=100,
                                 borderwidth='1.0',
                                 relief=tk.SUNKEN)
        
        self._canvas.grid(row=0, column=0)
        self._blank_label_color = self._canvas.cget('bg')
        
        self._tooltip = ToolTip(self._canvas, msg_func=self._color_info_func)
        self._popup = ColorPopupMenu(self)

        self._internal_color_change = False
        
        self._text = ttk.Label(self,
                               justify=tk.CENTER,
                               anchor=tk.CENTER)
        self._text.grid(row=1, column=0, sticky=tk.EW)
        
        self.columnconfigure(0, weight=1)

        self._value = None
        self._color_var = None
        
        self._mode = None
        if variable:
            self._mode = mode
            self._color_var = variable
            self.rgb = variable.get()
            
            if 'r' in self._mode:
                self._color_var.trace_variable('w', self._color_var_changed)
        
        self._dnd_source = dnd_source
        self._dnd_target = dnd_target
        self._dnd_started = False
        
        self.dnd_cursor = None
        
        self._canvas.bind('<B1-ButtonRelease-1>', self._update_color)
        self._canvas.bind('<B1-Motion>', self._start_dnd)
        self._canvas.bind('<Button-3>', self._show_popup_menu)

    @property
    def rgb(self):
        """The RGB tuple to display. If None the the rectangle is cleared and
        the text set to the empty string."""
        
        return self._value
    
    @rgb.setter
    def rgb(self, value):
        self._value = value
        self._update()
    
    # Drag and Drop
    def _start_dnd(self, event):
        if self._dnd_source and self.rgb and not self._dnd_started:
            # Mouse events on Windows sometimes have `??` instead of a number
            event.num = 1
            self._dnd_started = True
            dnd.dnd_start(self, event)

    def dnd_accept(self, source, event):
        return self

    def dnd_enter(self, source, event):
        self._canvas_cursor = self._canvas['cursor']
        if self._dnd_target and source is not self and hasattr(source, 'rgb'):
            self._canvas['cursor'] = self.dnd_cursor or dnd.CURSOR_WIDGET
            self._canvas['relief'] = tk.RAISED
        else:
            self._canvas['cursor'] = dnd.CURSOR_FORBIDDEN
            #self._canvas.focus_set()

    def dnd_motion(self, source, event):
        pass

    def dnd_leave(self, source, event):
        self._canvas['cursor'] = self._canvas_cursor
        self._canvas['relief'] = tk.SUNKEN

    def dnd_commit(self, source, event):
        if self._dnd_target and hasattr(source, 'rgb'):
            new_rgb = source.rgb
            if new_rgb != self.rgb:
                self.rgb = new_rgb
                if 'w' in self._mode:
                    self._color_var.set(new_rgb)
        self._canvas['cursor'] = self._canvas_cursor
            
    def dnd_end(self, target, event):
        self._dnd_started = False
        
        if self._dnd_source and self.rgb:
            # Re-bind events that are dropped by dnd.py
            self._canvas.bind('<B1-Motion>', self._start_dnd)
            self._canvas.bind('<B1-ButtonRelease-1>', self._update_color)
        
    def _update_color(self, *args):
        if self._value and 'w' in self._mode and not self._dnd_started:
            self._internal_color_change = True
            self._color_var.set(self._value)
    
    def _color_var_changed(self, *args):
        if not self._internal_color_change:
            self._value = self._color_var.get()
            self._update()
        self._internal_color_change = False
        
    def _update(self):
        if self.rgb:
            self._canvas['bg'] = color_funcs.rgb_to_hex_string(self.rgb)
            self._text['text'] = self._color_info_text()
        else:
            self._canvas['bg'] = self._blank_label_color
            self._text['text'] = ''
    
    def _color_info_text(self):
        t = ''
        for info in self.color_info:
            if info == 'rgbhex':
                t1 = color_funcs.rgb_to_hex_string(self.rgb)
            elif info == 'rgb':
                t1 = color_funcs.rgb_to_rgb_string(self.rgb)
            elif info == 'hsv':
                t1 = color_funcs.rgb_to_hsv_string(self.rgb)
            elif info == 'hls':
                t1 = color_funcs.rgb_to_hls_string(self.rgb)
                
            t = t + '%s\n' % t1
            
        return t
    
    def _color_info_func(self):
        if self.rgb is not None:
            return self._color_info_text()
        else:
            return None
    
    def _show_popup_menu(self, event):
        if self.rgb is not None:
            # display the popup menu
            try:
                self._popup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                # make sure to release the grab (Tk 8.0a1 only)
                self._popup.grab_release()


class ColorPopupMenu(tk.Menu, object):
    def __init__(self, square):
        self._square = square
        super(ColorPopupMenu, self).__init__(square.master, tearoff=0)
        
        self.add_command(label='Copy Hex Color', command=self._copy_hex)
        self.add_command(label='Copy RGB Color', command=self._copy_rgb)
        self.add_command(label='Copy HSV Color', command=self._copy_hsv)
        self.add_command(label='Copy HLS Color', command=self._copy_hls)
        
    def _copy_hex(self, *args):
        self._square.master.clipboard_clear()
        text = color_funcs.rgb_to_hex_string(self._square.rgb)
        self._square.master.clipboard_append(text)
    
    def _copy_rgb(self, *args):
        self._square.master.clipboard_clear()
        text = color_funcs.rgb_to_rgb_string(self._square.rgb)
        self._square.master.clipboard_append(text)
    
    def _copy_hsv(self, *args):
        self._square.master.clipboard_clear()
        text = color_funcs.rgb_to_hsv_string(self._square.rgb)
        self._square.master.clipboard_append(text)
    
    def _copy_hls(self, *args):
        self._square.master.clipboard_clear()
        text = color_funcs.rgb_to_hls_string(self._square.rgb)
        self._square.master.clipboard_append(text)
        