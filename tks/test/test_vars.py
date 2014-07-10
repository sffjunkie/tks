# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

import py.test

from tks.vars import ColorVar

@py.test.fixture(scope="module")
def root():
    tk.NoDefaultRoot()
    return tk.Tk()

def test_ColorVar_init(root):
    v = ColorVar(master=root)

    assert v.get() == (1.0, 0.0, 0.0)

def test_ColorVar_set(root):
    v = ColorVar(master=root)
    v.set((0.25, 0.25, 0.25))

    assert v.get() == (0.25, 0.25, 0.25)
