# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, p)

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

from tks.color_var import ColorVar
from tks.color_tints_and_shades import ColorTint, ColorShade

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Color Palette')

    color = ColorVar(value=(0.75, 0.85, 0.75))

    tints = ColorTint(root, color)
    tints.grid(row=0, column=0)
    shades = ColorShade(root, color)
    shades.grid(row=1, column=0)
    root.mainloop()
