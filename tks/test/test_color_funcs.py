import py.test
from tks import color_funcs

@py.test.fixture
def rgb():
    return (1.0, 0.25, 0.50)

def test_rgb_to_hex_string(rgb):
    assert color_funcs.rgb_to_hex_string(rgb) == '#ff3f7f'

def test_rgb_to_rgb_string(rgb):
    assert color_funcs.rgb_to_rgb_string(rgb) == 'rgb(1.00,0.25,0.50)'

def test_rgb_to_hsv_string(rgb):
    assert color_funcs.rgb_to_hsv_string(rgb) == 'hsv(0.94,0.75,1.00)'

def test_rgb_to_hls_string(rgb):
    assert color_funcs.rgb_to_hls_string(rgb) == 'hls(0.94,0.62,1.00)'

def test_hex_string_to_rgb(rgb):
    assert color_funcs.hex_string_to_tuple('#ff3f7f') == rgb
    
    