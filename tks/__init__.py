__version__ = '0.1'
__author__ = 'Simon Kennedy <code@sffjunkie.co.uk>'

import re

COLOR_FILL = 'white'
COLOR_FILL_SELECT = '#72e8f1'
COLOR_FILL_HEADER = 'white'
COLOR_OUTLINE = '#FEFEFE'


class TksColors():
    Fill = COLOR_FILL
    Select = COLOR_FILL_SELECT
    Header = COLOR_FILL_HEADER
    Outline = COLOR_OUTLINE


def parse_geometry(geom):
    """Return a width, height, x, y tuple from a Tk geometry"""
    
    m = re.match('(\d+)x(\d+)\+(\d+)\+(\d+)', geom)
    if m:
        return m.group(1, 2, 3, 4)
    