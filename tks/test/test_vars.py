# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

import datetime

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

import py.test

from tks.vars import ColorVar, DateVar, TimeVar

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


def test_DateVar_init(root):
    _v = DateVar(master=root)


def test_DateVar_SetAndGet(root):
    v = DateVar(master=root)

    d = datetime.date(2014, 1, 1)
    v.set(d)

    assert v.get() == d


def test_TimeVar_init(root):
    _v = TimeVar(master=root)


def test_TimeVar_SetAndGet(root):
    v = DateVar(master=root)

    t = datetime.datetime.now().time()
    v.set(t)

    assert v.get() == t
