# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

import datetime

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

import py.test

from tks.colors import ColorVar
from tks.dates import DateVar
from tks.times import TimeVar

@py.test.fixture(scope="module")
def root():
    tk.NoDefaultRoot()
    return tk.Tk()


def test_ColorVar_init(root):
    _v = ColorVar(master=root, name='A_var')


def test_ColorVar_get(root):
    v = ColorVar(master=root)

    assert v.get() == (1.0, 0.0, 0.0)


def test_ColorVar_set(root):
    v = ColorVar(master=root)
    v.set((0.25, 0.25, 0.25))

    assert v.get() == (0.25, 0.25, 0.25)


def test_ColorVar_gt1(root):
    v = ColorVar(master=root, value=(255.0, 255.0, 255.0))

    assert v.get() == (1.0, 1.0, 1.0)


def test_DateVar_init(root):
    _v = DateVar(master=root)


def test_DateVar_SetAndGet(root):
    d = datetime.date(2014, 1, 1)
    v = DateVar(master=root, value=d)

    assert v.get() == d


def test_TimeVar_init(root):
    _v = TimeVar(master=root)


def test_TimeVar_SetAndGet(root):
    t = datetime.datetime.now().time()
    v = DateVar(master=root, value=t)

    assert v.get() == t
