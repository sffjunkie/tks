# Copyright 2014-2018, Simon Kennedy, sffjunkie+code@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

import monkeypatch # pylint: disable=W0611

PACKAGE_DIR = 'src'

setup(name='tks',
      version='0.2.1',
      description="""A collection of Tk widgets""",
      long_description=
        """A collection of Tk widgets for dates, times and colors.
        For documentation see https://tks.readthedocs.io/en/latest/index.html""",
      author='Simon Kennedy',
      author_email='sffjunkie+code@gmail.com',
      url="https://github.com/sffjunkie/tks",
      license='Apache-2.0',
      package_dir={'': PACKAGE_DIR},
      packages=find_packages(PACKAGE_DIR),
      package_data={'tks': ['tks/*.txt'], },
      include_package_data=True,
      requires=['PIL'],
      extras_require={'idth': ['babel']},
)
