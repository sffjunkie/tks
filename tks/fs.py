# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

from __future__ import print_function, division, absolute_import
import os
import sys
import os.path

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    from tkinter import ttk
except ImportError:
    import ttk

try:
    from tkinter import filedialog
except ImportError:
    import tkFileDialog as filedialog


class FSEntry(ttk.Frame, object):
    def __init__(self, master,
                 variable=None):
        self.master = master
        super(FSEntry, self).__init__(master)

        if variable is None:
            self._var = tk.StringVar()
        else:
            self._var = variable

        self.entry = ttk.Entry(self, textvariable=self._var)
        self.entry.grid(row=0, column=0, sticky=tk.EW)

        self._btn = ttk.Button(self, text='Browse...',
                               command=self.browse)
        self._btn.grid(row=0, column=1, sticky=tk.E, padx=(6, 0))

        self.columnconfigure(0, weight=1)

    @property
    def value(self):
        return self._var.get()

    @value.setter
    def value(self, value):
        self._var.set(str(value))

    def browse(self):
        raise NotImplementedError

    def shorten(self, path):
        home_dir = os.path.expanduser('~')

        if 'win32' in sys.platform:
            path = path.replace('/', '\\')

        if path.startswith(home_dir):
            path = os.path.join('~', path[len(home_dir) + 1:])

        current_dir = os.getcwd()
        if path.startswith(current_dir):
            path = os.path.join('.', path[len(current_dir) + 1:])

        return path


class DirEntry(FSEntry):
    def __init__(self, master, variable=None, **options):
        self.master = master
        self.options = options
        super(DirEntry, self).__init__(master, variable)

    def browse(self):
        initial_dir = self._var.get()
        initial_dir = os.path.abspath(os.path.expanduser(initial_dir))

        self.options['initialdir'] = initial_dir
        dlg = filedialog.Directory(self.master, **self.options)
        new_dir = dlg.show()

        if new_dir:
            new_dir = self.shorten(new_dir)
            self.value = new_dir


class FileEntry(FSEntry):
    def __init__(self, master, variable=None, **options):
        self.master = master
        self.mode = options.pop('mode', 'open')
        self.options = options
        super(FileEntry, self).__init__(master, variable)

    def browse(self):
        initial_file = self._var.get()

        if initial_file:
            initial_dir = os.path.split(initial_file)[0]
            self.options['initialdir'] = initial_dir

        if self.mode == 'open':
            dlg = filedialog.Open(self.master, **self.options)
        else:
            dlg = filedialog.SaveAs(self.master, **self.options)

        new_file = dlg.show()

        if new_file:
            new_file = self.shorten(new_file)
            self._var.set(new_file)

