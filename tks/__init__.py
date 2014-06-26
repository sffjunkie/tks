# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

"""tkStuff - A collection of Tk widgets"""

__version__ = '0.1'
__author__ = 'Simon Kennedy <code@sffjunkie.co.uk>'

import re


class ColorDefs(object):
    """A container for color names"""

    Fill = 'white'
    Select = '#9de5eb'
    SelectDark = '#58B1B7'
    Header = 'white'
    Outline = '#ccc'


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
