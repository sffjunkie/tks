"""A Tk Tooltip"""

# # {{{ Based on http://code.activestate.com/recipes/576688/ (r1)

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)
import sys

if sys.version_info >= (3, 0):
    import tkinter as tk
else:
    import Tkinter as tk

from time import time

from .i18n import language
_ = language.gettext


class ToolTip(tk.Toplevel, object):
    """Provides a ToolTip widget for Tkinter.
    To apply a ToolTip to any Tkinter widget, simply pass the widget to the
    ToolTip constructor

    :param wdgt: The widget this ToolTip is assigned to
    :param display_func: A function that if it returns False stop display of the tooltip.
    :param msg:  A static string message assigned to the ToolTip
    :param msg_func: A function that retrieves a string to use as the ToolTip text
    :param delay:   The delay in seconds before the ToolTip appears (may be float)
    :param follow:  If True, the ToolTip follows motion, otherwise hides
    """
    def __init__(self, wdgt, display_func=None,
                 msg=None, msg_func=None,
                 delay=1, follow=True):
        self.wdgt = wdgt
        # The parent of the ToolTip is the parent of the ToolTips widget
        self.parent = self.wdgt.master

        # Initalise the Toplevel
        super(ToolTip, self).__init__(self.parent, bg='black', padx=1, pady=1)
        self.withdraw()
        self.overrideredirect(True)

        self.display_func = display_func

        self.msg_var = tk.StringVar()
        if msg == None:
            self.msg_var.set(_('No message provided'))
        else:
            self.msg_var.set(msg)

        self.msg_func = msg_func
        self.delay = delay
        self.follow = follow
        self.visible = 0
        self.last_motion = 0
        # The text of the ToolTip is displayed in a Message widget
        tk.Message(self, textvariable=self.msg_var, bg='#FFFFDD',
                   aspect=1000).grid()

        # Add bindings to the widget.  This will NOT override bindings that
        # the widget already has
        self.wdgt.bind('<Enter>', self.spawn, '+')
        self.wdgt.bind('<Leave>', self.hide, '+')
        self.wdgt.bind('<Motion>', self.move, '+')

    def spawn(self, event=None):
        """Spawn the ToolTip.  This simply makes the ToolTip eligible for display.
        Usually this is caused by entering the widget

        Arguments:
          event: The event that called this funciton
        """
        if self.display_func and self.display_func() == False:
            return

        self.visible = 1
        # The after function takes a time argument in miliseconds
        self.after(int(self.delay * 1000), self.show)

    def show(self):
        """Displays the ToolTip if the time delay has been long enough"""
        if self.visible == 1 and time() - self.last_motion > self.delay:
            self.visible = 2
        if self.visible == 2:
            self.deiconify()

    def move(self, event):
        """Processes motion within the widget.

        Arguments:
          event: The event that called this function
        """
        self.last_motion = time()
        # If the follow flag is not set, motion within the widget will make
        # the ToolTip dissapear
        if self.follow == False:
            self.withdraw()
            self.visible = 1
        # Offset the ToolTip 10x10 pixes southwest of the pointer
        self.geometry('+%i+%i' % (event.x_root + 10, event.y_root + 10))
        try:
            # Try to call the message function.  Will not change the message
            # if the message function is None or the message function fails
            self.msg_var.set(self.msg_func())
        except:
            pass
        self.after(int(self.delay * 1000), self.show)

    def hide(self, event=None):
        """Hides the ToolTip.  Usually this is caused by leaving the widget

        Arguments:
          event: The event that called this function
        """
        self.visible = 0
        self.withdraw()
# # end of http://code.activestate.com/recipes/576688/ }}}
