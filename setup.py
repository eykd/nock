# -*- coding: utf-8 -*-
"""setup.py -- setup file for nock module.
"""
import sys
import os

from setuptools import setup

TESTS_REQUIRE = [
    'nose',
]

README = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst')

SETUP = dict(
    name = "nock",
    py_modules = ['nock'],
    tests_require = TESTS_REQUIRE,
    test_suite = 'nose.collector',

    package_data = {
        '': ['*.txt', '*.html', '*.rst'],
    },
    zip_safe = False,

    version = "0.1.1",
    description = "Nock, Nock. Hoon's there?",
    long_description = open(README).read(),
    author = "David Eyk",
    author_email = "david.eyk@gmail.com",
    url = "http://github.com/eykd/nock",
    license = 'BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries',
    ],
)

setup(**SETUP)
