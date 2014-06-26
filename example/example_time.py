# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, p)

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

from tks.times import TimeEntry

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Time Test')
    entry = TimeEntry(root, locale='en_GB')
    entry.grid(row=0, column=0, sticky=tk.EW)
    root.columnconfigure(0, weight=1)
    root.mainloop()
