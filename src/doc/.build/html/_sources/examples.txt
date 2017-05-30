.. _code-examples:

Code Examples
=============

A Date Entry
------------

To display the date entry and dialog shown
:ref:`in the gallery <gallery-date>` the following code can be used.

::

   try:
       import tkinter as tk
   except ImportError:
       import Tkinter as tk
   
   from tks.dates import DateEntry
   
   if __name__ == '__main__':
       root = tk.Tk()
       root.title('Date Test')
       entry = DateEntry(root, locale='pt')
       entry.grid(row=0, column=0, sticky=tk.EW)
       root.columnconfigure(0, weight=1)
       root.mainloop()


A Time Entry
------------

To display the time entry and dialog shown
:ref:`in the gallery <gallery-time>` the following code can be used.

::

   try:
       import tkinter as tk
   except ImportError:
       import Tkinter as tk
   
   from tks.times import TimeEntry
   
   if __name__ == '__main__':
       root = tk.Tk()
       root.title('Time Test')
       entry = TimeEntry(root, locale='en_US')
       entry.grid(row=0, column=0, sticky=tk.EW)
       root.columnconfigure(0, weight=1)
       root.mainloop()


A Color Entry
-------------

To display the color entry and dialog shown
:ref:`in the gallery <gallery-color>` the following code can be used.

::

   try:
       import tkinter as tk
   except ImportError:
       import Tkinter as tk
   
   from tks.colors import ColorEntry
   
   if __name__ == '__main__':
       root = tk.Tk()
       root.title('Color Test')
       entry = ColorEntry(root, start_color='#fedcba')
       entry.grid(row=0, column=0, sticky=tk.EW)
       root.columnconfigure(0, weight=1)
       root.mainloop()


A Color Palette Widget
----------------------

To display the color palette widget shown
:ref:`in the gallery <gallery-color-palette>` the following code can be used.

::

   try:
       import tkinter as tk
   except ImportError:
       import Tkinter as tk
   
   from tks.color_palette import PaletteSelector
   
   if __name__ == '__main__':
       root = tk.Tk()
       root.title('Color Palette')
       entry = PaletteSelector(root)
       entry.grid(row=0, column=0)
       root.mainloop()

       