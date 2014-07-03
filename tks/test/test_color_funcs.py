import unittest
import py.test
from tks import color_funcs

@py.test.fixture
def rgb():
    return (1.0, 0.25, 0.50)

def test_rgb_to_hex_string(rgb):
    assert color_funcs.rgb_to_hex_string(rgb) == '#ff3f7f'

def test_rgb_to_rgb_string(rgb):
    assert color_funcs.rgb_to_rgb_string(rgb) == 'rgb(1.000,0.250,0.500)'

def test_rgb_to_hsv_string(rgb):
    assert color_funcs.rgb_to_hsv_string(rgb) == 'hsv(0.944,0.750,1.000)'

def test_rgb_to_hls_string(rgb):
    assert color_funcs.rgb_to_hls_string(rgb) == 'hls(0.944,0.625,1.000)'

def test_hex_string_to_rgb(rgb):
    assert all([abs(i - j) < 0.005 for i, j in zip(color_funcs.hex_string_to_rgb('#ff3f7f'), rgb)])
