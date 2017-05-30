# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

try:
    from itertools import izip as zip
except:
    pass

from operator import mul
from itertools import starmap

def mult(a, b):
    zip_b = zip(*b)
    return [[sum(ele_a * ele_b for ele_a, ele_b in zip(row_a, col_b))
             for col_b in zip_b] for row_a in a]

def dot(a, b):
    return sum(starmap(mul, zip(a, b)))

def transpose(a):
    return [list(i) for i in zip(*a)]

