# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""Implements a color wheel with an outer ring to select a hue and a
triangle within that where saturation and value can be selected
"""

from __future__ import print_function, division, absolute_import
import sys
import colorsys
from math import pi, degrees, radians, atan2, floor, pow, fabs, cos, sin

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import ttk
else:
    import Tkinter as tk
    import ttk

from PIL import Image, ImageTk

import tks.colors

DEFAULT_RADIUS = 125


class ColorWheel(ttk.Frame, object):
    """Displays an HSV color wheel."""

    def __init__(self, master,
                 variable=None,
                 radius=DEFAULT_RADIUS):
        super(ColorWheel, self).__init__(master, style='tks.TFrame')

        self._hue_degrees = 0.0

        if variable is not None:
            self.color_var = variable
            self._variable = variable.get()
            self._hsv = colorsys.rgb_to_hsv(*self._variable)
        else:
            # Start with Red
            self.color_var = tks.colors.ColorVar()
            self._variable = (1.0, 0.0, 0.0)
            self._hsv = (0.0, 1.0, 1.0)
            self.color_var.set(self._variable)

        self.color_var.trace_variable('w', self._color_var_changed)

        self._hue_to_rgb_map = []
        self._create_hue_to_rgb_map()
        self._calculate_radii(radius)
        self._center = radius + 1

        self._canvas = tk.Canvas(self,
                                 width=radius * 2 + 1,
                                 height=radius * 2 + 1)
        self._canvas.grid(row=0, column=0)
        self._canvas.bind('<Button-1>', self._canvas_clicked)

        self._create_wheel(radius)
        self._create_triangle()
        self._hue_create_selection()
        self._sv_create_selection()

        self._internal_color_change = False
        self._color_var_changed()

        self.columnconfigure(0, weight=0, minsize=radius * 2 + 1)

    @property
    def hue(self):
        return self._hsv[0]

    @hue.setter
    def hue(self, value):
        if value < 0.0 or value > 1.0:
            raise ValueError('Hue value must be between 0.0 and 1.0')

        hsv = (value, self._hsv[1], self._hsv[2])
        rgb = colorsys.hsv_to_rgb(*hsv)
        self.color_var.set(rgb)

        self._hue_degrees = int(value * 359)
        self._hue_update_selection()

    @property
    def saturation(self):
        return self._hsv[1]

    @saturation.setter
    def saturation(self, value):
        if value < 0.0 or value > 1.0:
            raise ValueError('Saturation must be between 0.0 and 1.0')

        self._hsv = (self._hsv[0], value, self._hsv[2])
        rgb = colorsys.hsv_to_rgb(*self._hsv)
        self.color_var.set(rgb)

    @property
    def value(self):
        return self._hsv[2]

    @value.setter
    def value(self, value):
        if value < 0.0 or value > 1.0:
            raise ValueError('Value must be between 0.0 and 1.0')

        self._hsv = (self._hsv[0], self._hsv[1], value)
        rgb = colorsys.hsv_to_rgb(*self._hsv)
        self.color_var.set(rgb)

    def _color_var_changed(self, *args):
        """Respond to changes in the color variable."""

        self._variable = self.color_var.get()
        self._hsv = colorsys.rgb_to_hsv(*self._variable)
        angle = int(self._hsv[0] * 359.0)
        if not self._internal_color_change:
            if angle != self._hue_degrees:
                self._hue_degrees = angle
                self._hue_update_selection()
                self._update_triangle()
                self._update_triangle_image()
        self._internal_color_change = False

        s = self._hsv[1]
        v = self._hsv[2]
        hx, hy, sx, sy, vx, vy = self._triangle_vertices(self._hue_degrees,
                                                         self._center)
        x = floor(sx + (vx - sx) * v + (hx - vx) * s * v + 0.5)
        y = floor(sy + (vy - sy) * v + (hy - vy) * s * v + 0.5)

        self._sv_update_selection(x, y)

    def _create_hue_to_rgb_map(self):
        """Create a pre-calculated array of angle to hue mappings."""

        for angle in range(360):
            c = colorsys.hsv_to_rgb(radians(angle) / (2 * pi), 1.0, 1.0)
            self._hue_to_rgb_map.append(c)

    def _calculate_radii(self, radius):
        """Calculate the radii we need."""

        self._outer_radius = radius
        self._outer_radius2 = pow(self._outer_radius, 2)

        self._inner_radius = int(self._outer_radius - \
                                       (self._outer_radius / 4))
        self._inner_radius2 = pow(self._inner_radius, 2)

        self._triangle_radius = self._inner_radius - 6
        self._triangle_radius2 = self._triangle_radius * self._triangle_radius

        self._hue_radius = (self._outer_radius + \
                            self._inner_radius) / 2
        self._selection_radius = 3

    def _create_wheel(self, radius):
        """Create the color wheel."""

        stride = (self._outer_radius * 2) + 1
        ring_buf_size = stride * stride * 4
        ring_data = bytearray(ring_buf_size)

        # -radius + 0 + radius
        points = range(-self._outer_radius, self._outer_radius + 1)
        for y in points:
            for x in points:
                r2 = (x * x) + (y * y)

                offset = (((self._outer_radius + y) * stride) + \
                          (self._outer_radius + x)) * 4

                if r2 < self._outer_radius2 and r2 > self._inner_radius2:
                    angle = int(degrees(atan2(y, x))) % 360
                    c = self._hue_to_rgb_map[angle]
                    ring_data[offset] = int(255 * c[0])
                    ring_data[offset + 1] = int(255 * c[1])
                    ring_data[offset + 2] = int(255 * c[2])
                    ring_data[offset + 3] = 255
                else:
                    ring_data[offset] = 0
                    ring_data[offset + 1] = 0
                    ring_data[offset + 2] = 0
                    ring_data[offset + 3] = 0

        self._wheel = Image.frombytes('RGBA',
                                      (stride, stride),
                                      bytes(ring_data),
                                      'raw', 'RGBA', 0, -1)

        self._wheel_photoimage = ImageTk.PhotoImage(image=self._wheel)
        self._wheel_photoimage.image_reference = self._wheel_photoimage
        self._canvas.create_image((self._center + 1, self._center + 1),
                                  image=self._wheel_photoimage,
                                  tags='wheel')

    def _create_triangle(self):
        """Create the saturation/value triangle that is displayed in the wheel."""

        stride = (self._triangle_radius * 2) + 1
        buf_size = stride * stride * 4
        self._triangle_data = bytearray(source=buf_size)
        self._triangle_back_buffer = bytearray(source=buf_size)

        self._update_triangle()

        self._triangle = Image.frombuffer('RGBA',
                                          (stride, stride),
                                          self._triangle_data,
                                          'raw', 'RGBA', 0, 1)

        self._triangle_photoimage = ImageTk.PhotoImage(image=self._triangle)
        self._triangle_photoimage.image_reference = self._triangle_photoimage
        self._canvas.create_image((self._center, self._center),
                                  image=self._triangle_photoimage,
                                  tags='triangle')

    def _canvas_clicked(self, event):
        """Respond to a click on the canvas by determining if the click is
        within the outer wheel or the triangle.
        """

        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)

        xdist = (x - self._center)
        ydist = (y - self._center)
        r2 = (xdist * xdist) + (ydist * ydist)

        if r2 < self._outer_radius2 and r2 > self._inner_radius2:
            self._hue_degrees = int(degrees(atan2(-ydist, xdist)) % 359)
            # print(self._hue_degrees)

            self._hue_update_selection()
            self._update_triangle()
            self._update_triangle_image()

            rgb = colorsys.hsv_to_rgb(self._hue_degrees / 359.0, 1.0, 1.0)
            vertices = self._triangle_vertices(self._hue_degrees, self._center)
            self._sv_update_selection(vertices[0], vertices[1])
            self.color_var.set(rgb)
        elif r2 < self._triangle_radius2:
            if self._in_triangle(x, y):
                self._sv_update_selection(x, y)
                rgb = self.color_var.get()
                hsv = colorsys.rgb_to_hsv(*rgb)
                s, v = self._sv_calc_from_position(x, y)
                rgb = colorsys.hsv_to_rgb(hsv[0], s, v)

                self._internal_color_change = True
                self.color_var.set(rgb)

    def _update_triangle(self):
        """Update the triangle for the new hue."""

        hx, hy, sx, sy, vx, vy = \
            self._triangle_vertices(self._hue_degrees,
                                    self._triangle_radius)

        r1, g1, b1 = colorsys.hsv_to_rgb(self._hue_degrees / 359.0,
                                         1.0, 1.0)
        r2, g2, b2 = (0.0, 0.0, 0.0)
        r3, g3, b3 = (1.0, 1.0, 1.0)

        if sy > vy:
            sx, vx = vx, sx
            sy, vy = vy, sy
            r2, r3 = r3, r2
            g2, g3 = g3, g2
            b2, b3 = b3, b2

        if hy > vy:
            hx, vx = vx, hx
            hy, vy = vy, hy
            r1, r3 = r3, r1
            g1, g3 = g3, g1
            b1, b3 = b3, b1

        if hy > sy:
            hx, sx = sx, hx
            hy, sy = sy, hy
            r1, r2 = r2, r1
            g1, g2 = g2, g1
            b1, b2 = b2, b1

        stride = (self._triangle_radius * 2) + 1
        for y in range(stride):
            offset = y * stride * 4

            if y < hy or y > vy:
                for x in range(stride):
                    self._triangle_back_buffer[offset] = 0
                    self._triangle_back_buffer[offset + 1] = 0
                    self._triangle_back_buffer[offset + 2] = 0
                    self._triangle_back_buffer[offset + 3] = 0
                    offset += 4
            else:
                if y < sy:
                    xl = linear_interpolate(hx, sx, hy, sy, y)
                    rl = linear_interpolate(r1, r2, hy, sy, y)
                    gl = linear_interpolate(g1, g2, hy, sy, y)
                    bl = linear_interpolate(b1, b2, hy, sy, y)
                else:
                    xl = linear_interpolate(sx, vx, sy, vy, y)
                    rl = linear_interpolate(r2, r3, sy, vy, y)
                    gl = linear_interpolate(g2, g3, sy, vy, y)
                    bl = linear_interpolate(b2, b3, sy, vy, y)

                xr = linear_interpolate(hx, vx, hy, vy, y)

                rr = linear_interpolate(r1, r3, hy, vy, y)
                gr = linear_interpolate(g1, g3, hy, vy, y)
                br = linear_interpolate(b1, b3, hy, vy, y)

                if xl > xr:
                    xl, xr = xr, xl
                    rl, rr = rr, rl
                    gl, gr = gr, gl
                    bl, br = br, bl

                for x in range(stride):
                    if x < xl or x > xr:
                        self._triangle_back_buffer[offset] = 0
                        self._triangle_back_buffer[offset + 1] = 0
                        self._triangle_back_buffer[offset + 2] = 0
                        self._triangle_back_buffer[offset + 3] = 0
                        offset += 4
                    else:
                        r = int(linear_interpolate(rl, rr, xl, xr, x) * 255)
                        g = int(linear_interpolate(gl, gr, xl, xr, x) * 255)
                        b = int(linear_interpolate(bl, br, xl, xr, x) * 255)
                        self._triangle_back_buffer[offset] = r
                        self._triangle_back_buffer[offset + 1] = g
                        self._triangle_back_buffer[offset + 2] = b
                        self._triangle_back_buffer[offset + 3] = 255
                        offset += 4

        self._triangle_data[:] = self._triangle_back_buffer

    def _update_triangle_image(self):
        """Create a new PhotoImage for the updated triangle."""

        del self._triangle_photoimage
        self._triangle_photoimage = ImageTk.PhotoImage(image=self._triangle)
        self._triangle_photoimage.image_reference = self._triangle_photoimage
        self._canvas.itemconfigure('triangle', image=self._triangle_photoimage)

    def _triangle_vertices(self, angle, center=0):
        """Calculate the vertices of the triangle."""

        angle = radians(self._hue_degrees)
        hx = floor(center + 0.5 + (cos(angle) * self._triangle_radius))
        hy = floor(center + 0.5 - (sin(angle) * self._triangle_radius))
        sx = floor(center + 0.5 + (cos(angle + (2.0 * pi / 3.0)) * self._triangle_radius))
        sy = floor(center + 0.5 - (sin(angle + (2.0 * pi / 3.0)) * self._triangle_radius))
        vx = floor(center + 0.5 + (cos(angle + (4.0 * pi / 3.0)) * self._triangle_radius))
        vy = floor(center + 0.5 - (sin(angle + (4.0 * pi / 3.0)) * self._triangle_radius))

        return hx, hy, sx, sy, vx, vy

    def _in_triangle(self, x, y):
        """Determine if point x,y is within the triangle."""

        hx, hy, sx, sy, vx, vy = \
            self._triangle_vertices(self._hue_degrees, self._center)

        det = (vx - sx) * (hy - sy) - (vy - sy) * (hx - sx)
        s = ((x - sx) * (hy - sy) - (y - sy) * (hx - sx)) / det
        v = ((vx - sx) * (y - sy) - (vy - sy) * (x - sx)) / det

        is_in = s >= 0.0 and v >= 0.0 and s + v <= 1.0
        return is_in

    def _hue_create_selection(self):
        """Create the circular hue selection indicator."""

        self._hue_x, self._hue_y = self._hue_selection_pos()

        rect = (self._hue_x - self._selection_radius,
                self._hue_y - self._selection_radius,
                self._hue_x + self._selection_radius,
                self._hue_y + self._selection_radius)

        self._canvas.create_oval(rect,
                                 width='1.0',
                                 outline='#fafafa',
                                 fill='black',
                                 tags='hue')

    def _hue_update_selection(self):
        """Update the hue selection indicator"""

        pos = self._hue_selection_pos()
        offset_x = pos[0] - self._hue_x
        offset_y = pos[1] - self._hue_y

        self._canvas.move('hue', offset_x, offset_y)

        self._hue_x = pos[0]
        self._hue_y = pos[1]

    def _hue_selection_pos(self):
        """Calculate the hue selection indicator position"""

        angle = radians(self._hue_degrees)
        hx = floor(self._center + 0.5 + (cos(angle) * self._hue_radius))
        hy = floor(self._center + 0.5 - (sin(angle) * self._hue_radius))

        return hx, hy

    def _sv_create_selection(self):
        """Create the circular saturation/value selection indicator."""

        # based on starting at 0 degree angle
        angle = radians(self._hue_degrees)
        self._sv_selection_x = self._center + (cos(angle) * self._triangle_radius)
        self._sv_selection_y = self._center

        rect = (self._sv_selection_x - self._selection_radius,
                self._sv_selection_y - self._selection_radius,
                self._sv_selection_x + self._selection_radius,
                self._sv_selection_y + self._selection_radius)

        self._canvas.create_oval(rect,
                                 width='1.0',
                                 outline='#fafafa',
                                 fill='black',
                                 tags='sv')


    def _sv_update_selection(self, x, y):
        """Update the saturation/value selection indicator"""

        offset_x = x - self._sv_selection_x
        offset_y = y - self._sv_selection_y

        self._canvas.move('sv', offset_x, offset_y)
        self._sv_selection_x = x
        self._sv_selection_y = y

    def _sv_calc_from_position(self, x, y):
        """Calculate the saturation and value at position x,y"""

        hx, hy, sx, sy, vx, vy = \
            self._triangle_vertices(self._hue_degrees, 0)

        x = x - self._center
        y = y - self._center

        if vx * (x - sx) + vy * (y - sy) < 0.0:
            s = 1.0
            v = (((x - sx) * (hx - sx) + (y - sy) * (hy - sy)) / \
                 ((hx - sx) * (hx - sx) + (hy - sy) * (hy - sy)))
            if v < 0.0:
                v = 0.0
            elif v > 1.0:
                v = 1.0

        elif hx * (x - sx) + hy * (y - sy) < 0.0:
            s = 0.0
            v = (((x - sx) * (vx - sx) + (y - sy) * (vy - sy)) / \
                 ((vx - sx) * (vx - sx) + (vy - sy) * (vy - sy)))
            if v < 0.0:
                v = 0.0
            elif v > 1.0:
                v = 1.0

        elif sx * (x - hx) + sy * (y - hy) < 0.0:
            v = 1.0
            s = (((x - vx) * (hx - vx) + (y - vy) * (hy - vy)) / \
                 ((hx - vx) * (hx - vx) + (hy - vy) * (hy - vy)))
            if s < 0.0:
                s = 0.0
            elif s > 1.0:
                s = 1.0
        else:
            v = (((x - sx) * (hy - vy) - (y - sy) * (hx - vx)) / \
                 ((vx - sx) * (hy - vy) - (vy - sy) * (hx - vx)))
            if v <= 0.0:
                v = 0.0
                s = 0.0
            else:
                if v > 1.0:
                    v = 1.0

                if (fabs(hy - vy) < fabs(hx - vx)):
                    s = (x - sx - v * (vx - sx)) / (v * (hx - vx))
                else:
                    s = (y - sy - v * (vy - sy)) / (v * (hy - vy))

                if s < 0.0:
                    s = 0.0
                elif s > 1.0:
                    s = 1.0

        return s, v


def linear_interpolate(a, b, v1, v2, i):
    """Linear interpolation"""

    if v1 == v2:
        return a
    else:
        return a + (b - a) * (i - v1) / (v2 - v1)
