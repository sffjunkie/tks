# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

""":mod:`tks.times`  provides 4 classes to obtain a time from a user.

:class:`TimeVar`
    A Tk variable which holds a time.

:class:`TimeEntry`
    Displays entry boxes for hours, minutes and optionally seconds and
    an AM/PM selector. Also contains a button to display a time
    selection dialog.

:class:`TimeDialog`
    Displays a dialog window allowing the user to select a time.

:class:`TimeSelector`
    A widget which contains the time selection machinery.
"""

from __future__ import print_function, division, absolute_import
import sys
import math
import datetime

if sys.version_info >= (3, 0):
    import tkinter as tk
    import tkinter.font as tkf
    import tkinter.ttk as ttk
else:
    import Tkinter as tk
    import tkFont as tkf
    import ttk

try:
    import babel
except ImportError:
    babel = None

from tks.i18n import language
_ = language.gettext

import tks
import tks.dialog

PADDING = 4
FACE_RADIUS = 150
MODE_NONE = 0
MODE_HOUR = 1
MODE_MINUTE = 2
MODE_SECOND = 3


class TimeVar(tks.PickleVar):
    """A Tkinter variable which holds a :class:`datetime.time`"""

    def __init__(self, master=None, value=None, name=None):
        if value is None:
            value = datetime.datetime.now().time()

        super(TimeVar, self).__init__(master, value, name)


class TimeEntry(ttk.Frame, object):
    """A time entry widget

    :param master:   The master frame
    :type master:    :class:`ttk.Frame`
    :param variable: The variable which hold the date to display in
                     the entry boxes.
    :type variable:  :class:`tks.times.TimeVar`
    :param locale:   Determines the widgets in the entry.
                     Either a locale name e.g. 'en' or a babel Locale instance.
                     If :mod:`babel` is not installed ISO 8601 format will be
                     used i.e. 24 hours (no am/pm) and ':' as a separator.
    :type locale:    str or :class:`babel.Locale <babel.core.Locale>`
    :param fonts:    Fonts to use
    :type fonts:     :class:`~tks.DefaultFonts`
    :param show_seconds: If True a seconds value can be entered.
    :type show_seconds:  bool
    """

    def __init__(self, master,
                 variable=None,
                 locale='en',
                 fonts=None,
                 show_seconds=False):
        super(TimeEntry, self).__init__(master)

        if variable:
            if not isinstance(variable, TimeVar):
                raise ValueError('"variable" argument must be a TimeVar')

            self._variable = variable
        else:
            self._variable = TimeVar()

        start_time = self._variable.get()

        if not fonts:
            fonts = tks.load_fonts()

        self.fonts = fonts

        self._ampm = None
        if babel and locale:
            if not isinstance(locale, babel.Locale):
                locale = babel.Locale(locale)

            pattern = locale.time_formats['short'].pattern

            for ch in pattern:
                ch = ch.lower()
                if ch not in ['h', 'm', 's', 'a', 'k']:
                    separator = ch
                    break

            if 'a' in pattern:
                s = babel.dates.format_time(start_time,
                                            format='a', locale=locale)
                if 'am' in s or 'pm' in s:
                    self._ampm = ('am', 'pm')
                elif 'AM' in s or 'PM' in s:
                    self._ampm = ('AM', 'PM')
        else:
            separator = ':'

        self._locale = locale

        self._hour_var = tk.IntVar()
        self._minute_var = tk.IntVar()
        if show_seconds:
            self._second_var = tk.IntVar()

        self._hour_entry = ttk.Combobox(self,
                                        textvariable=self._hour_var,
                                        width=3,
                                        font=self.fonts.text)

        if self._ampm is None:
            hour_values = ['%02d' % x for x in range(1, 24)]
            hour_values.append('00')
        else:
            hour_values = ['%02d' % x for x in range(1, 13)]

        self._hour_entry['values'] = hour_values

        #self._hour_var.set(start_time.hour)
        self._hour_entry.grid(row=0, column=0)

        l = ttk.Label(self, text=separator, width=1, justify=tk.CENTER,
                      font=self.fonts.text)
        l.grid(row=0, column=1)

        self._minute_entry = ttk.Combobox(self,
                                          textvariable=self._minute_var,
                                          width=3)
        self._minute_entry['values'] = ['%02d' % x for x in range(60)]
        self._minute_entry.grid(row=0, column=2)

        self._show_seconds = show_seconds
        if self._show_seconds:
            l = ttk.Label(self, text=separator, width=1, justify=tk.CENTER)
            l.grid(row=0, column=3)

            self._second_entry = ttk.Combobox(self,
                                              textvariable=self._second_var,
                                              width=3)
            self._second_entry['values'] = ['%02d' % x for x in range(60)]
            self._second_entry.grid(row=0, column=4)

        if self._ampm:
            self._ampm_var = tk.StringVar()

            am = ttk.Radiobutton(self, text=self._ampm[0],
                                 variable=self._ampm_var,
                                 value='am')
            am.grid(row=0, column=5)
            pm = ttk.Radiobutton(self, text=self._ampm[1],
                                 variable=self._ampm_var,
                                 value='pm')
            pm.grid(row=0, column=6)

            if self._hour_var.get() > 12:
                ampm_value = self._ampm[0].lower()
            else:
                ampm_value = self._ampm[1].lower()

            self._ampm_var.set(ampm_value)

        btn = ttk.Button(self, text='Select...', command=self._select_time)
        btn.grid(row=0, column=7, sticky=tk.E, padx=(6, 0))

        for idx in range(7):
            self.columnconfigure(idx, weight=0)
        self.columnconfigure(7, weight=1)

        self._hour_var.trace_variable('w', self._hour_changed)
        self._minute_var.trace_variable('w', self._minute_changed)
        if self._show_seconds:
            self._second_var.trace_variable('w', self._second_changed)

        self._variable.trace_variable('w', self._value_changed)

        self._internal_value_change = True
        self.value = self._variable.get()

    @property
    def value(self):
        """The :class:`~datetime.time` represented by the entry."""

        h = self._hour_var.get()
        m = self._minute_var.get()
        if self._show_seconds:
            s = self._second_var.get()
        else:
            s = 0

        if self._ampm and self._ampm_var.get() == 'pm':
            h += 12
            h = h % 24

        return datetime.time(hour=h,
                             minute=m,
                             second=s)

    @value.setter
    def value(self, value):
        """Set the time to be displayed."""

        if value.hour != self._hour_var.get():
            if self._ampm:
                if value.hour > 0 and value.hour <= 12:
                    self._hour_var.set(value.hour)
                    self._ampm_var.set('am')
                else:
                    self._hour_var.set((value.hour - 12) % 12)
                    self._ampm_var.set('pm')
            else:
                self._hour_var.set('%02d' % (value.hour % 24))

        if value.minute != self._minute_var.get():
            self._minute_var.set('%02d' % value.minute)

        if self._show_seconds and value.second != self._second_var.get():
            self._second_var.set('%02d' % value.second)

        self._internal_value_change = True
        self._variable.set(value)

    def _hour_changed(self, *args):
        value = self._variable.get()
        new_hour = self._hour_var.get()
        old_minute = value.minute

        if self._show_seconds:
            old_second = value.second
            new_time = datetime.time(hour=new_hour,
                                     minute=old_minute,
                                     second=old_second)
        else:
            new_time = datetime.time(hour=new_hour,
                                     minute=old_minute,
                                     second=0)

        self.value = new_time

    def _minute_changed(self, *args):
        value = self._variable.get()
        old_hour = value.hour
        new_minute = self._minute_var.get()

        if self._show_seconds:
            old_second = value.second
            new_time = datetime.time(hour=old_hour,
                                     minute=new_minute,
                                     second=old_second)
        else:
            new_time = datetime.time(hour=old_hour,
                                     minute=new_minute,
                                     second=0)

        self.value = new_time

    def _second_changed(self, *args):
        value = self._variable.get()
        old_hour = value.hour
        old_minute = value.minute
        new_second = self._second_var.get()

        new_time = datetime.time(hour=old_hour,
                                 minute=old_minute,
                                 second=new_second)

        self.value = new_time

    def _value_changed(self, *args):
        if not self._internal_value_change:
            self.value = self._variable.get()
        self._internal_value_change = False

    def _select_time(self):
        """Display the time selection dialog."""

        h = self._hour_var.get()
        if self._ampm and self._ampm_var.get() == 'pm' and h < 12:
            h += 12
            h = h % 24

        if self._show_seconds:
            second = self._second_var.get()
        else:
            second = 0

        t = datetime.time(hour=h,
                          minute=self._minute_var.get(),
                          second=second)

        dlg = TimeDialog(self,
                         _('Select a Time...'),
                         start_time=t,
                         locale=self._locale,
                         show_seconds=self._show_seconds,
                         ampm=self._ampm)
        self.wait_window(dlg)
        new_time = dlg.time
        if new_time != None:
            self.value = new_time


class TimeDialog(tks.dialog.Dialog):
    """Display a dialog to obtain a time from the user

    :param master: The master frame
    :type master: :class:`ttk.Frame`
    :param title: Window title.
    :type title:  str
    :param start_time: The time to display in the entry boxes. If not provided
                       or None then today's date will be used.
    :type start_time:  :class:`datetime.time`
    :param locale: Determines the widgets in the entry.
                   Either a locale name e.g. 'en' or a babel Locale instance.
                   If :mod:`babel` is not installed ISO 8601 format will be
                   used i.e. 24 hours (no am/pm) and ':' as a separator.
    :type locale:  str or :class:`babel.Locale <babel.core.Locale>`
    :param time_position: Controls if and where a text representation of the
                          time is displayed. Can be one of the following

                          None - Don't display
                          tk.TOP - Display above the clock face
                          tk.BOTTOM - Display below the clock face
    :param show_seconds: If True a seconds value can be entered.
    :type show_seconds:  bool
    :param ampm: If not None display a 12 hour clock face with am/pm selection
                 where the 1st element of the tuple is the text for AM and the
                 2nd element for PM.
    :type apmp: (str, str)
    :param fonts: Fonts definitions to use
    :type fonts: :class:`~tks.DefaultFonts`
    """

    def __init__(self, master, title,
                 start_time=None,
                 locale='en',
                 time_position=tk.TOP,
                 show_seconds=False,
                 ampm=None,
                 fonts=None):
        super(TimeDialog, self).__init__(master, title)

        self.time = None

        if not fonts:
            fonts = tks.load_fonts()

        if babel and not isinstance(locale, babel.Locale):
            locale = babel.Locale(locale)

        self.time = None
        if start_time is None:
            start_time = datetime.datetime.time.now()

        self.selector = TimeSelector(self, start_time,
                                      locale=locale,
                                      time_position=time_position,
                                      show_seconds=show_seconds,
                                      ampm=ampm,
                                      fonts=fonts)

    def ok(self, event=None):
        """Called when the OK button is pressed"""

        self.time = self.selector.time

    def cancel(self, event=None):
        """Called when either the Escape key or the Cancel button is pressed"""


class TimeSelector(ttk.Frame, object):
    """A time selection widget.

    :param master: The master frame
    :type master: :class:`ttk.Frame`
    :param locale: Determines the widgets in the entry.
                   Either a locale name e.g. 'en' or a babel Locale instance.
                   If :mod:`babel` is not installed ISO 8601 format will be
                   used i.e. 24 hours (no am/pm) and ':' as a separator.
    :type locale:  str or :class:`babel.Locale <babel.core.Locale>`
    :param ampm: If not None display a 12 hour clock face with am/pm selection
                 where the 1st element of the tuple is the text for AM and the
                 2nd element for PM.
    :type apmp: (str, str)
    :param time_position: Controls where to display the selected time. I None
                          the time is not displayed. If tk.TOP then it is
                          displayed above the clock dial, if tk.BOTTOM then
                          below.
    :type time_position:  str
    :param show_seconds:  If True then the selector can also be used to set
                          seconds.
    :type show_seconds:   bool
    :param fonts: Font definitions to use
    :type fonts: :class:`~tks.DefaultFonts`
    :param colors:    Colors to use.
    :type colors:      :class:`~tks.DefaultColors`

    Used by the :class:`TimeDialog` class but can be used independently."""

    def __init__(self, master, start_time,
                 locale='en',
                 ampm=None,
                 time_position=tk.TOP,
                 show_seconds=False,
                 fonts=None,
                 colors=None):
        self._master = master
        super(TimeSelector, self).__init__(master)
        self._time = None
        self._ampm = ampm

        if start_time is None:
            self._time = datetime.datetime.time.now()
        else:
            self._time = start_time

        if babel and not isinstance(locale, babel.Locale):
            locale = babel.Locale(locale)

        if not fonts:
            fonts = tks.load_fonts()

        if not colors:
            colors = tks.load_colors()

        f = tkf.Font(font=fonts.text)
        f['weight'] = tkf.BOLD
        f['size'] = int(f.actual('size') * 2)
        ttk.Style().configure('TimeFrame.TLabel', font=f,
                              anchor=tk.CENTER,
                              background=colors.header)

        ttk.Style().configure('Selected.TimeFrame.TLabel',
                              foreground=colors.select_dark)

        ttk.Style().configure('TimeFrame.TFrame',
                              relief=tk.SOLID,
                              background=colors.header)

        ttk.Style().configure('SecondFrame.TLabel',
                              foreground='black')

        ttk.Style().configure('Selected.SecondFrame.TLabel',
                              foreground=colors.select_dark)

        self._master.bind('<Key>', self._key_pressed)

        self.hour_var = tk.IntVar()
        self.hour_var.set('%02d' % start_time.hour)
        self.minute_var = tk.IntVar()
        self.minute_var.set('%02d' % start_time.minute)

        if show_seconds:
            self._second_var = tk.IntVar()
            self._second_var.set('%02d' % start_time.second)

            second_scale_frame = ttk.Frame(self)
            self._second_label = ttk.Label(second_scale_frame,
                                           text=_('Seconds'),
                                           style='SecondFrame.TLabel')
            self._second_label.grid(row=0, column=0)

            self._second_scale = ttk.Scale(second_scale_frame, to=59,
                                           variable=self._second_var,
                                           command=self._second_scale_update)
            self._second_scale.grid(row=0, column=1, sticky=(tk.EW, tk.S))

            second_scale_frame.columnconfigure(0, weight=0)
            second_scale_frame.columnconfigure(1, weight=1)
            second_scale_frame.grid(row=2, column=0, padx=4, sticky=tk.EW)

            self._second_var.trace_variable('w', self._second_var_changed)
        else:
            self._second_var = None

        self._time_position = time_position
        if time_position:
            time_frame = ttk.Frame(self, style='TimeFrame.TFrame', padding=4)
            time_frame.columnconfigure(0, weight=1)

            self._hour_text = ttk.Label(time_frame, width=2,
                                        textvariable=self.hour_var,
                                        style='TimeFrame.TLabel')
            self._hour_text.grid(row=0, column=1)
            time_frame.columnconfigure(1, weight=0)
            self._hour_text.bind('<Button-1>', self._hour_text_clicked)

            sep = ttk.Label(time_frame, text=':',
                            style='TimeFrame.TLabel',
                            anchor="center",
                            padding=(6, 0))
            sep.grid(row=0, column=2)
            time_frame.columnconfigure(2, weight=0)

            self._minute_text = ttk.Label(time_frame, width=2,
                                          textvariable=self.minute_var,
                                          style='TimeFrame.TLabel')
            self._minute_text.grid(row=0, column=3)
            time_frame.columnconfigure(3, weight=0)
            self._minute_text.bind('<Button-1>', self._minute_text_clicked)

            if show_seconds:
                sep = ttk.Label(time_frame, text=':',
                                style='TimeFrame.TLabel',
                                anchor='center',
                                padding=(6, 0))
                sep.grid(row=0, column=4)
                time_frame.columnconfigure(4, weight=0)

                self._second_text = ttk.Label(time_frame, width=2,
                                              textvariable=self._second_var,
                                              style='TimeFrame.TLabel')
                self._second_text.grid(row=0, column=5)
                self._second_text.bind('<Button-1>', self._second_text_clicked)
                time_frame.columnconfigure(5, weight=0)

            time_frame.columnconfigure(6, weight=1)

            if time_position == tk.TOP:
                row = 0
            elif time_position == tk.BOTTOM:
                row = 2

            time_frame.grid(row=row, column=0, sticky=(tk.EW, tk.N),
                            padx=4, pady=(4, 0))

        if ampm:
            self._hs = TimeSelector12HourAndMinute(self, start_time,
                                                   ampm=ampm,
                                                   fonts=fonts,
                                                   colors=colors)
            self._ms = None
            self._mode = '12hour'
        else:
            self._hs = TimeSelector24Hour(self, start_time,
                                          fonts=fonts,
                                          colors=colors)
            self._ms = TimeSelectorMinute(self, start_time,
                                          fonts=fonts,
                                          colors=colors)
            self._mode = '24hour'

        self._selector = self._hs
        self._selector.grid(row=1, column=0, sticky=tk.NSEW, padx=3, pady=3)

        self.columnconfigure(0, weight=1)

        self._dial_mode = None
        self._number_key_mode = None
        self.number_key_mode = MODE_HOUR

    @property
    def time(self):
        """The selected time"""

        return self._time

    @time.setter
    def time(self, value):
        self._time = value
        self.hour_var.set('%02d' % value.hour)
        self.minute_var.set('%02d' % value.minute)
        if self._second_var:
            self._second_var.set('%02d' % value.second)

    @property
    def hour(self):
        return self.time.hour

    @hour.setter
    def hour(self, value):
        self.time = datetime.time(value,
                                  self.time.minute,
                                  self.time.second)

    @property
    def minute(self):
        return self.time.minute

    @minute.setter
    def minute(self, value):
        self.time = datetime.time(self.time.hour,
                                  value,
                                  self.time.second)

    @property
    def second(self):
        return self.time.second

    @second.setter
    def second(self, value):
        self.time = datetime.time(self.time.hour,
                                  self.time.minute,
                                  value)

    @property
    def dial_mode(self):
        return self._dial_mode

    @dial_mode.setter
    def dial_mode(self, mode):
        if mode == MODE_HOUR and self._selector is self._ms:
            self._selector.grid_forget()
            self._selector = self._hs
            self._selector.grid(row=1, column=0, sticky=tk.NSEW,
                                padx=3, pady=3)
        elif mode == MODE_MINUTE and self._selector is self._hs:
            self._selector.grid_forget()
            self._selector = self._ms
            self._selector.grid(row=1, column=0, sticky=tk.NSEW,
                                padx=3, pady=3)

        self._dial_mode = mode

    @property
    def number_key_mode(self):
        return self._number_key_mode

    @number_key_mode.setter
    def number_key_mode(self, value):
        if not self._time_position:
            return

        mode = int(value)
        if mode != self._number_key_mode:
            if mode == MODE_NONE:
                self._hour_text.configure(style='TimeFrame.TLabel')
                self._minute_text.configure(style='TimeFrame.TLabel')

                if self._second_var:
                    self._second_text.configure(style='TimeFrame.TLabel')
                    self._second_label.configure(style='SecondFrame.TLabel')
            elif mode == MODE_HOUR:
                self._hour_text.configure(style='Selected.TimeFrame.TLabel')
                self._minute_text.configure(style='TimeFrame.TLabel')

                if self._second_var:
                    self._second_text.configure(style='TimeFrame.TLabel')
                    self._second_label.configure(style='SecondFrame.TLabel')

                if not self._ampm:
                    self.dial_mode = MODE_HOUR
            elif mode == MODE_MINUTE:
                self._hour_text.configure(style='TimeFrame.TLabel')
                self._minute_text.configure(style='Selected.TimeFrame.TLabel')

                if self._second_var:
                    self._second_text.configure(style='TimeFrame.TLabel')
                    self._second_label.configure(style='SecondFrame.TLabel')

                if not self._ampm:
                    self.dial_mode = MODE_MINUTE
            elif mode == MODE_SECOND:
                self._hour_text.configure(style='TimeFrame.TLabel')
                self._minute_text.configure(style='TimeFrame.TLabel')

                if self._second_var:
                    self._second_text.configure(style='Selected.TimeFrame.TLabel')
                    self._second_label.configure(style='Selected.SecondFrame.TLabel')

            self._number_key_mode = mode
            self._number_key_mode_text = ''

    def _hour_text_clicked(self, event):
        self.number_key_mode = MODE_HOUR

    def _minute_text_clicked(self, event):
        self.number_key_mode = MODE_MINUTE

    def _second_text_clicked(self, event):
        self.number_key_mode = MODE_SECOND

    def _number_pressed(self, number):
        mode_after_hour = MODE_MINUTE

        if self._second_var:
            mode_after_minute = MODE_SECOND
        else:
            mode_after_minute = MODE_NONE

        if self.number_key_mode == MODE_HOUR:
            if not self._number_key_mode_text:
                if (self._mode == '24hour' and number > '2') or \
                   (self._mode == '12hour' and number > '1'):
                    self.number_key_mode = mode_after_hour
                self._number_key_mode_text = number
                self.hour = int(number)
            else:
                if self._number_key_mode_text[-1] == '2':
                    if number < '4':
                        self._number_key_mode_text += number
                        self.hour = int(self._number_key_mode_text)
                        self.number_key_mode = mode_after_hour
                else:
                    self._number_key_mode_text += number
                    self.hour = int(self._number_key_mode_text)
                    self.number_key_mode = mode_after_hour

            self._hs.hour = self.hour

        elif self.number_key_mode == MODE_MINUTE:
            if not self._number_key_mode_text:
                if number > '5':
                    self.number_key_mode = mode_after_minute
                self._number_key_mode_text = number
                self.minute = int(number)
            else:
                self._number_key_mode_text += number
                self.minute = int(self._number_key_mode_text)
                self.number_key_mode = mode_after_minute

            self._hs.minute = self.minute
            if self._ms:
                self._ms.minute = self.minute

        elif self.number_key_mode == MODE_SECOND:
            if not self._number_key_mode_text:
                if number > '5':
                    self.number_key_mode = MODE_NONE
                self._number_key_mode_text = number
                self.second = int(number)
            else:
                self._number_key_mode_text += number
                self.second = int(self._number_key_mode_text)
                self.number_key_mode = MODE_NONE

    def _key_pressed(self, event):
        """Respond to a key being pressed"""

        if not self._time_position:
            return

        if event.char >= '0' and event.char <= '9':
            self._number_pressed(event.char)
        elif event.char == ':':
            if self.number_key_mode == MODE_HOUR:
                self.number_key_mode = MODE_MINUTE
            elif self.number_key_mode == MODE_MINUTE and self._second_var:
                self.number_key_mode = MODE_SECOND
        elif event.keysym == 'Return':
            self._master.ok()

    def _second_scale_update(self, value):
        """Make sure the second value is a whole number."""

        self._second_var.set('%02d' % int(math.floor(float(value))))
        self.number_key_mode = MODE_NONE

    def _second_var_changed(self, *args):
        """Update ourselves whenever the second var chnages"""

        self.second = self._second_var.get()


class TimeSelector12HourAndMinute(ttk.Frame, object):
    """A Time selector widget"""

    def __init__(self, master,
                 start_time,
                 ampm,
                 fonts,
                 colors):
        self._master = master
        super(TimeSelector12HourAndMinute, self).__init__(master)

        self._ampm = ampm
        self._fonts = fonts
        self._colors = colors

        self._last_hour_tag = ''
        self._last_minute_tag = ''

        self._am = True
        self._hour = 0
        self._minute = 0

        self._hour_hand = None
        self._minute_hand = None

        self._canvas = tk.Canvas(self)
        self._canvas.grid(row=1, column=0, sticky=(tk.EW, tk.S))
        self._create_canvas()

        self.columnconfigure(0, weight=1)

        self.hour = start_time.hour
        self.minute = start_time.minute
        self.second = start_time.second

    @property
    def time(self):
        return datetime.time(self.hour, self.minute, self.second)

    @property
    def am(self):
        return self._am

    @am.setter
    def am(self, value):
        self._am = bool(value)
        if self._am:
            self._canvas.itemconfigure('pmr', fill='#fff')
            self._canvas.itemconfigure('amr', fill=self._colors.select)
            self._hour = (self._hour - 12) % 24
            self._master.hour = self.hour
        else:
            self._canvas.itemconfigure('amr', fill='#fff')
            self._canvas.itemconfigure('pmr', fill=self._colors.select)
            self._hour = (self._hour + 12) % 24
            self._master.hour = self.hour

    @property
    def hour(self):
        return self._hour

    @hour.setter
    def hour(self, value):
        h = int(value) % 24

        tag = None
        if h == 0:
            self.am = True
            tag = 'h12c'
        elif h == 12:
            self.am = False
            tag = 'h12c'
        elif h > 12:
            self.am = False
            tag = 'h%dc' % (h - 12)
        else:
            self.am = True
            tag = 'h%dc' % h

        if tag != self._last_hour_tag:
            self._canvas.itemconfig(tag, fill=self._colors.select)
            if self._last_hour_tag:
                self._canvas.itemconfig(self._last_hour_tag, fill='')

        self._last_hour_tag = tag
        self._hour = h
        self._master.hour = h
        self._hour_hand.value = h

    @property
    def minute(self):
        return self._minute

    @minute.setter
    def minute(self, value):
        m = int(value) % 60

        tag = 'm%dc' % m
        self._canvas.itemconfig(tag, fill=self._colors.select)
        if self._last_minute_tag:
            self._canvas.itemconfig(self._last_minute_tag, fill='')

        self._last_minute_tag = tag
        self._minute = m
        self._master.minute = m
        self._minute_hand.value = m

    def _hm_clicked(self, event):
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)

        items = self._canvas.find_closest(x, y)
        tags = self._canvas.gettags(items[0])

        if 'face' in tags:
            return

        for tag in tags:
            if tag[0] == 'm' or tag[0] == 'h':
                break
        else:
            return

        if tag.endswith('t'):
            tag = '%sc' % tag[:-1]

        value = int(tag[1:-1])
        if tag.startswith('h'):
            if tag == self._last_hour_tag:
                return

            if self.am:
                if value == 12:
                    self.hour = 0
                else:
                    self.hour = value
            else:
                if value != 12:
                    value += 12
                self.hour = value

            self._master.number_key_mode = MODE_HOUR
        else:
            if tag == self._last_minute_tag:
                return

            self.minute = value
            self._master.number_key_mode = MODE_MINUTE

        self._canvas.itemconfig(tag, fill=self._colors.select)

    def _ampm_clicked(self, event):
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)

        items = self._canvas.find_closest(x, y)
        tags = self._canvas.gettags(items[0])

        if 'am' in tags and not self.am:
            self.am = True
        elif 'pm' in tags and self.am:
            self.am = False

    def _create_canvas(self):
        f = tkf.Font(font=self._fonts.text)
        hour_text_width = f.measure('00')
        selection_radius = hour_text_width * 1.125

        outer_radius = hour_text_width * 8
        dial_radius = outer_radius + selection_radius + PADDING
        inner_radius = outer_radius - (PADDING / 2) - (selection_radius * 2)
        hand_radius = inner_radius - selection_radius

        width = height = (dial_radius * 2) + 1

        self._center = (dial_radius + (PADDING / 2),
                        dial_radius + (PADDING / 2))


        dial_rect = tks.rect_at(self._center, dial_radius)
        self._canvas.create_oval(dial_rect,
                                 fill=self._colors.fill,
                                 tags='face',
                                 width='0.5',
                                 outline=self._colors.outline)

        radii = [inner_radius, outer_radius]

        for radius in radii:
            for idx, angle in enumerate(range(30, 361, 30)):
                x_offset = math.sin(math.radians(angle)) * radius
                y_offset = -math.cos(math.radians(angle)) * radius

                if radius == inner_radius:
                    i = ((idx + 1) * 5) % 60
                    tag = 'm%d' % i
                    text = '%02d' % i
                elif radius == outer_radius:
                    i = idx + 1
                    tag = 'h%d' % i
                    text = str(i)

                oval_rect = tks.rect_at((self._center[0] + x_offset,
                                         self._center[1] + y_offset),
                                        selection_radius)
                iid = self._canvas.create_oval(oval_rect,
                                               fill=self._colors.fill,
                                               outline='',
                                               tags='%sc' % tag)

                self._canvas.tag_bind(iid, '<Button-1>', self._hm_clicked)
                self._canvas.tag_raise(iid)

                iid = self._canvas.create_text((self._center[0] + x_offset,
                                                self._center[1] + y_offset),
                                               text=text,
                                               tags='%st' % tag,
                                               font=f)

                self._canvas.tag_bind(iid, '<Button-1>', self._hm_clicked)
                self._canvas.tag_raise(iid)

        ampm_width = max(f.measure('am'),
                         f.measure('pm')) + (2 * PADDING)
        ampm_height = f.metrics('linespace') + PADDING
        am_rect = (self._center[0] - (ampm_width / 2),
                   self._center[1] - PADDING - (1.25 * ampm_height),
                   self._center[0] + (ampm_width / 2),
                   self._center[1] - PADDING - (0.25 * ampm_height))

        self._canvas.create_rectangle(am_rect,
                                      outline=self._colors.outline,
                                      fill=self._colors.select,
                                      tags=('am', 'ampm', 'amr'))

        am_text = self._ampm[0]
        pm_text = self._ampm[1]
        am_pos = tks.rect_center(am_rect)
        self._canvas.create_text(am_pos, text=am_text, tags=('am', 'ampm'))

        pm_rect = (self._center[0] - (ampm_width / 2),
                   self._center[1] + PADDING + (0.25 * ampm_height),
                   self._center[0] + (ampm_width / 2),
                   self._center[1] + PADDING + (1.25 * ampm_height))

        self._canvas.create_rectangle(pm_rect,
                                      fill='#fff',
                                      outline=self._colors.outline,
                                      tags=('pm', 'ampm', 'pmr'))

        pm_pos = tks.rect_center(pm_rect)
        self._canvas.create_text(pm_pos, text=pm_text, tags=('pm', 'ampm'))

        self._canvas.tag_bind('ampm', '<Button-1>', self._ampm_clicked)

        self._minute_hand = ClockHand(self._canvas, self._center,
                                      hand_radius)

        self._hour_hand = ClockHand(self._canvas, self._center,
                                    outer_radius - selection_radius,
                                    mode='hour')

        center_circle_rect = tks.rect_at(self._center, PADDING)
        self._canvas.create_oval(center_circle_rect,
                                 fill=self._colors.select,
                                 outline=self._colors.outline)

        self._canvas.tag_lower('face')
        self._canvas.tag_raise('text')
        self._canvas.tag_raise('minute')
        self._canvas.tag_raise('ampm')
        self._canvas.configure(width=width, height=height)

    def key_pressed(self, key):
        if key == 'a' and not self.am:
            self.am = True
        elif key == 'p' and self.am:
            self.am = False


class TimeSelector24Hour(ttk.Frame, object):
    """A Time selector widget"""

    def __init__(self, master,
                 start_time,
                 fonts,
                 colors):
        super(TimeSelector24Hour, self).__init__(master)
        self._master = master

        if start_time is None:
            start_time = datetime.datetime.now().time()

        self._colors = colors
        self._fonts = fonts

        self._hour_hand_inner = None
        self._hour_hand_outer = None

        self._canvas = tk.Canvas(self)
        self._canvas.grid(row=1, column=0, sticky=(tk.EW, tk.S))
        self._create_canvas()

        self.columnconfigure(0, weight=1)

        self._hour = -1
        self._last_hour_tag = ''
        self.hour = start_time.hour

        self._center = None

    @property
    def hour(self):
        return self._hour

    @hour.setter
    def hour(self, value):
        h = int(value) % 24
        tag = 'h%dc' % h

        if tag != self._last_hour_tag:
            self._canvas.itemconfig(tag, fill=self._colors.select)
            if self._last_hour_tag:
                self._canvas.itemconfig(self._last_hour_tag, fill='')

        self._last_hour_tag = tag
        self._hour = h
        self._master.hour = h

        if h > 12 or h == 0:
            self._hour_hand_inner.value = -1
            self._hour_hand_outer.value = h - 12
        else:
            self._hour_hand_inner.value = h
            self._hour_hand_outer.value = -1

    def _hour_clicked(self, event):
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)

        items = self._canvas.find_closest(x, y)
        tags = self._canvas.gettags(items[0])

        if 'face' in tags:
            return

        for tag in tags:
            if tag[0] == 'm' or tag[0] == 'h':
                break

        if tag.endswith('t'):
            tag = '%sc' % tag[:-1]

        if tag.startswith('h'):
            if tag == self._last_hour_tag:
                return

            value = int(tag[1:-1])
            self.hour = value

        self._canvas.itemconfig(tag, fill=self._colors.select)

        self._master.dial_mode = MODE_MINUTE
        self._master.number_key_mode = MODE_MINUTE

    def _dial_clicked(self, event):
        x = self._canvas.canvasx(event.x) - self._center[0]
        y = self._canvas.canvasy(event.y) - self._center[1]

        angle = math.degrees(math.atan2(y, x))
        self.hour = int(math.floor(((angle + 90) % 360) / 30))

    def _create_canvas(self):
        f = tkf.Font(font=self._fonts.text)
        hour_text_width = f.measure('00')
        selection_radius = hour_text_width * 1.125

        outer_radius = hour_text_width * 8
        dial_radius = outer_radius + selection_radius + PADDING
        inner_radius = outer_radius - (PADDING / 2) - (selection_radius * 2)

        width = height = (dial_radius * 2) + 1
        self._center = (dial_radius + (PADDING / 2),
                        dial_radius + (PADDING / 2))

        dial_rect = tks.rect_at(self._center, dial_radius)
        dial = self._canvas.create_oval(dial_rect,
                                        fill=self._colors.fill,
                                        tags='face',
                                        width='0.5',
                                        outline=self._colors.outline)
        self._canvas.tag_bind(dial, '<Button-1>', self._dial_clicked)

        radii = [inner_radius, outer_radius]

        for radius in radii:
            for idx, angle in enumerate(range(30, 361, 30)):
                x_offset = math.sin(math.radians(angle)) * radius
                y_offset = -math.cos(math.radians(angle)) * radius

                if radius == inner_radius:
                    i = idx + 1
                    circle_tag = 'inner_circle'
                elif radius == outer_radius:
                    i = idx + 1 + 12
                    circle_tag = 'outer_circle'

                i = i % 24

                tag = 'h%d' % i
                text = '%02d' % i

                oval_rect = tks.rect_at((self._center[0] + x_offset,
                                         self._center[1] + y_offset),
                                        selection_radius)
                iid = self._canvas.create_oval(oval_rect,
                                               fill='',
                                               outline='',
                                               tags=('%sc' % tag, circle_tag))

                self._canvas.tag_bind(iid, '<Button-1>', self._hour_clicked)
                self._canvas.tag_raise(iid)

                iid = self._canvas.create_text((self._center[0] + x_offset,
                                                self._center[1] + y_offset),
                                               text=text,
                                               tags=('%st' % tag, 'text'),
                                               font=f)

                self._canvas.tag_bind(iid, '<Button-1>', self._hour_clicked)
                self._canvas.tag_raise(iid)

        self._canvas.tag_lower('face')
        self._canvas.configure(width=width, height=height)

        self._hour_hand_inner = ClockHand(self._canvas, self._center,
                                          inner_radius - selection_radius,
                                          mode='hour')
        self._hour_hand_outer = ClockHand(self._canvas, self._center,
                                          outer_radius - selection_radius,
                                          mode='hour')

        center_circle_rect = tks.rect_at(self._center, PADDING)
        self._canvas.create_oval(center_circle_rect,
                                 fill=self._colors.select,
                                 outline=self._colors.outline)

        self._canvas.tag_raise('circle')
        self._canvas.tag_raise('text')


class TimeSelectorMinute(ttk.Frame, object):
    """A Time selector widget"""

    def __init__(self, master,
                 start_time,
                 fonts,
                 colors):
        super(TimeSelectorMinute, self).__init__(master)
        self._master = master
        self._fonts = fonts
        self._colors = colors
        self._minute = -1
        self._last_minute_tag = ''
        self._center = None

        self._canvas = tk.Canvas(self)
        self._canvas.grid(row=1, column=0, sticky=(tk.EW, tk.S))
        self._create_canvas()

        self.columnconfigure(0, weight=1)

        self.minute = start_time.minute

    @property
    def minute(self):
        return self._minute

    @minute.setter
    def minute(self, value):
        value = int(value) % 60
        if value != self._minute:
            tag = 'h%dc' % value

            if (value % 5) == 0:
                self._canvas.itemconfig(tag, fill=self._colors.select)
                self._minute_indicator.minute = -1

                self._minute_indicator.tag_raise()
                self._canvas.tag_lower('text')
                self._canvas.tag_lower('circle')
                self._canvas.tag_lower(self._minute_hand.tag)
                self._canvas.tag_lower('face')
            else:
                self._minute_indicator.minute = value

                self._minute_indicator.tag_raise()
                self._minute_hand.tag_lower()
                self._canvas.tag_lower('text')
                self._canvas.tag_lower('circle')
                self._canvas.tag_lower('face')

            if tag != self._last_minute_tag:
                self._canvas.itemconfig(tag, fill=self._colors.select)
                if self._last_minute_tag:
                    self._canvas.itemconfig(self._last_minute_tag, fill='')

            self._last_minute_tag = tag
            self._minute = value
            self._master.minute = value
            self._minute_hand.value = value

    def _minute_clicked(self, event):
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)

        items = self._canvas.find_closest(x, y)
        tags = self._canvas.gettags(items[0])

        if 'face' in tags:
            return

        for tag in tags:
            if tag[0] == 'm' or tag[0] == 'h':
                break

        if tag.endswith('t'):
            tag = '%sc' % tag[:-1]

        value = int(tag[1:-1])
        if tag == self._last_minute_tag:
            return

        self.minute = value

    def _dial_clicked(self, event):
        x = self._canvas.canvasx(event.x) - self._center[0]
        y = self._canvas.canvasy(event.y) - self._center[1]

        angle = math.degrees(math.atan2(y, x))
        self.minute = int(math.floor(((angle + 90) % 360) / 6))

    def _create_canvas(self):
        f = tkf.Font(font=self._fonts.text)
        hour_text_width = f.measure('00')
        selection_radius = hour_text_width * 1.125

        outer_radius = hour_text_width * 8
        dial_radius = outer_radius + selection_radius + PADDING
        # inner_radius = outer_radius - (PADDING / 2) - (selection_radius * 2)
        hand_radius = outer_radius

        width = height = (dial_radius * 2) + 1
        self._center = (dial_radius + (PADDING / 2),
                        dial_radius + (PADDING / 2))

        dial_rect = tks.rect_at(self._center, dial_radius)
        dial = self._canvas.create_oval(dial_rect,
                                        fill=self._colors.fill,
                                        tags='face',
                                        width='0.5',
                                        outline=self._colors.outline)
        self._canvas.tag_bind(dial, '<Button-1>', self._dial_clicked)

        radii = [outer_radius]

        for radius in radii:
            for idx, angle in enumerate(range(30, 361, 30)):
                x_offset = math.sin(math.radians(angle)) * radius
                y_offset = -math.cos(math.radians(angle)) * radius

                if radius == outer_radius:
                    i = (idx + 1) * 5

                i = i % 60

                tag = 'h%d' % i
                text = '%02d' % i

                oval_rect = tks.rect_at((self._center[0] + x_offset,
                                         self._center[1] + y_offset),
                                        selection_radius)
                iid = self._canvas.create_oval(oval_rect,
                                               fill=self._colors.fill,
                                               outline='',
                                               tags=('%sc' % tag, 'circle'))

                self._canvas.tag_bind(iid, '<Button-1>', self._minute_clicked)
                self._canvas.tag_raise(iid)

                iid = self._canvas.create_text((self._center[0] + x_offset,
                                                self._center[1] + y_offset),
                                               text=text,
                                               tags=('%st' % tag, 'text'),
                                               font=f)

                self._canvas.tag_bind(iid, '<Button-1>', self._minute_clicked)
                self._canvas.tag_raise(iid)

        self._canvas.configure(width=width, height=height)

        self._minute_hand = ClockHand(self._canvas, self._center, hand_radius)
        self._minute_indicator = MinuteIndicator(self._canvas, self._center,
                                                 hand_radius)

        center_circle_rect = tks.rect_at(self._center, PADDING)

        self._canvas.create_oval(center_circle_rect,
                                 fill=self._colors.select,
                                 outline=self._colors.outline)


class ClockHand(object):
    """Draws a clock hand on the canvas"""

    def __init__(self, canvas, center, radius, mode='minute'):
        self._mode = mode
        self.tag = '%s_hand' % mode
        self._canvas = canvas
        self._center = center
        self._radius = radius

        coords = (center[0], center[1], center[0], center[1])
        self._line = canvas.create_line(coords,
                                        fill='#888',
                                        tags=self.tag,
                                        width=1.25)
        self._variable = -1

    @property
    def value(self):
        return self._variable

    @value.setter
    def value(self, value):
        if value != self._variable:
            if value != -1:
                if self._mode == 'minute':
                    angle = value * 6
                else:
                    angle = value * 30

                x = self._center[0] + math.sin(math.radians(angle)) * self._radius
                y = self._center[1] - math.cos(math.radians(angle)) * self._radius

                coords = (self._center[0], self._center[1], x, y)
            else:
                coords = (-2, -2, -1, -1)

            self._canvas.coords(self._line, coords)
            self._variable = value

    def tag_raise(self):
        """Raise ourselves to the top of the canvas stack"""

        self._canvas.tag_raise(self.tag)

    def tag_lower(self):
        """Lower ourselves to the bottom of the canvas stack"""

        self._canvas.tag_lower(self.tag)


class MinuteIndicator(object):
    """Draws a marker on the canvas for the selected minute when the
    minute is not a multiple of 5.
    """

    def __init__(self, canvas, center, radius):
        self.tag = 'minute_indicator'
        self._canvas = canvas
        self._center = center
        self._radius = radius
        self._indicator_radius = 4
        self._offscreen = (-10, -10, -9, -9)
        self._minute = -1
        self._indicator = canvas.create_oval(self._offscreen,
                                             outline='',
                                             fill=tks.DefaultColors.select_dark,
                                             tags=self.tag)

    @property
    def minute(self):
        """The minute to draw the marker for."""

        return self._minute

    @minute.setter
    def minute(self, value):
        """Updates the position of the minute marker"""

        if value != -1 and value % 5 != 0:
            angle = value * 6

            x = self._center[0] + math.sin(math.radians(angle)) * self._radius
            y = self._center[1] - math.cos(math.radians(angle)) * self._radius

            rect = tks.rect_at((x, y), self._indicator_radius)
        else:
            rect = self._offscreen

        self._canvas.coords(self._indicator, rect)

    def tag_raise(self):
        """Raise ourselves to the top of the canvas stack"""

        self._canvas.tag_raise(self.tag)

    def tag_lower(self):
        """Lower ourselves to the bottom of the canvas stack"""

        self._canvas.tag_lower(self.tag)

