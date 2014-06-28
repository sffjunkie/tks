Welcome to tkStuff
==================

.. toctree::
   :maxdepth: 3
   :hidden:
   
   gallery
   module

tkStuff is a collection of Tkinter widgets for dates, times and colors.

For each there is an entry widget and a dialog for obtaining values from
the user.

For colors, each element of the dialog is also exposed as a class (classes
exist for a :ref:`color wheel <color-wheel-class>`,
:ref:`3 element sliders <color-slider-classes>`,
:ref:`a color information square <color-square-class>`.)

A :ref:`color palette <color-palette-selector-class>` widget is also provides
access to the set of colors defined by X11 and CSS3.

Examples of these can be seen in the :ref:`gallery`\.

License
=======

This module is licensed under the terms of the `Apache`_ V2.0 license.
    
Dependencies
============

tkStuff has one external optional dependency on `babel`_ which provides
improved date and time handling.

If not present dates are limited to the ISO 8601 YYYY-MM-DD format and times
are limited to a 24 hour clock.

Installation
============

Installation is performed from `PyPi`_ via :command:`pip` ::

   pip install tks

.. _Apache: http://www.opensource.org/licenses/apache2.0.php
.. _PyPi: http://pypi.python.org/pypi/
.. _Babel: https://pypi.python.org/pypi/Babel
