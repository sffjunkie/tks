# Copyright 2009-2014, Simon Kennedy, code@sffjunkie.co.uk

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, p)

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

from tks.date import DateEntry

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Date Test')
    entry = DateEntry(root, locale='ar')
    entry.grid(row=0, column=0)
    root.mainloop()
    