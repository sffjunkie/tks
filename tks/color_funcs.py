# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

"""Various functions to manipulate RGB hex, RGB, HSV and HLS colors."""

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)
import string
import colorsys


def rgb_to_hex_string(value):
    """Convert from an (R, G, B) tuple to a hex color.

    :param value: The RGB value to convert
    :type value:  tuple

    R, G and B should be in the range 0.0 - 1.0
    """
    color = ''.join(['%02x' % x1 for x1 in [x * 255 for x in value]])
    return '#%s' % color


def rgb_to_rgb_string(value):
    """Convert from an (R, G, B) tuple to an RGB string.

    :param value: The RGB value to convert
    :type value:  tuple

    R, G and B should be in the range 0.0 - 1.0
    """
    value = 'rgb(%s)' % (','.join(['%.02f' % x for x in value]))
    return value


def rgb_to_hsv_string(value):
    """Convert from an (R, G, B) tuple to an HSV string.

    :param value: The RGB value to convert
    :type value:  tuple

    R, G and B should be in the range 0.0 - 1.0
    """
    hsv = colorsys.rgb_to_hsv(*value)
    hsv = 'hsv(%s)' % (','.join(['%.02f' % x for x in hsv]))
    return hsv


def rgb_to_hls_string(value):
    """Convert from an (R, G, B) tuple to an HLS string.

    :param value: The RGB value to convert
    :type value:  tuple

    R, G and B should be in the range 0.0 - 1.0
    """
    hls = colorsys.rgb_to_hls(*value)
    hls = 'hls(%s)' % (','.join(['%.02f' % x for x in hls]))
    return hls


def hex_string_to_rgb(value):
    """Convert from a hex color string of the form `#abc` or `#abcdef` to an
    RGB tuple
    """
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
    elif len(value) == 4:
        def to_iterable():
            # pylint: disable=missing-docstring
            return tuple([int('%s%s' % (t, t), 16) / 255 for t in value[1:]])
    else:
        return None

    try:
        return to_iterable()
    except ValueError:
        return None


def clamped_tuple(value):
    """Clamps the values in a tuple between 0.0 and 1.0
    """
    def _clamp(value):  # pylint: disable=missing-docstring
        value = float(value)
        return min(max(0.0, value), 1.0)

    return tuple([_clamp(elem) for elem in value])


def color_string_to_tuple(value):
    """Convert a color string to a tuple of floats."""

    return clamped_tuple(value[4:-1].split(','))


def color_string_to_color(value):
    """Convert a color string to a mode, value tuple where mode is one of
    `rgbhex`, `rgb`, `hsv` or `hls`
    """
    if value[0] == '#':
        rgb = hex_string_to_rgb(value)
        if rgb is not None:
            return 'rgbhex', rgb

    mode = value[:4]
    if mode in ['rgb(', 'hsv(', 'hls('] and value[-1] == ')':
        try:
            t = color_string_to_tuple(value)
            return mode[:3], t
        except ValueError:
            return None

    return None


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
    :type percent:  float
    """
    return _color_transform(rgb, percent / 100)


def rgb_shades(rgb, base_percent, count, linear=True):
    """Produce a list of shades from the base color

    :param rgb: The RGB value for which to calculate the shades
    :type rgb:  tuple
    :param base_percent: Determines the factor between the returned colors
    :type base_percent:  float
    :param count: The number of shades to return
    :type count: int
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
    :type percent:  float
    """
    return _color_transform(rgb, -percent / 100)


def _color_transform(color, luminosity=1.0):
    return tuple([min(max(0.0, elem + luminosity), 1.0) for elem in color])
