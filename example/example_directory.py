# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, p)

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

from tks.fs import DirEntry, FileEntry

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Directory Test')
    entry = DirEntry(root)
    entry.grid(row=0, column=0, sticky=tk.EW)
    entry = FileEntry(root)
    entry.grid(row=1, column=0, sticky=tk.EW)
    root.columnconfigure(0, weight=1)
    root.mainloop()
