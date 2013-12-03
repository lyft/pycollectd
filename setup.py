# -*- coding: utf-8 -*-
#
# © 2013 Lyft, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.  You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pip.req import parse_requirements
from setuptools import setup, find_packages

import os


# We use the version to construct the DOWNLOAD_URL.
VERSION = '0.0.1'

# URL to the repository on Github.
REPO_URL = 'https://github.com/lyft/pycollectd'

# Github will generate a tarball as long as you tag your releases, so don't
# forget to tag!
DOWNLOAD_URL = ''.join((REPO_URL, '/tarball/release/', VERSION))

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS = os.path.join(BASE_DIR, 'requirements.pip')

# We want to install all the dependencies of the library as well, but we
# don't want to duplicate the dependencies both here and in
# requirements.pip. Instead we parse requirements.pip to pull in our
# dependencies.
#
# A requirement file can contain comments (#) and can include some other
# files (--requirement or -r), so we need to use pip's parser to get the
# final list of dependencies.
DEPENDENCIES = [unicode(package.req)
                for package in parse_requirements(REQUIREMENTS)]


setup(
    name='pycollectd',
    version=VERSION,
    author='Paul Lathrop',
    author_email='paul@tertiusfamily.net',
    maintainer='Paul Lathrop',
    maintainer_email='paul@tertiusfamily.net',
    description='Framework for writing collectd plugins in python.',
    long_description="""
    Framework for writing collectd plugins in python. These plugins are
    intended to be used with collectd's 'python' plugin.
    """,
    url=REPO_URL,
    download_url=DOWNLOAD_URL,
    license='Apache Software License',
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: System :: Monitoring',
    ],
)
