# This code is taken from the Tkinter drag and drop module included in versions
# of Python. It has been changed to...
#
# 1. Use the button specific events for release and motion. This is done because
#    for example '<Motion>' events do not appear # to be generated on Windows.
# 2. Define cursors to be used

"""Drag and drop handling."""

import sys

if 'win32' in sys.platform:
    CURSOR_FORBIDDEN = 'no'
elif 'darwin' in sys.platform:
    CURSOR_FORBIDDEN = 'notallowed'
else:
    CURSOR_FORBIDDEN = 'pirate'

CURSOR_WIDGET = 'hand2'


def dnd_start(source, event):
    """Called by widgets to start the drag and drop process."""

    h = DndHandler(source, event)
    if h.root:
        return h
    else:
        return None


class DndHandler(object):
    """The drag and drop machinery."""

    root = None

    def __init__(self, source, event):
        if event.num > 5:
            return
        root = event.widget._root()

        if hasattr(root, '__dnd'):
            return
        root.__dnd = self

        self.root = root
        self.source = source
        self.target = None
        self.initial_button = button = event.num
        self.initial_widget = widget = event.widget
        self.release_pattern = "<B%d-ButtonRelease-%d>" % (button, button)
        self.save_cursor = widget['cursor'] or ""
        widget.bind(self.release_pattern, self.on_release)
        widget.bind("<B%d-Motion>" % button, self.on_motion)
        widget['cursor'] = CURSOR_WIDGET

    def __del__(self):
        root = self.root
        self.root = None
        if root:
            try:
                del root.__dnd
            except AttributeError:
                pass

    def on_motion(self, event):
        """Called when the mouse moves with button 1 held down."""

        x, y = event.x_root, event.y_root
        target_widget = self.initial_widget.winfo_containing(x, y)
        source = self.source
        new_target = None
        while target_widget:
            try:
                attr = target_widget.dnd_accept
            except AttributeError:
                pass
            else:
                new_target = attr(source, event)
                if new_target:
                    break
            target_widget = target_widget.master
        old_target = self.target
        if old_target is new_target:
            if old_target:
                old_target.dnd_motion(source, event)
        else:
            if old_target:
                self.target = None
                old_target.dnd_leave(source, event)
            if new_target:
                new_target.dnd_enter(source, event)
                self.target = new_target

    def on_release(self, event):
        """Called when the mouse button is released."""

        self.finish(event, 1)

    def cancel(self, event=None):
        """Called to cancel the drag and drop."""

        self.finish(event, 0)

    def finish(self, event, commit=0):
        """Called to finish the drag and drop operation."""

        target = self.target
        source = self.source
        widget = self.initial_widget
        root = self.root
        try:
            del root.__dnd
            self.initial_widget.unbind(self.release_pattern)
            self.initial_widget.unbind("<B%d-Motion>" % self.initial_button)
            widget['cursor'] = self.save_cursor
            self.target = self.source = self.initial_widget = self.root = None
            if target:
                if commit:
                    target.dnd_commit(source, event)
                else:
                    target.dnd_leave(source, event)
        finally:
            source.dnd_end(target, event)
