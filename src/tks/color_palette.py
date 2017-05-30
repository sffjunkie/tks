# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""A Tkinter widget to select colors from a palette of colors"""

from __future__ import (print_function, division, absolute_import,
                        unicode_literals)
import re
import sys
import math
import colorsys
from io import StringIO
from pkgutil import get_data

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import ttk
    from tkinter import font as tkf
else:
    import Tkinter as tk
    import ttk
    import tkFont as tkf

import tks.colors
import tks.color_funcs

from .i18n import language
_ = language.gettext


def hsv_key_func(key):
    """Key function to sort by the HSV value for a color"""

    return colorsys.rgb_to_hsv(*key[0])


def hls_key_func(key):
    """Key function to sort by the HLS value for a color"""

    return colorsys.rgb_to_hls(*key[0])


def yiq_key_func(key):
    """Key function to sort by the YIQ value for a color"""

    return colorsys.rgb_to_yiq(*key[0])


def intensity_key_func(key):
    """Key function to sort by intensity"""

    return tks.color_funcs.rgb_intensity(key[0])


def name_key_func(key):
    """Key function to sort by name"""

    return str(key[1].display_name).lower()


class ColorInfo(object):
    """A container for info about a specific color"""

    def __init__(self, display_name, names=None):
        self.display_name = display_name
        if names:
            self.color_names = names
        else:
            self.color_names = []


class PaletteSelector(ttk.Frame, object):
    """A widget to display a set of colors from a palette."""

    def __init__(self, master,
                 variable=None,
                 height=400):
        super(PaletteSelector, self).__init__(master, style='tks.TFrame')

        if variable is not None:
            self.color_var = variable
        else:
            self.color_var = tks.colors.ColorVar()

        x11_colors = Palette('x11.txt', read_only=True)
        css3_colors = Palette('css3.txt', read_only=True)

        self._color_databases = {
            'X11': x11_colors,
            'CSS3': css3_colors
        }

        palette_name = 'X11'
        self._current_palette = self._color_databases[palette_name]
        self._current_palette_var = tk.StringVar(value=palette_name)

        header_frame = ttk.Frame(self, style='tks.TFrame')
        l = ttk.Label(header_frame, text=_('Palette:'), anchor=tk.W)
        l.grid(row=0, column=0, padx=(4, 4))

        c = ttk.Combobox(header_frame, width=5,
                         textvariable=self._current_palette_var)
        c['values'] = sorted(self._color_databases.keys())
        c.grid(row=0, column=1, padx=(0, 4))
        c.bind('<<ComboboxSelected>>', self._change_palette)

        l = ttk.Label(header_frame, text=_('Sort By:'), anchor=tk.W)
        l.grid(row=0, column=2, padx=(4, 4))

        self._sort_order = 'HSV'
        self._sort_order_var = tk.StringVar()
        self._sort_order_var.set(self._sort_order)

        col = 3
        for idx, order in enumerate(['HSV', 'HLS', 'RGB', 'YIQ', 'Name']):
            btn = ttk.Radiobutton(header_frame, text=order,
                                  variable=self._sort_order_var, value=order,
                                  command=self._change_sort)
            btn.grid(row=0, column=col + idx, padx=4)

        header_frame.grid(row=0, column=0, sticky=(tk.N, tk.EW), columnspan=2)

        f = tkf.Font(font=('TkDefaultFont',))
        max_name_len = 0
        for color_db in self._color_databases.values():
            max_name_len = max(max_name_len,
                               color_db.color_name_len_for_font(f))

        max_canvas_width = 700
        self._canvas_visible_height = height

        self._color_width = (max_name_len + 30)
        self._column_count = math.floor(max_canvas_width / self._color_width)
        self._canvas_width = self._column_count * self._color_width
        self._canvas_height = -1

        self._color_height = f.metrics()['linespace'] + 16

        yscrollbar = tk.Scrollbar(self)
        yscrollbar.grid(row=1, column=1, sticky=tk.NS)

        self._canvas = tk.Canvas(self,
                                 width=self._canvas_width,
                                 height=self._canvas_visible_height,
                                 yscrollcommand=yscrollbar.set)
        self._canvas.grid(row=1, column=0, sticky=tk.NSEW)
        yscrollbar.config(command=self._canvas.yview)

        def _mouse_wheel(event):
            """Respond to the mouse scroll wheel"""

            self._canvas.yview_scroll(int(-event.delta / 30), 'units')

        # Mouse wheel for Windows first then other systems.
        self._canvas.bind('<MouseWheel>', _mouse_wheel)
        self._canvas.bind('<Button-4>', _mouse_wheel)
        self._canvas.bind('<Button-5>', _mouse_wheel)

        self.rowconfigure(1, weight=1)
        # self.columnconfigure(0, weight=1)

        self._selected_rct_tag = ''
        self._key_func = hsv_key_func
        self._change_palette(init=True)
        self._canvas.tag_bind('color', '<Button-1>', self._color_selected)

        for key in ['<Up>', '<Down>', '<Left>', '<Right>', '<Home>', '<End>']:
            master.bind(key, self._keysym_press)

        if variable is None:
            self._select_entry('rct001')

    def _change_palette(self, event=None, init=False):
        """Change to another color database"""

        db_name = self._current_palette_var.get()
        self._current_palette = self._color_databases[db_name]

        row = 0
        col = 0

        self._canvas.delete('color')
        sorted_items = sorted(self._current_palette.items(), key=self._key_func)
        for idx, (key, color_info) in enumerate(sorted_items):
            rect = (col * self._color_width + 1,
                    row * self._color_height + 1,
                    (col * self._color_width) + self._color_width - 1,
                    (row * self._color_height) + self._color_height - 1)

            text_pos = ((col * self._color_width + 1) + \
                        (self._color_width / 2),
                        (row * self._color_height + 1) + \
                        (self._color_height / 2))

            rct_tag = 'rct%03d' % (idx + 1)
            tags = (str(key), rct_tag, 'color')
            rgb_hex = tks.color_funcs.rgb_to_hex_string(key)
            self._canvas.create_rectangle(rect,
                                          fill=rgb_hex,
                                          width='1.0',
                                          outline=rgb_hex,
                                          tags=tags)

            text_color = tks.color_funcs.contrast_color(key)
            txt_tag = 'txt%03d' % (idx + 1)
            tags = (str(key), txt_tag, 'color')
            self._canvas.create_text(text_pos,
                                     text=color_info.display_name,
                                     fill=text_color,
                                     anchor='center',
                                     tags=tags)

            col += 1
            if col == self._column_count:
                row += 1
                col = 0

        self._canvas.update_idletasks()

        color_count = len(self._current_palette)
        self._canvas_height = self._color_height * \
                              math.ceil(color_count / self._column_count)
        scrollregion = (0, 0, self._canvas_width,
                        self._canvas_height)
        self._canvas.config(scrollregion=scrollregion)

        self._selected_rct_tag = ''

        if not init:
            self._select_entry('rct001')
            self._canvas.yview_moveto(0.0)

    def _change_sort(self, event=None):
        """Change the color sort order"""

        new_order = self._sort_order_var.get()
        if new_order == self._sort_order:
            return

        if new_order == 'HSV':
            self._key_func = hsv_key_func
        elif new_order == 'HLS':
            self._key_func = hls_key_func
        elif new_order == 'RGB':
            self._key_func = intensity_key_func
        elif new_order == 'YIQ':
            self._key_func = yiq_key_func
        elif new_order == 'Name':
            self._key_func = name_key_func

        palette_name = self._current_palette_var.get()
        palette = self._color_databases[palette_name]
        for idx, (key, color_info) in enumerate(sorted(palette.items(),
                                                       key=self._key_func)):
            rct_tag = 'rct%03d' % (idx + 1)

            rgb_hex = tks.color_funcs.rgb_to_hex_string(key)
            self._canvas.itemconfigure(rct_tag,
                                       fill=rgb_hex,
                                       outline=rgb_hex)

            tags = self._canvas.gettags(rct_tag)
            for tag in tags:
                if tag[0] == '(':
                    self._canvas.dtag(rct_tag, tag)
                    self._canvas.addtag_withtag(str(key), rct_tag)
                    break

            txt_tag = 'txt%03d' % (idx + 1)

            tags = self._canvas.gettags(txt_tag)
            for tag in tags:
                if tag[0] == '(':
                    self._canvas.dtag(txt_tag, tag)
                    self._canvas.addtag_withtag(str(key), txt_tag)
                    break

            self._canvas.itemconfigure(txt_tag,
                                       fill=tks.color_funcs.contrast_color(key),
                                       text=color_info.display_name)

        self._selected_rct_tag = ''
        self._select_entry('rct001')
        self._canvas.yview_moveto(0.0)
        self._sort_order = new_order

    def _color_selected(self, event=None):
        """Color entry selected with the mouse"""

        self._canvas.focus_set()

        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)

        items = self._canvas.find_closest(x, y)
        tags = self._canvas.gettags(items[0])

        for tag in tags:
            if tag.startswith('rct') or tag.startswith('txt'):
                selected_tag = tag

        self._select_entry(selected_tag)

    def _keysym_press(self, *args):
        """Respond to the Home, End and arrow keys"""

        keysym = args[0].keysym
        db_length = len(self._current_palette)
        row_count = int(math.ceil(db_length / self._column_count))

        if keysym == 'Home' or self._selected_rct_tag == '':
            idx = 1
        elif keysym == 'End':
            idx = db_length
        else:
            idx = int(self._selected_rct_tag[3:])

            if keysym == 'Up' and idx >= self._column_count:
                idx -= self._column_count
            elif keysym == 'Down' and idx <= (row_count - 1) * self._column_count:
                idx += self._column_count
            elif keysym == 'Left' and idx != 1:
                idx -= 1
            elif keysym == 'Right' and idx < db_length:
                idx += 1

        tag = 'rct%03d' % idx

        tag_bbox = self._canvas.bbox(tag)
        visible_y = self._canvas.yview()
        visible_start_y = self._canvas_height * visible_y[0]
        visible_end_y = self._canvas_height * visible_y[1]

        if tag_bbox[1] < visible_start_y:
            visible_start_y = tag_bbox[1]
            move_to_y = visible_start_y / self._canvas_height
            self._canvas.yview_moveto(move_to_y)
        elif tag_bbox[3] >= visible_end_y:
            visible_end_y = tag_bbox[3]
            visible_start_y = visible_end_y - self._canvas_visible_height
            move_to_y = visible_start_y / self._canvas_height
            self._canvas.yview_moveto(move_to_y)

        self._select_entry(tag)

    def _select_entry(self, value):
        """Highlight a color entry"""

        tag = 'rct%s' % value[3:]
        old_tag = self._selected_rct_tag
        if tag != old_tag:
            if old_tag:
                old_rct_color = self._canvas.itemcget(old_tag, 'fill')
                self._canvas.itemconfigure(old_tag, outline=old_rct_color)

            rgb_hex = self._canvas.itemcget(tag, 'fill')
            color = tks.color_funcs.hex_string_to_rgb(rgb_hex)
            # color = self._current_palette.lookup_name(color_name)
            if color is None:
                color = (1.0, 1.0, 1.0)
            outline = tks.color_funcs.contrast_color(color)
            self._canvas.itemconfigure(tag, outline=outline)

            self._selected_rct_tag = tag
            self.color_var.set(color)


class Palette(dict):
    """A palette of colors."""

    def __init__(self, name, read_only=False):
        dict.__init__(self)
        self._read_only = False
        self._load_colors(name, read_only)

    def __setitem__(self, key, value):
        if self._read_only:
            raise TypeError(_('Unable to set item. '
                              'This database is read only'))

        return dict.__setitem__(self, key, value)

    def __delitem__(self, key, value):
        if self._read_only:
            raise TypeError(_('Unable to delete item. '
                              'This database is read only'))

        return dict.__setitem__(self, key, value)

    def find_closest(self, rgb):
        """Find a color in the database which is the closest match"""

        closest_color = None
        closest_distance = math.pow(10, 6)
        for key in self:
            distance2 = math.pow((rgb[0] - key[0]) * 255 * 0.3, 2) + \
                math.pow((rgb[1] - key[1]) * 255 * 0.59, 2) + \
                math.pow((rgb[2] - key[2]) * 255 * 0.11, 2)

            if distance2 < closest_distance:
                closest_color = key

        return closest_color

    def lookup_name(self, name):
        """Lookup a color name in the database"""

        for key, color_info in self.items():
            if name in color_info.color_names:
                return key

        raise KeyError(_('Color name %s not in database.') % name)

    def color_info(self, rgb):
        """Return a tuple of information about an RGB color"""

        color_name = self[rgb].color_names[0]
        hsv = colorsys.rgb_to_hsv(*rgb)
        yiq = colorsys.rgb_to_yiq(*rgb)
        hls = colorsys.rgb_to_hls(*rgb)

        hex_color = '#%02x%02x%02x' % tuple([int(x * 255) for x in rgb])

        return color_name, hsv, yiq, hls, hex_color

    def color_info_string(self, rgb):
        """Create an information line for an RGB color"""

        color_name, hsv, yiq, hls, hex_color = self.color_info(rgb)
        format_str = '(%.02f, %.02f, %.02f)'
        rgb_str = format_str % rgb
        hsv_str = format_str % hsv
        yiq_str = format_str % yiq
        hls_str = format_str % hls

        format_str = '%s: rgb%s, hsv%s, yiq%s, hls%s, hex=%s'
        info = format_str % (color_name,
                             rgb_str,
                             hsv_str,
                             yiq_str,
                             hls_str,
                             hex_color)
        return info

    def color_name_len_for_font(self, font_):
        """Return the size a color name will take up in the specified font."""

        max_name_len = 0
        for color_info in self.values():
            name_len = font_.measure(color_info.display_name)

            if name_len > max_name_len:
                max_name_len = name_len

        return max_name_len

    def _load_colors(self, name, read_only):
        """Load a database of colors"""

        color_data = get_data('tks', name)
        color_info = StringIO(color_data.decode('ascii'))

        def color_lines():
            """Yield the lines that are colors i.e. not a comment"""

            for line in color_info.readlines():
                if len(line) != 0 and line[0] != '!':
                    yield line

        for line in color_lines():
            line = line.strip(' \r\n')
            r, g, b, color_name = line.split(None, 3)

            color = tuple([int(x) / 255.0 for x in (r, g, b)])
            color_name = color_name.strip()

            display_name = self._build_display_name(color_name)
            if color not in self:
                # store [name, display name]
                self[color] = ColorInfo(display_name, [color_name])
            else:
                color_info = self[color]

                if color_name not in color_info.color_names:
                    color_info.color_names.append(color_name)

        self._read_only = read_only

    @staticmethod
    def _build_display_name(color_name):
        """Manipulate a color name so it displays more aesthetically."""

        split_with = ['light', 'dark', 'dim', 'medium',
                      'white', 'almond', 'peach', 'lemon', 'mint', 'blue',
                      'lavender', 'rose', 'slate', 'gray', 'grey', 'turquoise',
                      'cyan', 'green', 'olive', 'brown', 'red', 'salmon',
                      'orange', 'pink', 'violet', 'orchid', 'purple',
                      'turquoise']

        color_name = color_name.lower()
        for elem in split_with:
            if elem in color_name:
                color_name = color_name.replace(elem, ' %s ' % elem)

        re_match = re.match(r'([a-zA-Z\s]*)(\d+)$', color_name)
        if re_match:
            color_name = '%s %s' % re_match.groups()

        color_name = ' '.join([s.capitalize() for s in color_name.split()])
        return color_name
