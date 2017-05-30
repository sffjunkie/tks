# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""Various functions to manipulate RGB hex, RGB, HSV and HLS colors."""

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)
import string
import colorsys


def rgb_intensity(rgb):
    """Convert an RGB color to its intensity"""

    return rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114


def contrast_color(rgb):
    """Return either white or black whichever provides the most contrast"""

    if rgb == (0.0, 0.0, 0.0) or rgb_intensity(rgb) < (160.0 / 255.0):
        return 'white'
    else:
        return 'black'


def rgb_to_hex_string(value):
    """Convert from an (R, G, B) tuple to a hex color.

    :param value: The RGB value to convert
    :type value:  tuple

    R, G and B should be in the range 0.0 - 1.0
    """
    color = ''.join(['%02x' % x1 for x1 in [int(x * 255) for x in value]])
    return '#%s' % color


def rgb_to_rgb_string(value, dp=3):
    """Convert from an (R, G, B) tuple to an RGB string.

    :param value: The RGB value to convert
    :type value:  tuple
    :param dp: Number of decimal places in the string
    :type dp: int

    R, G and B should be in the range 0.0 - 1.0
    """
    format_str = '%%.0%df' % dp
    value = 'rgb(%s)' % (','.join([format_str % x for x in value]))
    return value


def rgb_to_hsv_string(value, dp=3):
    """Convert from an (R, G, B) tuple to an HSV string.

    :param value: The RGB value to convert
    :type value:  tuple
    :param dp: Number of decimal places in the string
    :type dp: int

    R, G and B should be in the range 0.0 - 1.0
    """
    hsv = colorsys.rgb_to_hsv(*value)
    format_str = '%%.0%df' % dp
    hsv = 'hsv(%s)' % (','.join([format_str % x for x in hsv]))
    return hsv


def rgb_to_hls_string(value, dp=3):
    """Convert from an (R, G, B) tuple to an HLS string.

    :param value: The RGB value to convert
    :type value:  tuple
    :param dp: Number of decimal places in the string
    :type dp: int

    R, G and B should be in the range 0.0 - 1.0
    """
    hls = colorsys.rgb_to_hls(*value)
    format_str = '%%.0%df' % dp
    hls = 'hls(%s)' % (','.join([format_str % x for x in hls]))
    return hls


def hex_string_to_rgb(value, allow_short=True):
    """Convert from a hex color string of the form `#abc` or `#abcdef` to an
    RGB tuple.

    :param value: The value to convert
    :type value: str
    :param allow_short: If True then the short of form of an hex value is
                        accepted e.g. #fff
    :type allow_short:  bool
    """
    if value[0] != '#':
        return None

    for ch in value[1:]:
        if ch not in string.hexdigits:
            return None

    if len(value) == 7:
        # The following to_iterable function is based on the
        # :func:`grouper` function in the Python standard library docs
        # http://docs.python.org/library/itertools.html
        def to_iterable():
             # pylint: disable=missing-docstring
            args = [iter(value[1:])] * 2
            return tuple([int('%s%s' % t, 16) / 255 for t in zip(*args)])
    elif len(value) == 4 and allow_short:
        def to_iterable():
            # pylint: disable=missing-docstring
            return tuple([int('%s%s' % (t, t), 16) / 255 for t in value[1:]])
    else:
        return None

    try:
        return to_iterable()
    except ValueError:
        return None


def clamp(value):
    """Clamp a float between 0.0 and 1.0"""

    return min(max(0.0, float(value)), 1.0)


def clamped_tuple(value):
    """Clamps the values in a tuple between 0.0 and 1.0
    """
    return tuple([clamp(elem) for elem in value])


def luminosity_transform(color, luminosity=0.05):
    """Transform an RGB color by a luminosity.

    If luminosity is a tuple then the 3 elements are used to transform the red,
    green and blue values individually. If a float then the same value is used
    to transform all 3 elements."""

    if isinstance(luminosity, tuple):
        luminosity = luminosity[:3]
    else:
        luminosity = (luminosity, luminosity, luminosity)

    return tuple([clamp(e + l) for e, l in zip(color, luminosity)])


def color_string_to_tuple(value):
    """Convert a color string to a tuple of floats."""

    try:
        return clamped_tuple(value[4:-1].split(','))
    except:
        return None


def color_string_to_color(value, allow_short_hex=True):
    """Convert a color string to a (color format, value) tuple where the
    color format is one of `rgbhex`, `rgb`, `hsv` or `hls`
    """
    try:
        if value[0] == '#':
            color_format = 'rgbhex'
            rgb = hex_string_to_rgb(value, allow_short=allow_short_hex)
            if rgb:
                return color_format, rgb
        else:
            if value[:4] in ['rgb(', 'hsv(', 'hls(']:
                color_format = value[:3]
                if value[-1] == ')':
                    t = color_string_to_tuple(value)
                    if t:
                        return color_format, t
            else:
                color_format = None

        return color_format, None
    except:
        return None, None


def color_string_to_rgb(value):
    """Return an RGB tuple from a color string."""

    color_info = color_string_to_color(value)
    if color_info == (None, None):
        return color_info
    else:
        if color_info[0] == 'rgbhex' or color_info[0] == 'rgb':
            return color_info[1]
        elif color_info[0] == 'hsv':
            return colorsys.hsv_to_rgb(*color_info[1])
        elif color_info[0] == 'hls':
            return colorsys.hls_to_rgb(*color_info[1])


def rgb_tints(rgb, base_percent, count, linear=True):
    """Produce a list of tints from the base color

    :param rgb: The RGB value for which to calculate the tints
    :type rgb:  tuple
    :param base_percent: Determines the factor between the returned colors
    :type base_percent:  float
    :param count: The number of tints to return
    :type count: int
    """
    factor = base_percent
    tints = []
    number_to_calc = (2 * count) - 1
    for dummy in range(number_to_calc):
        if factor < 100:
            tints.append(rgb_tint(rgb, factor))
        else:
            tints.append(None)

        if linear:
            factor += base_percent
        else:
            factor *= (1.0 + (base_percent / 100.0))

    # Remove any duplicates from the end
    for dummy in range(number_to_calc - 1):
        t1 = tints[-1]
        t2 = tints[-2]

        if not t1:
            tints.pop()
        elif t1 and t2:
            if int(t1[0] * 255) == int(t2[0] * 255) and \
               int(t1[1] * 255) == int(t2[1] * 255) and \
               int(t1[2] * 255) == int(t2[2] * 255):

                tints.pop()
            else:
                break

    tints = tints[:count]
    #tints.reverse()
    return tints


def rgb_tint(rgb, percent=5):
    """Create a tinted version of the RGB color

    :param rgb: The RGB value for which to calculate the tint
    :type rgb:  tuple
    :param percent: Determines the percent between the specified color and
                     the tint
    :type percent:  int
    """
    return luminosity_transform(rgb, percent / 100)


def rgb_shades(rgb, base_percent, count, linear=True):
    """Produce a list of shades from the base color

    :param rgb: The RGB value for which to calculate the shades
    :type rgb:  tuple
    :param base_percent: Determines the factor between the returned colors
    :type base_percent:  float
    :param count: The number of shades to return
    :type count:  int
    """
    factor = base_percent
    shades = []
    number_to_calc = (2 * count) - 1
    for dummy in range(number_to_calc):
        if factor < 100:
            shades.append(rgb_shade(rgb, factor))
        else:
            shades.append(None)

        if linear:
            factor += base_percent
        else:
            factor *= (1.0 - (base_percent / 100.0))

    # Remove any duplicates from the end
    for dummy in range(number_to_calc - 1):
        s1 = shades[-1]
        s2 = shades[-2]

        if not s1:
            shades.pop()
        elif s1 and s2:
            if int(s1[0] * 255) == int(s2[0] * 255) and \
               int(s1[1] * 255) == int(s2[1] * 255) and \
               int(s1[2] * 255) == int(s2[2] * 255):

                shades.pop()
            else:
                break

    return shades[:count]


def rgb_shade(rgb, percent=5):
    """Create a shade of the RGB color

    :param rgb: The RGB value for which to calculate the tint
    :type rgb:  tuple
    :param percent: Determines the percent between the specified color and
                    the shade
    :type percent:  int
    """
    return luminosity_transform(rgb, -percent / 100)
