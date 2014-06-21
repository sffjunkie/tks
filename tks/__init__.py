__version__ = '0.1'
__author__ = 'Simon Kennedy <code@sffjunkie.co.uk>'

import re


class TksColors():
    Fill = 'white'
    Select = '#9de5eb'
    SelectDark = '#58B1B7'
    Header = 'white'
    Outline = '#ccc'


def parse_geometry(geom):
    """Return a width, height, x, y tuple from a Tk geometry"""
    
    m = re.match('(\d+)x(\d+)\+(\d+)\+(\d+)', geom)
    if m:
        return m.group(1, 2, 3, 4)
    