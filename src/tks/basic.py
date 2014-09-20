"""Basic Entry Types
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

import tks

from tks.i18n import language
_ = language.gettext


class BooleanEntry(ttk.Frame, object):
    """A boolean entry widget"""

    def __init__(self, master, true_text='True', false_text='False'):
        super(BooleanEntry, self).__init__(master)

        self._value = tk.BooleanVar()
        y = ttk.Radiobutton(master, text=true_text,
                            variable=self._value, value=True)
        y.grid(column=0, row=0, padx=(0, 5))

        n = ttk.Radiobutton(master, text=false_text,
                            variable=self._value, value=False)
        n.grid(column=1, row=0)

    @property
    def value(self):
        return self._value.get()

    @value.setter
    def value(self, value):
        self._value.set(value)


class IntEntry(ttk.Frame, object):
    """A boolean entry widget"""

    def __init__(self, master, min=0, max=-1):
        super(IntEntry, self).__init__(master)

        self._value = tk.IntVar()
        i = ttk.Entry(master, textvariable=self._value)
        i.grid(row=0, column=0)

    @property
    def value(self):
        return self._value.get()

    @value.setter
    def value(self, value):
        self._value.set(value)
