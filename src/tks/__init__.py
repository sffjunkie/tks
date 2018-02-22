# Copyright 2014-2018, Simon Kennedy, sffjunkie+code@gmail.com

"""tkStuff - A collection of Tk widgets"""

__version__ = '0.2.1'
__author__ = 'Simon Kennedy <sffjunkie+code@gmail.com>'

import re
import sys
import pickle

if sys.version_info >= (3, 0):
    from base64 import encodebytes, decodebytes
    import tkinter as tk
else:
    from base64 import (encodestring as encodebytes,
                        decodestring as decodebytes)
    import Tkinter as tk

from tks.rc import rcfile, configparser

class DefaultColors(object):
    """A container for color names."""

    fill = 'white'
    select = '#9de5eb'
    select_dark = '#58B1B7'
    header = 'white'
    outline = '#ccc'
    invalid = 'red'


class DefaultFonts(object):
    """A container for font information."""

    text = ('TkTextFont',)
    monospace = ('TkFixedFont',)


def load_colors():
    """Load color definitions from the `.tksrc` file"""

    colors = DefaultColors()
    try:
        rc = rcfile()
        rc.read()

        try:
            header_color = rc['color.header']
            if header_color != '':
                colors.header = header_color
        except configparser.Error:
            pass

        try:
            select_color = rc['color.select']
            if select_color != '':
                colors.select = select_color
        except configparser.Error:
            pass
    except:
        pass

    return colors


def load_fonts():
    """Load font definitions from the `.tksrc` file"""

    def _parse_font(font_def):
        elems = [i.strip() for i in font_def.split(',')][:3]
        return tuple([elem for elem in elems if elem])

    fonts = DefaultFonts()
    try:
        rc = rcfile()
        rc.read()

        try:
            font_def = rc['font.text']
            fonts.text = _parse_font(font_def)
        except configparser.Error:
            pass

        try:
            font_def = rc['font.monospace']
            fonts.monospace = _parse_font(font_def)
        except configparser.Error:
            pass
    except:
        pass

    return fonts


def parse_geometry(geom):
    """Return a width, height, x, y tuple from a Tk geometry."""

    re_match = re.match(r'(\d+)x(\d+)\+(\d+)\+(\d+)', geom)
    if re_match:
        return re_match.group(1, 2, 3, 4)


def rect_center(rect):
    """Return the centre of a rectangle as an (x, y) tuple."""

    left = min(rect[0], rect[2])
    top = min(rect[1], rect[3])

    return (left + abs(((rect[2] - rect[0]) / 2)),
            top + abs(((rect[3] - rect[1]) / 2)))


def rect_at(point, size, size_y=-1):
    """Returns a rectangle centred at `point`. If only `size` is provided then
    the rectangle will be a square. The dimensions will be `size` * 2.
    """

    if size_y == -1:
        size_y = size

    return (point[0] - size, point[1] - size_y,
            point[0] + size, point[1] + size_y)


class PickleVar(tk.Variable, object):
    """A Tkinter variable which stores values as pickled objects."""

    def __init__(self, master=None, value=None, name=None):
        # Python 3 Tkinter does not call our set method so we'll need to
        # pickle the value now
        if value and sys.version_info >= (3, 0):
            value = self.__transform_value(value)

        super(PickleVar, self).__init__(master, value, name)

    def get(self):
        value = super(PickleVar, self).get()
        if value and not isinstance(value, bytes) and sys.version_info >= (3, 0):
            value = bytes(value, encoding='ASCII')

        value = decodebytes(value)
        return pickle.loads(value)

    def set(self, value):
        value = self.__transform_value(value)
        return tk.Variable.set(self, value)

    @staticmethod
    def __transform_value(value):
        """We need to base64 encode/decode the pickled objects as Tkinter tries
        to convert the value to a string and fails with a UnicodeDecodeError
        """
        value = pickle.dumps(value)
        value = encodebytes(value)
        return value
