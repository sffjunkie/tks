# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, p)

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

import tks.colors
import tks.color_funcs

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Color Test')

    var = tks.colors.ColorVar(value=tks.color_funcs.hex_string_to_rgb('#fedcba'))
    entry = tks.colors.ColorEntry(root, variable=var, color_format='rgbhex')
    entry.grid(row=0, column=0, sticky=tk.EW)

    root.columnconfigure(0, weight=1)
    root.mainloop()
