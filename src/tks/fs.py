# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""Allows selection of filesystem entries (directories and files).

DirEntry
    Displays a text box and a button to select a directory using the system
    defined selection method.

FileEntry
    Displays a text box and a button to select a file using the system
    defined selection method.
"""

from __future__ import print_function, division, absolute_import
import os
import sys
import os.path

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
else:
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog

from tks.tooltip import ToolTip


def shorten(path):
    """Shorten a path.

    If the path starts with the path to the home directory then replace
    it with the ``~`` character.

    If the path starts with the current directory then replace it with
    the ``.`` character
    """

    home_dir = os.path.expanduser('~')

    if 'win32' in sys.platform:
        path = path.replace('/', '\\')

    current_dir = os.getcwd()
    if path.startswith(current_dir):
        path = os.path.join('.', path[len(current_dir) + 1:])

    if path.startswith(home_dir):
        path = os.path.join('~', path[len(home_dir) + 1:])

    return path


class FSEntry(ttk.Frame, object):
    """Base class for filesystem entries."""

    def __init__(self, master,
                 variable=None):
        self.master = master
        super(FSEntry, self).__init__(master)

        if variable:
            self._variable = variable
        else:
            self._variable = tk.StringVar()

        self._full_path = ''

        self._entry = ttk.Entry(self, textvariable=self._variable)
        self._entry.grid(row=0, column=0, sticky=tk.EW)

        self._btn = ttk.Button(self, text='Browse...',
                               command=self._browse)
        self._btn.grid(row=0, column=1, sticky=tk.E, padx=(6, 0))

        self._tooltip = ToolTip(self._entry,
                                display_func=self._tooltip_display_func,
                                msg_func=self._tooltip_msg_func)

        self.columnconfigure(0, weight=1)

    @property
    def value(self):
        return self._variable.get()

    @value.setter
    def value(self, value):
        self._variable.set(str(value))

    def _browse(self):
        """Browse for an entry. To be overridden by the subclass."""

        raise NotImplementedError

    def _tooltip_display_func(self):
        return bool(self._tooltip_msg_func())

    def _tooltip_msg_func(self, *args):
        path = self._variable.get()

        if not path:
            return None

        return path


class DirEntry(FSEntry):
    """Entry box and a button to select a directory."""

    def __init__(self, master, variable=None, **options):
        self.master = master
        self.options = options
        super(DirEntry, self).__init__(master, variable)

    def _browse(self):
        """Display the dialog to _browse for a directory."""

        initial_dir = self._variable.get()
        initial_dir = os.path.abspath(os.path.expanduser(initial_dir))

        self.options['initialdir'] = initial_dir
        dlg = filedialog.Directory(self.master, **self.options)
        new_dir = dlg.show()

        if new_dir:
            new_dir = shorten(new_dir)
            self.value = new_dir


class FileEntry(FSEntry):
    """Entry box and a button to select a file."""

    def __init__(self, master, variable=None, **options):
        self.master = master
        self.mode = options.pop('mode', 'open')
        self.options = options
        super(FileEntry, self).__init__(master, variable)

    def _browse(self):
        """Display the dialog to _browse for a file."""

        initial_file = self._variable.get()

        if initial_file:
            initial_dir = os.path.split(initial_file)[0]
            self.options['initialdir'] = initial_dir

        if self.mode == 'open':
            dlg = filedialog.Open(self.master, **self.options)
        else:
            dlg = filedialog.SaveAs(self.master, **self.options)

        new_file = dlg.show()

        if new_file:
            new_file = shorten(new_file)
            self.value = new_file

