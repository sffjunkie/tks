# -*- coding: utf-8 -*-

"""Base i18n functions"""

import os
import sys
import locale
import gettext

# Change this variable to your app name!
#  The translation files will be under
#  @LOCALE_DIR@/@LANGUAGE@/LC_MESSAGES/@APP_NAME@.mo
APP_NAME = "tks"

APP_DIR = os.path.dirname(os.path.abspath(__file__))
# .mo files will then be located in APP_Dir/i18n/LANGUAGECODE/LC_MESSAGES/
LOCALE_DIR = APP_DIR

# Now we need to choose the language. We will provide a list, and gettext
# will use the first translation available in the list
DEFAULT_LANGUAGES = os.environ.get('LANGUAGE', '').split(':')
if 'en_US' not in DEFAULT_LANGUAGES:
    DEFAULT_LANGUAGES += ['en_US']

lc, encoding = locale.getdefaultlocale()
if lc:
    languages = [lc]

# Concat all languages (env + default locale),
#  and here we have the languages and location of the translations
languages += DEFAULT_LANGUAGES
mo_location = LOCALE_DIR

gettext.bind_textdomain_codeset(APP_NAME, codeset='UTF-8')
language = gettext.translation(APP_NAME, mo_location,
                               languages=languages, fallback=True)

if sys.version_info < (3, 0):
    language.gettext = language.ugettext
