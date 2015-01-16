#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
from setuptools import setup


def fread(filename):
    with open(filename) as f:
        return f.read()


setup(
    name='Flask-Alchemy',
    version='0.1',
    url='https://github.com/lepture/flask-alchemy',
    author='Hsiaoming Yang',
    author_email='me@lepture.com',
    description='The fastest markdown parser in pure Python',
    long_description=fread('README.rst'),
    license='BSD',
    py_modules=['flask_alchemy'],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Text Processing :: Markup',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
