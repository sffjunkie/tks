# Copyright 2014, Simon Kennedy, code@sffjunkie.co.uk

import io
import os.path

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


RC_FILE = '.tksrc'

DEFAULT_CONFIG = u"""[font]

[color]
"""


class rcfile(object):
    def __init__(self, filename=''):
        self.parser = None

        if filename:
            self.filenames = [filename]
        else:
            self.filenames = None

    def read(self, extra_files=None):
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
        with open(filename, 'w') as fp:
            self.parser.write(fp)

    def set_to(self, data):
        self.parser = configparser.ConfigParser()
        ds = io.StringIO(data)
        ds.name = os.path.expanduser(os.path.join('~', RC_FILE))
        self.parser.readfp(ds)

    def has_section(self, section):
        return self.parser.has_section(section)

    def __getitem__(self, key):
        if '.' in key:
            path = key.split('.', 1)
            return self.parser.get(path[0], path[1])
        else:
            return self.parser.defaults()[key]

    def __setitem__(self, key, value):
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
        if '.' in key:
            path = key.split('.', 1)
            self.parser.remove_option(path[0], path[1])
        else:
            raise KeyError
