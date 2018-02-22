# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

""":mod:`tks.dates` provides 4 classes to obtain a date from a user.

:class:`DateVar`
    A Tk variable which holds a date.

:class:`DateEntry`
    Displays entry boxes for year, month and day as well as a button to
    display a date selection dialog.

:class:`DateDialog`
    Displays a dialog window allowing the user to select a date.

:class:`DateSelector`
    A widget which contains the date selection machinery.
"""

from __future__ import print_function, division, absolute_import
import sys
import datetime
import calendar
from functools import partial

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import font as tkf
    from tkinter import ttk
else:
    import Tkinter as tk
    import tkFont as tkf
    import ttk

try:
    import babel
    import babel.dates
    import babel.numbers
except ImportError:
    babel = None

from tks.i18n import language
_ = language.gettext

import tks
import tks.dialog


class TargetShape():
    """How to draw the target round a date"""

    Square = 'square'
    Rectangle = 'rectangle'
    Circle = 'circle'


class DateVar(tks.PickleVar):
    """A Tkinter variable which holds a :class:`datetime.date`"""

    def __init__(self, master=None, value=None, name=None):
        if value is None:
            value = datetime.date.today()

        super(DateVar, self).__init__(master, value, name)


class DateEntry(ttk.Frame, object):
    """A date entry widget

    Creates a frame which contains entry boxes for Year, Month and Day and a
    button to display a date selection dialog.

    Dates will always consist of a 4 digit year and 2 digit months and days
    only the order and separator are determined by the `locale` parameter

    :param master:   The master frame
    :type master:    :class:`ttk.Frame`
    :param variable: The variable which hold the date to display in
                     the entry boxes.
    :type variable:  :class:`tks.dates.DateVar`
    :param locale:   Determines the order of the widgets in the entry.
                     Either a locale name e.g. 'en' or a babel Locale
                     instance. If :mod:`babel` is not installed ISO 8601
                     format will be used.
    :type locale:    str or :class:`babel.Locale <babel.core.Locale>`
    :param fonts:    Fonts to use.
    :type fonts:     :class:`~tks.DefaultFonts`
    """

    def __init__(self, master,
                 variable=None,
                 locale='en',
                 fonts=None):
        super(DateEntry, self).__init__(master)

        if variable:
            if not isinstance(variable, DateVar):
                raise ValueError('"variable" argument must be a DateVar')

            self._variable = variable
        else:
            self._variable = DateVar(value=datetime.date.today())

        if babel and locale:
            if not isinstance(locale, babel.Locale):
                locale = babel.Locale(locale)

            self._pattern = locale.date_formats['short'].pattern

            for ch in self._pattern:
                if ch.lower() not in ['d', 'm', 'y']:
                    separator = ch
                    break

            elems = self._pattern.split(separator)
            for idx, elem in enumerate(elems):
                if 'y' in elem:
                    year_column = idx
                elif 'M' in elem:
                    month_column = idx
                elif 'd' in elem:
                    day_column = idx
        else:
            year_column = 0
            month_column = 1
            day_column = 2
            separator = '-'
            self._pattern = 'yyyy-MM-dd'

        self._locale = locale

        if not fonts:
            fonts = tks.load_fonts()

        self.fonts = fonts

        self._year_var = tk.StringVar()
        self._month_var = tk.StringVar()
        self._day_var = tk.StringVar()

        self._year_entry = ttk.Entry(self,
                                     textvariable=self._year_var,
                                     width=4,
                                     font=self.fonts.text)
        self._year_entry.grid(row=0, column=year_column * 2)

        self._month_entry = ttk.Combobox(self,
                                         textvariable=self._month_var,
                                         width=3,
                                         font=self.fonts.text)
        self._month_entry['values'] = ['%02d' % (x + 1) for x in range(12)]
        self._month_entry.grid(row=0, column=month_column * 2)

        self._day_entry = ttk.Combobox(self,
                                       textvariable=self._day_var,
                                       width=3,
                                       font=self.fonts.text)
        self._day_entry.grid(row=0, column=day_column * 2)

        lbl = ttk.Label(self, text=separator, width=1)
        lbl.grid(row=0, column=1)

        lbl = ttk.Label(self, text=separator, width=1)
        lbl.grid(row=0, column=3)

        btn = ttk.Button(self, text=_('Select...'), command=self._select_date)
        btn.grid(row=0, column=5, sticky=tk.E, padx=(6, 0))

        for idx in range(5):
            self.columnconfigure(idx, weight=0)
        self.columnconfigure(5, weight=1)

        self._year_var.trace_variable('w', self._year_changed)
        self._month_var.trace_variable('w', self._month_changed)
        self._day_var.trace_variable('w', self._day_changed)

        self._variable.trace_variable('w', self._value_changed)

        self._time = None
        self._internal_value_change = True
        self.value = self._variable.get()

    @property
    def value(self):
        """The :class:`~datetime.date` represented by the entry."""

        d = self._variable.get()

        if self._time:
            d = d.replace(hour=self._time.hour,
                          minute=self._time.minute,
                          second=self._time.second)

        return d

    @value.setter
    def value(self, value):
        changed = False
        if value.year != self._year_var.get():
            self._year_var.set(value.year)
            changed = True

        if value.month != self._month_var.get():
            self._month_var.set('%02d' % value.month)
            changed = True

        if value.day != self._day_var.get():
            self._day_var.set('%02d' % value.day)
            changed = True

        if changed:
            self._update_day_values(value.year, value.month, value.day)

        if isinstance(value, datetime.datetime):
            self._time = value.time()
        else:
            self._time = None

        self._internal_value_change = True
        self._variable.set(value)

    def _update_day_values(self, year, month, day):
        """Update the day combo box with the correct values
        """
        dummy, days_in_month = calendar.monthrange(year, month)

        new_day = None
        if self._day_entry['values']:
            current_last_day = int(self._day_entry['values'][-1])
            if current_last_day > days_in_month and day > days_in_month:
                new_day = days_in_month

        self._day_entry['values'] = \
            ['%02d' % (x + 1) for x in range(days_in_month)]

        if new_day:
            self._day_var.set('%02d' % new_day)

    def _year_changed(self, *args):
        value = self._variable.get()
        new_date = datetime.date(year=int(self._year_var.get()),
                                 month=value.month,
                                 day=value.day)
        self.value = new_date

    def _month_changed(self, *args):
        value = self._variable.get()
        new_date = datetime.date(year=value.year,
                                 month=int(self._month_var.get()),
                                 day=value.day)
        self.value = new_date
        #self._update_day_values(self._year_var.get(),
        #                        self._month_var.get(),
        #                        self._day_var.get())

    def _day_changed(self, *args):
        value = self._variable.get()
        new_date = datetime.date(year=value.year,
                                 month=value.month,
                                 day=int(self._day_var.get()))
        self.value = new_date

    def _value_changed(self, *args):
        if not self._internal_value_change:
            self.value = self._variable.get()
        self._internal_value_change = False

    def _select_date(self):
        """Display the date selection dialog"""

        d = datetime.date(year=int(self._year_var.get()),
                          month=int(self._month_var.get()),
                          day=int(self._day_var.get()))

        dlg = DateDialog(self,
                         _('Select a Date...'),
                         start_date=d,
                         locale=self._locale,
                         fonts=self.fonts)
        self.wait_window(dlg)
        new_date = dlg.date
        if new_date != None:
            self.value = new_date


class DateDialog(tks.dialog.Dialog):
    """Display a dialog to obtain a date from the user

    :param master: The master frame
    :type master:  :class:`ttk.Frame`
    :param title:  Dialog title
    :type title:   str
    :param start_date: The date to display in the entry boxes or None for
                       today's date
    :type start_date:  :class:`datetime.date` or :class:`datetime.datetime`
    :param locale: Determines how today's name is displayed
                   Either a locale name e.g. 'en' or a babel Locale
                   instance. If :mod:`babel` is not installed ISO 8601
                   format will be used.
    :type locale:  str or :class:`babel.Locale <babel.core.Locale>`
    :param target_type: `TargetShape.Square`, `TargetShape.Rectangle` or
                        `TargetShape.Circle`
    :type target_type:  :class:`TargetShape`
    :param fonts: Font definitions to use
    :type fonts: :class:`~tks.DefaultFonts`
    :param colors:    Colors to use.
    :type colors:      :class:`~tks.DefaultColors`
    """

    def __init__(self, master, title,
                 start_date=None,
                 locale='en',
                 target_type=TargetShape.Circle,
                 fonts=None,
                 colors=None):
        super(DateDialog, self).__init__(master, title)

        self.date = None

        if not fonts:
            fonts = tks.load_fonts()

        if not colors:
            colors = tks.load_colors()

        if babel and not isinstance(locale, babel.Locale):
            locale = babel.Locale(locale)

        self.selector = DateSelector(self, start_date,
                                     locale=locale,
                                     target_type=target_type,
                                     fonts=fonts,
                                     colors=colors)
        self.deiconify()

        selector_size = self.selector.size
        # gi = tks.parse_geometry(self.winfo_geometry())
        # self.minsize(gi[0], gi[1])
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())
        self.resizable(width=False, height=False)

    def ok(self):
        """Called when the OK button is pressed"""

        self.date = self._selector.date

    def cancel(self):
        """Called when either the Escape key or the Cancel button is pressed"""


class DateSelector(ttk.Frame, object):
    """A date selection widget

    :param master: The master frame
    :type master:  :class:`ttk.Frame`
    :param start_date: The date to display in the entry boxes or None for
                       today's date
    :type start_date:  :class:`datetime.date` or :class:`datetime.datetime`
    :param locale: Determines how today's name is displayed
                   Either a locale name e.g. 'en' or a babel Locale
                   instance. If :mod:`babel` is not installed ISO 8601
                   format will be used.
    :type locale:  str or :class:`babel.Locale <babel.core.Locale>`
    :param target_type: `TargetShape.Square`, `TargetShape.Rectangle` or
                        `TargetShape.Circle`
    :type target_type:  :class:`TargetShape`
    :param fonts: Font definitions to use
    :type fonts: :class:`tks.DefaultFonts`
    :param colors:    Colors to use.
    :type colors:      :class:`~tks.DefaultColors`
    """

    def __init__(self, master,
                 start_date,
                 locale='en',
                 target_type=TargetShape.Circle,
                 fonts=None,
                 colors=None):
        self._master = master
        super(DateSelector, self).__init__(master, style='tks.TFrame')
        self._date = None

        if not fonts:
            fonts = tks.load_fonts()

        if not colors:
            colors = tks.load_colors()

        today = datetime.date.today()
        if babel:
            if not isinstance(locale, babel.Locale):
                locale = babel.Locale(locale)

            today_txt = babel.dates.format_date(today, 'long', locale)
        else:
            today_txt = today.strftime('%Y-%m-%d')

        ttk.Style().configure('Selector.tks.TButton',
                              font=fonts.text,
                              anchor=tk.CENTER)
        ttk.Style().configure('Selector.tks.TLabel',
                              font=fonts.text,
                              anchor=tk.CENTER)
        ttk.Style().configure('Month.Selector.tks.TButton',
                              padding=(0, 10))
        ttk.Style().configure('Year.Selector.tks.TButton',
                              padding=(0, 10))

        self._today_btn = ttk.Button(self, text=today_txt,
                                     width=len(today_txt) + 4,
                                     command=self._today_clicked)
        self._today_btn.grid(row=0, column=0, sticky=tk.N,
                             padx=3, pady=3)

        self._ds = DaySelector(self, start_date,
                               locale,
                               target_type=target_type,
                               fonts=fonts,
                               colors=colors)
        self._ds.grid(row=1, column=0, sticky=(tk.N, tk.EW), padx=3, pady=3)
        self._prev_selector = self._ds

        self._ms = MonthSelector(self, locale)
        self._ms.grid(row=1, column=0, sticky=(tk.N, tk.EW), padx=3, pady=3)
        self._ys = YearSelector(self)
        self._ys.grid(row=1, column=0, sticky=(tk.N, tk.EW), padx=3, pady=3)

        if start_date is None:
            self.date = today
        else:
            self.date = start_date

        self.columnconfigure(0, weight=1)
        self.grid(row=1, column=0)

        self.update_idletasks()
        self._ds_size = self._ds.winfo_reqwidth(), self._ds.winfo_reqheight()
        self._ms_size = self._ms.winfo_reqwidth(), self._ms.winfo_reqheight()
        self._ys_size = self._ys.winfo_reqwidth(), self._ys.winfo_reqheight()

        max_width = max(self._ds_size[0], self._ms_size[0], self._ys_size[0])
        max_height = max(self._ds_size[1], self._ms_size[1], self._ys_size[1])
        self.size = max_width, max_height

        self.tk.call("grid", "remove", self._ms)
        self.tk.call("grid", "remove", self._ys)

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value
        self._ds.date = value
        self._ms.date = value
        self._ys.date = value

    @property
    def year(self):
        return self.date.year

    @year.setter
    def year(self, value):
        self.date = datetime.date(value,
                                  self.date.month,
                                  self.date.day)

    @property
    def month(self):
        return self.date.month

    @month.setter
    def month(self, value):
        self.date = datetime.date(self.date.year,
                                  value,
                                  self.date.day)

    @property
    def day(self):
        return self.date.day

    @day.setter
    def day(self, value):
        self.date = datetime.date(self.date.year,
                                  self.date.month,
                                  value)

    def _today_clicked(self):
        self.date = datetime.date.today()
        self._ms.grid_forget()
        self._ys.grid_forget()
        self._ds.grid(row=1, column=0, sticky=(tk.N, tk.EW), padx=3, pady=3)

    def day_selected(self):
        self.date = self._ds.date

    def month_btn_clicked(self, event):
        self._prev_selector = self._ds
        self._ds.grid_forget()
        self.date = self.date
        self._ms.grid(row=1, column=0, sticky=(tk.N, tk.EW), padx=3, pady=3)

    def month_selected(self):
        self._ms.grid_forget()
        self.date = self._ms.date
        self._ds.grid(row=1, column=0, sticky=(tk.N, tk.EW), padx=3, pady=3)

    def year_btn_clicked(self, event):
        if event.widget.master.master == self._ds:
            self._prev_selector = self._ds
        else:
            self._prev_selector = self._ms

        self._prev_selector.grid_forget()
        self._ys.date = self.date
        self._ys.grid(row=1, column=0, sticky=(tk.N, tk.EW), padx=3, pady=3)

    def year_selected(self):
        self._ys.grid_forget()
        self.date = self._ys.date
        self._prev_selector.grid(row=1, column=0, sticky=(tk.N, tk.EW),
                                 padx=3, pady=3)

    def new_month_selected(self, date_):
        self._date = date_
        self._ms.date = date_
        self._ys.date = date_


class DaySelector(ttk.Frame, object):
    """A day selector widget which displays dates as a calendar, one
    month at a time.

    :param master: The master frame
    :type master: :class:`ttk.Frame`
    :param start_date: The start date to display in the entry boxes or None
                       for today's date
    :type start_date:  :class:`datetime.date` or :class:`datetime.datetime`
    :param locale:     The locale for example day names
    :type locale:      :class:`babel.Locale`
    :param target_type: Target type to select dates
    :type target_type: bool
    :param fonts: Fonts to use
    :type fonts: :class:`DefaultFonts`
    """

    def __init__(self, master,
                 start_date,
                 locale,
                 target_type=TargetShape.Circle,
                 fonts=None,
                 colors=None):
        self._master = master
        super(DaySelector, self).__init__(master, style='tks.TFrame')

        self._canvas_color = ttk.Style(master).lookup('tks.TFrame',
                                                      'background')

        if fonts:
            self.fonts = fonts
        else:
            self.fonts = tks.DefaultFonts()

        if colors:
            self.colors = colors
        else:
            self.colors = tks.DefaultColors()

        self.colors.today = '#eee'
        self.colors.other_month = '#888'

        if start_date is None:
            self._date = datetime.date.today()
        else:
            self._date = start_date

        if babel:
            if not isinstance(locale, babel.Locale):
                locale = babel.Locale(locale)

            self._first_week_day = locale.first_week_day
            self._days = locale.days['format']['abbreviated']
            self._months = locale.months['format']['wide']
            self._locale = locale
        else:
            self._first_week_day = calendar.MONDAY
            self._days = calendar.day_abbr
            self._months = calendar.month_name

        self._calendar = calendar.LocaleTextCalendar(self._first_week_day, '')

        self._selected_tgt = ''

        self._font = tkf.Font(font=fonts.text)
        family = self._font.actual('family')
        size = self._font.actual('size')
        self._font_bold = tkf.Font(font=(family, size, tkf.BOLD))

        self._header = ttk.Frame(self, padding=(3, 0), style='tks.TFrame')

        self._prev_btn = ttk.Button(self._header, text='<', width=2,
                                    command=self._prev_month,
                                    style='Selector.tks.TButton')
        self._prev_btn.grid(row=0, column=0, sticky=tk.W)

        self._month_btn = ttk.Button(self._header,
                                     style='Selector.tks.TButton')
        self._month_btn.grid(row=0, column=1, sticky=tk.EW, padx=(0, 2))
        self._month_btn.bind('<ButtonRelease-1>',
                             self._master.month_btn_clicked)

        self._year_btn = ttk.Button(self._header,
                                    style='Selector.tks.TButton')
        self._year_btn.grid(row=0, column=2, sticky=tk.EW, padx=(2, 0))
        self._year_btn.bind('<ButtonRelease-1>',
                            self._master.year_btn_clicked)

        self._next_btn = ttk.Button(self._header, text='>', width=2,
                                    command=self._next_month,
                                    style='Selector.tks.TButton')
        self._next_btn.grid(row=0, column=3, sticky=tk.W)

        self._header.columnconfigure(0, weight=0)
        self._header.columnconfigure(1, weight=1)
        self._header.columnconfigure(2, weight=1)
        self._header.columnconfigure(3, weight=0)
        self._header.grid(row=0, column=0, sticky=tk.EW)

        self._canvas = tk.Canvas(self, background=self._canvas_color)
        self._canvas.grid(row=1, column=0, columnspan=3, pady=(4, 0))
        self._create_canvas(target_type)

        self.columnconfigure(0, weight=1)

        self._today_tag = None
        self._update_canvas()
        self._fill_target()

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value
        self._update_canvas()

    def _create_canvas(self, target_type):
        days = []
        for idx in range(7):
            day_idx = (self._first_week_day + idx) % 7
            days.append(self._days[day_idx])

        font_info = tkf.Font(font=self._font)
        item_width = max(font_info.measure(day) for day in days) + 4
        linespace = font_info.metrics('linespace')
        item_height = linespace + 4

        if target_type == TargetShape.Circle:
            if babel:
                num = babel.numbers.format_number(99, self._locale)
            else:
                num = '99'

            circle_diameter = font_info.measure(num) * 2.25
            circle_radius = circle_diameter / 2.0
            item_width = item_height = max(item_width, item_height,
                                           circle_diameter)
        elif target_type == TargetShape.Square:
            item_width = item_height = max(item_width, item_height)

        x_stride = item_width + 6
        y_stride = item_height + 2

        half_width = int(item_width / 2)
        half_height = int(item_height / 2)
        x_start = (x_stride / 2)
        y_start = (y_stride / 2)

        x_pos = x_start
        y_pos = y_start

        rect_width = x_stride * 6.5
        self._canvas.create_rectangle(
            (x_start - half_width, y_start - half_height,
             x_start + rect_width, y_start + half_height),
            fill=self.colors.header,
            outline='')

        for day in days:
            self._canvas.create_text((x_pos, y_pos), text=day,
                                     font=self._font,
                                     anchor=tk.CENTER)
            x_pos = x_pos + x_stride

        y_pos += y_stride

        for week_number in range(6):
            x_pos = x_start
            for day_number in range(7):
                day_tag = 'day%d:%d' % (week_number, day_number)
                tgt_tag = 'tgt%d:%d' % (week_number, day_number)

                if target_type == TargetShape.Circle:
                    func = self._canvas.create_oval
                    rect = (x_pos - circle_radius,
                            y_pos - circle_radius,
                            x_pos + circle_radius,
                            y_pos + circle_radius)
                else:
                    func = self._canvas.create_rectangle
                    rect = (x_pos - half_width,
                            y_pos - half_height,
                            x_pos + half_width,
                            y_pos + half_height)

                func(rect,
                     outline='',
                     tags=(day_tag, tgt_tag))

                text_tag = 'txt%d:%d' % (week_number, day_number)
                self._canvas.create_text((x_pos, y_pos), text='0',
                                         tags=(day_tag, text_tag),
                                         font=self._font,
                                         anchor=tk.CENTER)

                self._canvas.tag_bind(day_tag, '<Button-1>', self._date_clicked)

                x_pos += x_stride
            y_pos += y_stride

        self._canvas.configure(width=x_pos - (x_stride / 2),
                               height=y_pos - (y_stride / 2))

    def _date_clicked(self, event):
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)

        items = self._canvas.find_closest(x, y)
        tags = self._canvas.gettags(items[0])

        for tag in tags:
            if tag.startswith('day'):
                break
        else:
            return

        txt_tag = 'txt%s' % tag[3:]
        tgt_tag = 'tgt%s' % tag[3:]

        if self._selected_tgt:
            self._canvas.itemconfig(self._selected_tgt,
                                    fill='')

        self._canvas.itemconfig(tgt_tag,
                                fill=self.colors.select)

        week_number, day_number = [int(x) for x in txt_tag[3:].split(':')]
        self._date = self._get_date(week_number, day_number)

        self._selected_tgt = tgt_tag

        self._master.day_selected()

    def _update_canvas(self):
        """Redraw the calendar"""

        month_txt = self._months[self._date.month]
        self._month_btn['text'] = '%s' % month_txt
        self._year_btn['text'] = '%s' % str(self._date.year)

        self._days = list(self._calendar.monthdatescalendar(self._date.year,
                                                            self._date.month))

        # We display 6 weeks of days but some months only have 5 weeks in
        # them this means the calendar doesn't have the required number of rows
        # so we add another
        if len(self._days) == 5:
            d = self._days[4][-1]
            delta = datetime.timedelta(days=1)

            missing_days = []
            for day_number in range(7):
                d += delta
                missing_days.append(d)

            self._days.append(missing_days)

        if self._selected_tgt:
            self._canvas.itemconfig(self._selected_tgt, fill='')

        for week_number, days_in_week in enumerate(self._days):
            for day_number, date_ in enumerate(days_in_week):
                txt_tag = 'txt%d:%d' % (week_number, day_number)

                if babel:
                    text = babel.numbers.format_number(date_.day, self._locale)
                else:
                    text = str(date_.day)

                if self._date.month == date_.month:
                    self._canvas.itemconfigure(txt_tag,
                                               text=text,
                                               fill='black',
                                               font=self._font)
                else:
                    self._canvas.itemconfigure(txt_tag,
                                               text=text,
                                               fill=self.colors.other_month)

                tgt_tag = 'tgt%s:%s' % (week_number, day_number)

                if self._selected_tgt and tgt_tag == self._selected_tgt:
                    self._canvas.itemconfig(self._selected_tgt, fill='')

                if date_ == self._date:
                    self._canvas.itemconfig(tgt_tag,
                                            fill=self.colors.select)
                    self._selected_tgt = tgt_tag

    def _next_month(self):
        self._date = next_month(self._date)
        self._master.new_month_selected(self._date)
        self._update_canvas()

    def _prev_month(self):
        self._date = prev_month(self._date)
        self._master.new_month_selected(self._date)
        self._update_canvas()

    def _select_today(self):
        self._date = datetime.date.today()
        self._update_canvas()

    def _get_date(self, week_number, day_number):
        return self._days[week_number][day_number]

    def _find_date_position(self, d):
        for week_number, week in enumerate(self._days):
            for day_number, day in enumerate(week):
                if day == d:
                    return (week_number, day_number)

    def _fill_target(self):
        tgt_tag = 'tgt%d:%d' % self._find_date_position(self._date)

        self._canvas.itemconfig(tgt_tag,
                                fill=self.colors.select)

        self._selected_tgt = tgt_tag


class MonthSelector(ttk.Frame, object):
    """
    :param calendar:   The locale calendar to use
    :type calendar:    :class:`calendar.LocaleTextCalendar
    """

    def __init__(self, master, locale):
        super(MonthSelector, self).__init__(master,
                                            style='Selector.tks.TFrame')

        self._master = master
        self._date = None

        if babel:
            if not isinstance(locale, babel.Locale):
                locale = babel.Locale(locale)

            self._months = locale.months['format']['wide']
        else:
            self._months = calendar.month_name


        self._prev_btn = ttk.Button(self, text='<', width=2,
                                    command=self._prev_year,
                                    style='Selector.tks.TButton')
        self._prev_btn.grid(row=0, column=0, sticky=tk.W, padx=(0, 4))

        self._year_btn = ttk.Button(self,
                                    style='Selector.tks.TButton')
        self._year_btn.grid(row=0, column=1, sticky=tk.EW)
        self._year_btn.bind('<ButtonRelease-1>',
                            self._master.year_btn_clicked)

        self._next_btn = ttk.Button(self, text='>', width=2,
                                    command=self._next_year,
                                    style='Selector.tks.TButton')
        self._next_btn.grid(row=0, column=2, sticky=tk.E, padx=(4, 0))

        btn_frame = ttk.Frame(self, style='tks.TFrame')
        self._buttons = []
        for y in range(4):
            for x in range(3):
                month = y * 3 + x + 1
                name = self._months[month]
                btn = ttk.Button(btn_frame, text=name,
                                 style='Month.Selector.tks.TButton',
                                 command=partial(self._btn_selected, month))

                self._buttons.append(btn)
                btn.grid(row=y, column=x, pady=(0, 4))

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=(4, 0),
                       sticky=tk.NSEW)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value
        self._update()

    def _update(self):
        self._year_btn['text'] = self._date.year
        for month in range(1, 13):
            if month == self.date.month:
                self._buttons[month - 1]['default'] = tk.ACTIVE
                self.bind('<space>', partial(self._btn_selected, month))
            else:
                self._buttons[month - 1]['default'] = tk.DISABLED

    def _prev_year(self):
        self.date = prev_year(self.date)

    def _next_year(self):
        self.date = next_year(self.date)

    def _btn_selected(self, month):
        self.date = set_month(self.date, month)
        self._master.month_selected()


class YearSelector(ttk.Frame, object):
    def __init__(self, master):
        self._master = master
        super(YearSelector, self).__init__(master, style='tks.TFrame')

        self._date = None
        self._prev_btn = ttk.Button(self, text='<', width=2,
                                    command=self._prev_decade,
                                    style='Selector.tks.TButton')
        self._prev_btn.grid(row=0, column=0, sticky=tk.W, padx=(0, 4))

        self._year_btn = ttk.Label(self,
                                   style='Selector.tks.TLabel')
        self._year_btn.grid(row=0, column=1, sticky=tk.EW)
        # self._year_btn.bind('<Button-1>', self.year_btn_clicked)

        self._next_btn = ttk.Button(self, text='>', width=2,
                                    command=self._next_decade,
                                    style='Selector.tks.TButton')
        self._next_btn.grid(row=0, column=2, sticky=tk.E, padx=(4, 0))

        btn_frame = ttk.Frame(self, style='tks.TFrame')
        self._buttons = []
        for y in range(4):
            for x in range(3):
                btn = ttk.Button(btn_frame, style='Year.Selector.tks.TButton')
                btn.grid(row=y, column=x, padx=1, pady=1)
                self._buttons.append(btn)

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=(4, 0),
                       sticky=tk.NSEW)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value
        self._update()

    def _update(self):
        year = self._date.year
        year_range = (year - 5, year + 6)
        self._year_btn['text'] = '%d - %d' % year_range

        year_in_range = False
        for idx, year in enumerate(range(year_range[0], year_range[1] + 1)):
            btn = self._buttons[idx]
            btn['text'] = '%d' % year
            btn['command'] = partial(self._btn_selected, year)

            if year == self._date.year:
                year_in_range = True
                btn['default'] = tk.ACTIVE
                self.bind('<space>', partial(self._btn_selected, year))
            else:
                btn['default'] = tk.DISABLED

        if not year_in_range:
            self.unbind('<space>')

    def _prev_decade(self):
        self.date = prev_decade(self.date)
        self._update()

    def _next_decade(self):
        self.date = next_decade(self.date)
        self._update()

    def _btn_selected(self, year):
        self.date = set_year(self.date, year)
        self._master.year_selected()


def set_month(d, month):
    try:
        return d.__class__(year=d.year, month=month, day=d.day)
    except ValueError:
        if d.month == 12:
            m = 1
            y = d.year + 1
        else:
            m = month + 1
            y = d.year

        return d.__class__(year=y, month=m, day=1) - \
            datetime.timedelta(days=1)


def set_year(d, year):
    try:
        return d.__class__(year=year, month=d.month, day=d.day)
    except ValueError:
        m = d.month + 1

        return d.__class__(year=year, month=m, day=1) - \
            datetime.timedelta(days=1)


def next_month(d):
    year = d.year
    month = d.month + 1
    if month > 12:
        year += 1
        month = 1

    try:
        return d.__class__(year=year, month=month, day=d.day)
    except ValueError:
        return d.__class__(year=year, month=month + 1, day=1) - \
            datetime.timedelta(days=1)


def prev_month(d):
    year = d.year
    month = d.month - 1
    if month == 0:
        year -= 1
        month = 12

    try:
        return d.__class__(year=year, month=month, day=d.day)
    except ValueError:
        return d.__class__(year=year, month=month + 1, day=1) - \
            datetime.timedelta(days=1)


def next_year(d, years=1):
    try:
        return d.__class__(year=d.year + years, month=d.month, day=d.day)
    except ValueError:
        return d.__class__(year=d.year + years, month=d.month + 1, day=1) - \
            datetime.timedelta(days=1)


def prev_year(d):
    return next_year(d, -1)


def next_decade(d):
    return next_year(d, 10)


def prev_decade(d):
    return next_year(d, -10)
