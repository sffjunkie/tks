# Copyright 2009-2014, Simon Kennedy, code@sffjunkie.co.uk

from __future__ import print_function, division, absolute_import
import re
import math
import colorsys
from io import StringIO
from pkgutil import get_data

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    from tkinter import ttk
except ImportError:
    import ttk

try:
    from tkinter import font
except ImportError:
    import tkFont as font

from tks.color_var import ColorVar
from tks.color_funcs import rgb_to_hex_string, hex_string_to_rgb


def rgb_to_hsv(color):
    return colorsys.rgb_to_hsv(*color)


def rgb_to_hls(color):
    return colorsys.rgb_to_hls(*color)


def rgb_to_yiq(color):
    return colorsys.rgb_to_yiq(*color)


def rgb_to_intensity(key):
    return key[0] * 0.299 + key[1] * 0.587 + key[2] * 0.114


def contrast_color(rgb):
    if rgb == (0.0, 0.0, 0.0) or rgb_to_intensity(rgb) < (160.0 / 255.0):
        return 'white'
    else:
        return 'black'


def hsv_key_func(key):
    return rgb_to_hsv(key[0])


def hls_key_func(key):
    return rgb_to_hls(key[0])


def yiq_key_func(key):
    return rgb_to_yiq(key[0])


def intensity_key_func(key):
    return rgb_to_intensity(key[0])


def name_key_func(key):
    return str(key[1].display_name).lower()


class ColorInfo():
    def __init__(self, display_name, names=[]):
        self.display_name = display_name
        self.color_names = names


class PaletteSelector(ttk.Frame, object):
    def __init__(self, master,
                 variable=None,
                 height=400):
        super(PaletteSelector, self).__init__(master, style='tks.TFrame')

        if variable is not None:
            self._color_var = variable
        else:
            self._color_var = ColorVar()
        
        x11_colors = ColorDatabase('x11.txt', read_only=True)
        css3_colors = ColorDatabase('css3.txt', read_only=True)
        
        self._color_databases = {
            'X11': x11_colors,
            'CSS3': css3_colors
        }

        db = 'X11'        
        self._current_database = self._color_databases[db]
        self._current_database_var = tk.StringVar(value=db)
        
        header_frame = ttk.Frame(self, style='tks.TFrame')
        l = ttk.Label(header_frame, text='Palette:', anchor=tk.W)
        l.grid(row=0, column=0, padx=(4, 4))
        
        c = ttk.Combobox(header_frame, width=5,
                         textvariable=self._current_database_var)
        c['values'] = sorted(self._color_databases.keys())
        c.grid(row=0, column=1, padx=(0, 4))
        c.bind('<<ComboboxSelected>>', self._change_database)
        
        l = ttk.Label(header_frame, text='Sort By:', anchor=tk.W)
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
            
        f = font.Font(font=('TkTextFont',))
        max_name_len = 0
        for color_db in self._color_databases.values():
            max_name_len = max(max_name_len, color_db.color_name_len_for_font(f))
        
        max_canvas_width = 700
        self._canvas_visible_height = height

        self._color_width = (max_name_len + 30)
        self._column_count = math.floor(max_canvas_width / self._color_width)
        self._canvas_width = self._column_count * self._color_width
        
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
            self._canvas.yview_scroll(int(-event.delta / 30), 'units')
        
        # Mouse wheel for Windows first then other systems.
        self._canvas.bind('<MouseWheel>', _mouse_wheel)
        self._canvas.bind('<Button-4>', _mouse_wheel)
        self._canvas.bind('<Button-5>', _mouse_wheel)
        
        self.rowconfigure(1, weight=1)
        #self.columnconfigure(0, weight=1)

        self._selected_rct_tag = ''
        self._key_func = hsv_key_func
        self._change_database(init=True)
        self._canvas.tag_bind('color', '<Button-1>', self._color_selected)
        
        for key in ['<Up>', '<Down>', '<Left>', '<Right>', '<Home>', '<End>']:
            master.bind(key, self._keysym_press)
        
        if variable is None:
            self._select_entry('rct001')
    
    def _change_database(self, event=None, init=False):
        db_name = self._current_database_var.get()
        self._current_database = self._color_databases[db_name]

        row = 0
        col = 0

        self._canvas.delete('color')
        for idx, (key, ci) in enumerate(sorted(self._current_database.items(),
                                               key=self._key_func)):
            rect = (col * self._color_width + 1,
                    row * self._color_height + 1,
                    (col * self._color_width) + self._color_width - 1,
                    (row * self._color_height) + self._color_height - 1)

            text_pos = ((col * self._color_width + 1) + (self._color_width / 2),
                    (row * self._color_height + 1) + (self._color_height / 2))
            
            rct_tag = 'rct%03d' % (idx + 1)
            tags = (str(key), rct_tag, 'color')
            rgb_hex = rgb_to_hex_string(key)
            self._canvas.create_rectangle(rect,
                                          fill=rgb_hex,
                                          width='1.0',
                                          outline=rgb_hex,
                                          tags=tags)
                                               
            text_color = contrast_color(key)
            txt_tag = 'txt%03d' % (idx + 1)
            tags = (str(key), txt_tag, 'color')
            self._canvas.create_text(text_pos,
                                     text=ci.display_name,
                                     fill=text_color,
                                     anchor='center',
                                     tags=tags)
                                          
            col += 1
            if col == self._column_count:
                row += 1
                col = 0
        
        self._canvas.update_idletasks()
        
        color_count = len(self._current_database)
        self._canvas_height = self._color_height * \
            math.ceil(color_count / self._column_count)
        scrollregion=(0, 0, self._canvas_width,
                      self._canvas_height)
        self._canvas.config(scrollregion=scrollregion)
        
        self._selected_rct_tag = ''
        
        if not init:
            self._select_entry('rct001')
            self._canvas.yview_moveto(0.0)

    def _change_sort(self, event=None):
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
            
        db_name = self._current_database_var.get()
        db = self._color_databases[db_name]
        for idx, (key, ci) in enumerate(sorted(db.items(),
                                               key=self._key_func)):
            rct_tag = 'rct%03d' % (idx + 1)
                    
            rgb_hex = rgb_to_hex_string(key)
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
                                       fill=contrast_color(key),
                                       text=ci.display_name)
        
        self._selected_rct_tag = ''
        self._select_entry('rct001')
        self._canvas.yview_moveto(0.0)
        self._sort_order = new_order
        
    def _color_selected(self, event=None):
        self._canvas.focus_set()
        
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)
        
        items = self._canvas.find_closest(x, y)
        tags = self._canvas.gettags(items[0])

        for tag in tags:
            if tag.startswith('rct') or tag.startswith('txt'):
                selected_tag = tag
        
        self._select_entry(selected_tag)

    def _keysym_press(self, *args, **kwargs):
        keysym = args[0].keysym
        db_length = len(self._current_database)
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
        tag = 'rct%s' % value[3:]
        old_tag = self._selected_rct_tag
        if tag != old_tag:
            if old_tag:
                old_rct_color = self._canvas.itemcget(old_tag, 'fill')
                self._canvas.itemconfigure(old_tag, outline=old_rct_color)
            
            rgb_hex = self._canvas.itemcget(tag, 'fill')
            color = hex_string_to_rgb(rgb_hex)
            #color = self._current_database.lookup_name(color_name)
            if color is None:
                color = (1.0, 1.0, 1.0)
            outline = contrast_color(color)
            self._canvas.itemconfigure(tag, outline=outline)
            
            self._selected_rct_tag = tag
            self._color_var.set(color)


class ColorDatabase(dict):
    def __init__(self, name, read_only=False):
        self._load_colors(name)
        self._read_only = read_only
        
    def find_closest(self, rgb):
        closest_color = None
        closest_distance = math.pow(10, 6)
        for key in self:
            distance2 = math.pow((rgb[0] - key[0])*255*0.3, 2) + \
                math.pow((rgb[1] - key[1])*255*0.59, 2) + \
                math.pow((rgb[2] - key[2])*255*0.11, 2)
            
            if distance2 < closest_distance:
                closest_color = key
                
        return closest_color
    
    def lookup_name(self, name):
        for key, ci in self.items():
            if name in ci.color_names:
                return key
        
        raise KeyError('Color name %s not in database.' % name)

    def color_info(self, rgb):
        color_name = self[rgb].color_names[0]
        hsv = rgb_to_hsv(rgb)
        yiq = rgb_to_yiq(rgb)
        hls = rgb_to_hls(rgb)
        
        hex_color = '#%02x%02x%02x' % tuple([int(x * 255) for x in rgb])
        
        return color_name, hsv, yiq, hls, hex_color

    def color_info_string(self, rgb):
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

    def color_name_len_for_font(self, f):
        max_name_len = 0
        for ci in self.values():
            name_len = f.measure(ci.display_name)
            
            if name_len > max_name_len:
                max_name_len = name_len
                
        return max_name_len
    
    def _load_colors(self, name):
        color_data = get_data('tks', name)
        color_info = StringIO(color_data.decode('ascii'))
        
        def color_lines():
            for line in color_info.readlines():
                if len(line) != 0 and line[0] != '!':
                    yield line
        
        for line in color_lines():
            line = line.strip(' \r\n')
            r, g, b, color_name = line.split(None, 3)
            
            color = tuple(map(lambda x: int(x) / 255.0, (r, g, b)))
            color_name = color_name.strip()

            display_name = self._build_display_name(color_name)
            if color not in self:
                # store [name, display name]
                self[color] = ColorInfo(display_name, [color_name]) 
            else:
                ci = self[color]

                if color_name not in ci.color_names:                
                    ci.color_names.append(color_name)
    
    def _build_display_name(self, color_name):
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
    
        m = re.match('([a-zA-Z\s]*)(\d+)$', color_name)
        if m:
            color_name = '%s %s' % m.groups()
    
        color_name = ' '.join([s.capitalize() for s in color_name.split()])
        return color_name
    