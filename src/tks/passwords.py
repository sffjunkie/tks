""":mod:`tks.passwords` provides 2 classes to obtain a password from a user

:class:`PasswordEntry`
    Displays a widget which allows the user to enter a password

:class:`PasswordDialog`
    Displays a dialog which allows the user to generate a random password.
"""

from __future__ import print_function, division, absolute_import
import sys
import random
import string

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import ttk
else:
    import Tkinter as tk
    import ttk

import tks
import tks.dialog

from tks.i18n import language
_ = language.gettext


class PasswordEntry(ttk.Frame, object):
    """A password entry widget

    Creates a frame which contains an entry box for a password and optionally

    * A checkbox to show and hide the password
    * A second entry box to make sure the password was entered as the user
      thought.
    * A button which displays a dialog to generate a random password.

    :param master:   The master frame
    :type master:    :class:`ttk.Frame`
    :param variable: The variable which hold the date to display in
                     the entry boxes.
    :type variable:  :class:`~Tkinter.StringVar`
    :param show_hide: If True a show/hide checkbox is added to show the actual
                      characters.
    :type show_hide:    bool
    :param compare:  If True a second entry box is shown to as a comparison.
    :type compare:    bool
    :param generate:  If True a button is shown which displays a password
                      generator when clicked.
    :type generate:    bool
    :param fonts:    Fonts to use.
    :type fonts:      :class:`~tks.DefaultFonts`
    :param colors:    Fonts to use.
    :type colors:      :class:`~tks.DefaultColors`
    """

    def __init__(self, master,
                 variable=None,
                 show_hide=True,
                 compare=True,
                 generate=True,
                 fonts=None,
                 colors=None):
        self.master = master
        super(PasswordEntry, self).__init__(master)

        if variable:
            self._password = variable
        else:
            self._password = tk.StringVar()

        if not fonts:
            fonts = tks.load_fonts()

        if not colors:
            self.colors = tks.load_colors()

        self._validate_entry = (master.register(self._tk_validate_entry),
                                '%P', '%V', '%W')

        self._entry = ttk.Entry(self, textvariable=self._password,
                                validate='all',
                                show='*',
                                font=fonts.text,
                                width=13)
        self._entry.grid(row=0, column=0, sticky=tk.EW)

        if compare:
            self._status_lbl = tk.Label(self, text='==',
                                        font=fonts.monospace)
            self._status_lbl.grid(row=0, column=1)

            self._entry['validatecommand'] = self._validate_entry

            self._check_password = tk.StringVar()
            self._entry2 = ttk.Entry(self, textvariable=self._check_password,
                                     validate='all',
                                     validatecommand=self._validate_entry,
                                     show='*',
                                     font=fonts.text,
                                     width=13)
            self._entry2.grid(row=0, column=2, sticky=tk.EW)

        if show_hide:
            self._show_password_var = tk.IntVar()
            self._show_password = ttk.Checkbutton(self, text=_("Show"),
                                                  variable=self._show_password_var)

            self._show_password.grid(row=0, column=3)
            self._show_password_var.trace_variable('w', self._show_password_toggle)

        if generate:
            self._generate_btn = ttk.Button(self, text="Generate...",
                                            command=self._generate_password)
            self._generate_btn.grid(row=0, column=4)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

    @property
    def value(self):
        pass1 = self._password.get()
        pass2 = self._check_password.get()

        if pass1 and pass1 == pass2:
            return pass1
        else:
            return None

    @value.setter
    def value(self, value):
        self._password.set(str(value))
        self._check_password.set(str(value))

    @property
    def valid(self):
        pass1 = self._password.get()
        pass2 = self._check_password.get()

        return pass1 and pass1 == pass2

    def _show_password_toggle(self, *args):
        if self._entry['show'] == '*':
            self._entry['show'] = ''
            self._entry2['show'] = ''
        else:
            self._entry['show'] = '*'
            self._entry2['show'] = '*'

    def _tk_validate_entry(self, P, V, W):
        rtn = 1
        if V == 'focusout':
            rtn = 1
        elif V == 'key':
            if W == str(self._entry):
                value1 = P
                value2 = self._check_password.get()
            else:
                value1 = self._password.get()
                value2 = P

            if value1 == value2:
                self._status_lbl['text'] = '=='
                self._status_lbl['foreground'] = 'black'
            else:
                self._status_lbl['text'] = '!='
                self._status_lbl['foreground'] = self.colors.invalid

        return rtn

    def _generate_password(self):
        dlg = PasswordDialog(self, _("Generate a Password"))
        self.wait_window(dlg)


class PasswordDialog(tks.dialog.Dialog):
    """A Password Generator Dialog

    :param master:  The master frame
    :type master:   :class:`ttk.Frame`
    :param title:   Dialog title
    :type title:    str
    """

    def __init__(self, master, title,
                 fonts=None,
                 colors=None):
        super(PasswordDialog, self).__init__(master, title,
                                                      ok_text=_('Use Password'))

        self.master = master
        self.selector = PasswordGenerator(self)

    def ok(self):
        """Called when the OK button is pressed"""

        value = self.selector.value
        if value:
            self.master.value = value

    def cancel(self):
        """Called when either the Escape key or the Cancel button is pressed"""


class PasswordGenerator(ttk.Frame, object):
    def __init__(self, master):
        super(PasswordGenerator, self).__init__(master)

        self._password = tk.StringVar()

        lbl = ttk.Label(self, text=_("Password"))
        lbl.grid(row=0, column=0, sticky=tk.W)

        f = tk.Frame(self)
        self._password_entry = ttk.Entry(f, textvariable=self._password)
        self._password_entry.grid(row=0, column=0, sticky=tk.EW)

        self._refresh_btn = ttk.Button(f, text=_("Refresh"),
                                       command=self._generate_password)
        self._refresh_btn.grid(row=0, column=1)
        f.grid(row=0, column=1)

        lbl = ttk.Label(self, text=_("Length"))
        lbl.grid(row=1, column=0, sticky=tk.W)

        values = range(4, 101)
        self._length_var = tk.IntVar(value=12)
        self._length_combo = ttk.Combobox(self, values=values,
                                          textvariable=self._length_var,
                                          width=5)
        self._length_combo.grid(row=1, column=1, sticky=tk.W)

        self._upper_var = tk.BooleanVar(value=True)
        self._lower_var = tk.BooleanVar(value=True)
        self._digit_var = tk.BooleanVar(value=True)
        self._symbol_var = tk.BooleanVar(value=False)

        lbl = ttk.Label(self, text=_("Use"))
        lbl.grid(row=2, column=0, sticky=tk.W)

        f = tk.Frame(self)
        cb = ttk.Checkbutton(f, text=_("A-Z"),
                             variable=self._upper_var)
        cb.grid(row=0, column=0, sticky=tk.W)
        cb = ttk.Checkbutton(f, text=_("a-z"),
                             variable=self._lower_var)
        cb.grid(row=0, column=1, sticky=tk.W)
        cb = ttk.Checkbutton(f, text=_("0-9"),
                             variable=self._digit_var)
        cb.grid(row=0, column=2, sticky=tk.W)
        cb = ttk.Checkbutton(f, text=_("!$%@#"),
                             variable=self._symbol_var)
        cb.grid(row=0, column=3, sticky=tk.W)
        f.grid(row=2, column=1, sticky=tk.W)

        self._generate_password()

    @property
    def value(self):
        return self._password.get()

    def _generate_password(self, *args):
        length = self._length_var.get()

        r = random.SystemRandom()

        chars = []
        if self._upper_var.get():
            chars.append(string.ascii_uppercase)

        if self._lower_var.get():
            chars.append(string.ascii_lowercase)

        if self._digit_var.get():
            chars.append(string.digits)

        if self._symbol_var.get():
            chars.append("!$%@#")

        #http://thelivingpearl.com/2013/01/02/generating-and-checking-passwords-in-python/
        pass_gen = lambda length, ascii: "".join([list(set(ascii))[r.randint(0, len(list(set(ascii))) - 1)] for i in range(length)])

        p = pass_gen(length, ''.join(chars))
        self._password.set(p)
