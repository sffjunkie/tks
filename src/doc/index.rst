tkStuff v\ |release|
====================

.. toctree::
   :maxdepth: 1
   :includehidden:

   gallery
   examples
   dates
   times
   colors
   fs
   passwords
   misc

tkStuff is a collection of Tkinter widgets for dates, times and colors.

For each of these there is an entry widget and a dialog for obtaining values
from the user.

For colors, each element of the dialog is also exposed as a class (classes
exist for a :ref:`color wheel <color-wheel-class>`,
:ref:`3 element sliders <color-slider-classes>`,
:ref:`a color information square <color-square-class>`.)

A :ref:`color palette <color-palette-selector-class>` widget is also provided
access to the set of colors defined by X11 and CSS3.

Finally there are 2 widgets to display
:ref:`tints and shades <color-tints-and-shades-classes>` of a color.

Examples of these can be seen in the :ref:`gallery` and some code examples in
the :ref:`code-examples` section.

License
=======

This module is licensed under the terms of the `Apache`_ V2.0 license.

Dependencies
============

tkStuff has one required dependency and an optional one. Either
`Pillow`_ or `PIL`_ are required and `Babel`_ is optional.

* PIL is used to generate the color wheel.

* Babel is used to provide improved date and time handling and if Babel not
  present dates are limited to the ISO 8601 YYYY-MM-DD format and times
  are limited to a 24 hour clock.

Installation
============

Installation is performed from `PyPi`_ via :command:`pip` ::

   pip install tks

This doesn't automatically install Babel. To do this either install it
separately or use the following command for the
**i**\mproved **d**\ate/**t**\ime **h**\andling ::

   pip install tks[idth]

Contact
=======

Simon Kennedy <sffjunkie+code@gmail.com>

Version History
===============

======== =======================================================================
Version  Description
======== =======================================================================
0.2      * Added :class:`\*Entry` classes for files, directories and passwords.
         * Added functions to set a Tk window icon.
         * :class:`\*Entry` classes now take a Tk variable subclass
           instead of a value.
         * Colors and fonts to be used for interface elements can be specified
           using an `rc` file.
         * Added a decimal places parameter to the color to string conversion
           functions.
-------- -----------------------------------------------------------------------
0.1      Initial release
======== =======================================================================

.. _Apache: http://www.opensource.org/licenses/apache2.0.php
.. _PyPi: http://pypi.python.org/pypi/
.. _Babel: https://pypi.python.org/pypi/Babel
.. _Pillow: https://pypi.python.org/pypi/Pillow/2.4.0
.. _PIL: https://pypi.python.org/pypi/PIL
