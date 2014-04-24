#!/usr/bin/env python
"""
steelscript-appfwk-business-hours
==========

A plugin for SteelScript App Framework to enable Business Hour reports.

"""
import os

try:
    from setuptools import setup, find_packages, Command
    packagedata = True
except ImportError:
    from distutils.core import setup
    from distutils.cmd import Command
    packagedata = False

    def find_packages(path='steelscript'):
        return [p for p, files, dirs in os.walk(path) if '__init__.py' in files]

from gitpy_versioning import get_version

setup_args = {
    'name':               'steelscript.appfwk.business-hours',
    'namespace_packages': ['steelscript'],
    'version':            get_version(),
    'author':             'Riverbed Technology',
    'author_email':       'eng-github@riverbed.com',
    'url':                'http://pythonhosted.org/steelscript',
    'description':        'Business-Hours plugin for SteelScript Application Framework',

    'long_description': """Business-Hours for SteelScript Application Framework
====================================================

SteelScript is a collection of libraries and scripts in Python and JavaScript for
interacting with Riverbed Technology devices.

For a complete guide to installation, see:

http://pythonhosted.org/steelscript/install.html
    """,
    'license': 'MIT',

    'platforms': 'Linux, Mac OS, Windows',

    'classifiers': (
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
    ),

    'packages': find_packages(),

    'scripts': None,

    'install_requires': (
        'steelscript.common>=0.6',
        'steelscript.netprofiler>=0.1',
        #'steelscript.appfwk.core>=0.1',
    ),

    'tests_require': (),

    'entry_points': {
        'portal.plugins': [
            'business_hours = steelscript.appfwk.business_hours.plugin:BusinessHoursPlugin'
        ],
    },
}

if packagedata:
    setup_args['include_package_data'] = True

setup(**setup_args)
