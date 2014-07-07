# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

"""tkStuff - A collection of Tk widgets"""

__version__ = '0.2'
__author__ = 'Simon Kennedy <code@sffjunkie.co.uk>'

import re

from tks.rc import rcfile

class DefaultColors(object):
    """A container for color names"""

    fill = 'white'
    select = '#9de5eb'
    select_dark = '#58B1B7'
    header = 'white'
    outline = '#ccc'
    today = '#eee'
    other_month = '#888'


class DefaultFonts(object):
    """A container for font information"""

    text = ('TkTextFont',)
    monospace = ('TkFixedFont',)


def load_colors():
    colors = DefaultColors()
    try:
        rc = rcfile()
        rc.read()

        header_color = rc['color.header']
        if header_color != '':
            colors.header = header_color

        select_color = rc['color.select']
        if select_color != '':
            colors.select = select_color
    except:
        pass

    return colors


def load_fonts():
    fonts = DefaultFonts()
    try:
        rc = rcfile()
        rc.read()

        font_info = rc['font.text']
        if font_info:
            elems = [i.strip() for i in font_info.split(',')]
            fonts.text = tuple([elem for elem in elems if elem][:3])

        font_info = rc['font.monospace']
        if font_info:
            elems = [i.strip() for i in font_info.split(',')]
            fonts.monospace = tuple([elem for elem in elems if elem][:3])
    except:
        pass

    return fonts


def parse_geometry(geom):
    """Return a width, height, x, y tuple from a Tk geometry"""

    re_match = re.match(r'(\d+)x(\d+)\+(\d+)\+(\d+)', geom)
    if re_match:
        return re_match.group(1, 2, 3, 4)


def rect_center(rect):
    """Return the centre of a rectangle"""

    left = min(rect[0], rect[2])
    top = min(rect[1], rect[3])

    return (left + abs(((rect[2] - rect[0]) / 2)),
            top + abs(((rect[3] - rect[1]) / 2)))


def rect_at(point, size, size_y=-1):
    """Returns a rectangle centred at `point`. If only `size` is provided then
    the rectangle will be a square. The dimensions will be size * 2
    """

    if size_y == -1:
        size_y = size

    return (point[0] - size, point[1] - size_y,
            point[0] + size, point[1] + size_y)

