from __future__ import print_function, division, absolute_import
import sys

if sys.version_info >= (3, 0):
    import tkinter as tk
    from tkinter import font as tkf
    from tkinter import ttk
else:
    import Tkinter as tk
    import tkFont as tkf
    import ttk

from tks.i18n import language
_ = language.gettext

import tks


class Dialog(tk.Toplevel, object):
    """A Dialog bas class"""

    def __init__(self, master, title,
                 ok_text=None,
                 cancel_text=None,
                 fonts=None,
                 colors=None):
        super(Dialog, self).__init__(master)

        self.withdraw()
        self.title(title)

        if not ok_text:
            ok_text = _('OK')

        if not cancel_text:
            cancel_text = _('Cancel')

        if not fonts:
            fonts = tks.load_fonts()

        if not colors:
            colors = tks.load_colors()

        okcancel = ttk.Frame(self, padding=(3, 3, 3, 3), style='TFrame')

        # Swap the order of buttons for Windows
        if 'win32' in sys.platform:
            btn_column = (1, 2)
        else:
            btn_column = (2, 1)

        btn_width = max(8, len(ok_text)) + 2
        self.ok_btn = ttk.Button(okcancel, text=ok_text, width=btn_width,
                                 command=self._ok)
        self.ok_btn.grid(column=btn_column[0], row=0, padx=(6, 0), sticky=tk.SE)

        btn_width = max(8, len(cancel_text)) + 2
        cancel = ttk.Button(okcancel, text=cancel_text, width=btn_width,
                            command=self._cancel)
        cancel.grid(column=btn_column[1], row=0, padx=(6, 0), sticky=tk.SE)

        okcancel.columnconfigure(0, weight=1)
        okcancel.columnconfigure(1, weight=0)
        okcancel.columnconfigure(2, weight=0)

        okcancel.grid(column=0, row=1, sticky=(tk.EW, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.update_idletasks()

        self.bind('<Escape>', self._cancel)
        self.protocol('WM_DELETE_WINDOW', self._cancel)
        self.focus()
        self.transient(master)
        self.grab_set()

    def ok(self):
        raise NotImplementedError

    def cancel(self):
        raise NotImplementedError

    @property
    def selector(self):
        return self._selector

    @selector.setter
    def selector(self, value):
        self._selector = value
        self._selector.grid(row=0, column=0)
        s = self._selector.size

    def _ok(self, event=None):
        """Called when the OK button is pressed"""

        self.ok()
        self.grab_release()
        self.destroy()

    def _cancel(self, event=None):
        """Called when either the Escape key or the Cancel button is pressed"""

        self.cancel()
        self.grab_release()
        self.destroy()
