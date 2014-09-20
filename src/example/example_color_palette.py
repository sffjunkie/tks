# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, p)

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

from tks.color_palette import PaletteSelector

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Color Palette')
    entry = PaletteSelector(root)
    entry.grid(row=0, column=0)
    root.mainloop()
