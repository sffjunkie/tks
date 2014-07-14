# Copyright 2014, Simon Kennedy, sffjunkie+code@gmail.com

"""Provides a class :class:`rcfile` to load configuration information
from a file."""

import io
import sys
import os.path

if sys.version_info >= (3, 0):
    import configparser
else:
    import ConfigParser as configparser


RC_FILE = '.tksrc'

DEFAULT_CONFIG = u"""[font]
#text=Calibri, 9
#monospace=Consolas, 9

[color]
#fill=white
#select=#9de5eb
#select_dark=#58B1B7
#header=white
#outline=#ccc
#invalid=red
"""


class rcfile(object):
    """A Resource Configuration file.

    :param filename: A default filename to read from.
    :type filename:  str
    """

    def __init__(self, filename=''):
        self.parser = None

        if filename:
            self.filenames = [filename]
        else:
            self.filenames = None

    def read(self, extra_files=None):
        """Read configuration information from the filename specified in the
        constructor plus any extra files specified as a parameter.

        :param extra_files: A list of extra filenames to load
        :type extra_files:  [str]
        """

        default_config_file = os.path.expanduser(os.path.join('~', RC_FILE))

        if not self.filenames:
            self.filenames = [default_config_file]

        if extra_files:
            self.filenames.extend(extra_files)

        self.parser = configparser.ConfigParser()

        existing = False
        for filename in self.filenames:
            if os.path.exists(filename):
                existing = True

        if existing:
            self.parser.read(self.filenames)
        else:
            ds = io.StringIO(DEFAULT_CONFIG)
            self.parser.readfp(ds, default_config_file)

        return self.parser

    def write(self, filename):
        """Write the configuration to a file.

        :param filename: Filename to write to.
        :type filename:  str
        """

        with open(filename, 'w') as fp:
            self.parser.write(fp)

    def reads(self, data):
        """Load configuration from a string."""

        self.parser = configparser.ConfigParser()
        ds = io.StringIO(data)
        ds.name = os.path.expanduser(os.path.join('~', RC_FILE))
        self.parser.readfp(ds)

    def has_section(self, section):
        """Determine if  section is found within the configuration."""

        return self.parser.has_section(section)

    def __getitem__(self, key):
        """Get an item from the configuration."""

        if '.' in key:
            path = key.split('.', 1)
            return self.parser.get(path[0], path[1])
        else:
            return self.parser.defaults()[key]

    def __setitem__(self, key, value):
        """Set an item in the configuration."""

        if not self.parser:
            self.parser = configparser.ConfigParser()

        if '.' in key:
            path = key.split('.', 1)

            if not self.parser.has_section(path[0]):
                self.parser.add_section(path[0])

            self.parser.set(path[0], path[1], value)
        else:
            raise KeyError

    def __delitem__(self, key):
        """Delete an item in the configuration."""

        if '.' in key:
            path = key.split('.', 1)
            self.parser.remove_option(path[0], path[1])
        else:
            raise KeyError
