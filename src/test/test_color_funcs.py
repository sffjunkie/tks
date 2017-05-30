"""Tests for color functions"""

import py.test
from tks import color_funcs


def almost_equal(value, compare_with):
    return abs(value - compare_with) < 0.005


def tuple_almost_equal(value, compare_with):
    return all([almost_equal(i, j) for i, j in zip(value, compare_with)])

@py.test.fixture
def rgb():
    """RGB fixture"""

    return (1.0, 0.25, 0.50)

def test_clamp():
    assert color_funcs.clamp(0.5) == 0.5
    assert color_funcs.clamp(-0.1) == 0.0
    assert color_funcs.clamp(1.01) == 1.0


def test_clamped_tuple():
    assert color_funcs.clamped_tuple((0.5, 0.5, 0.5)) == (0.5, 0.5, 0.5)
    assert color_funcs.clamped_tuple((-0.5, 0.5, 0.5)) == (0.0, 0.5, 0.5)
    assert color_funcs.clamped_tuple((0.5, 1.5, 0.5)) == (0.5, 1.0, 0.5)


def test_colorstring_totuple():
    assert color_funcs.color_string_to_tuple('col(0.5, 0.5, 0.5)') == (0.5, 0.5, 0.5)
    assert color_funcs.color_string_to_tuple('col(-0.5, 0.5, 0.5)') == (0, 0.5, 0.5)
    assert color_funcs.color_string_to_tuple('col(0.5, 0.5, 1.5)') == (0.5, 0.5, 1.0)


def test_colorstring_tocolor():
    color_type, color = color_funcs.color_string_to_color('#7f7f7f')
    assert color_type == 'rgbhex'
    assert tuple_almost_equal(color, (0.5, 0.5, 0.5))


def test_rgb_to_hex_string(rgb):
    assert color_funcs.rgb_to_hex_string((1.0, 1.0, 1.0)) == '#ffffff'
    assert color_funcs.rgb_to_hex_string((0.0, 0.0, 0.0)) == '#000000'
    assert color_funcs.rgb_to_hex_string((0.5, 0.5, 0.5)) == '#7f7f7f'
    assert color_funcs.rgb_to_hex_string(rgb) == '#ff3f7f'


def test_rgb_to_rgb_string(rgb):
    assert color_funcs.rgb_to_rgb_string(rgb) == 'rgb(1.000,0.250,0.500)'


def test_rgb_to_hsv_string(rgb):
    assert color_funcs.rgb_to_hsv_string(rgb) == 'hsv(0.944,0.750,1.000)'


def test_rgb_to_hls_string(rgb):
    assert color_funcs.rgb_to_hls_string(rgb) == 'hls(0.944,0.625,1.000)'


def test_hex_string_to_rgb(rgb):
    assert tuple_almost_equal(color_funcs.hex_string_to_rgb('#ff3f7f'), rgb)


def test_intensity(rgb):
    assert almost_equal(color_funcs.rgb_intensity(rgb), 0.50275)


def test_rgb_tint(rgb):
    assert color_funcs.rgb_tint(rgb, 2) == (1.0, 0.27, 0.52)
    assert color_funcs.rgb_tint(rgb) == (1.0, 0.3, 0.55)


def test_rgb_shade(rgb):
    assert color_funcs.rgb_shade(rgb, 2) == (0.98, 0.23, 0.48)
    assert color_funcs.rgb_shade(rgb) == (0.95, 0.20, 0.45)
