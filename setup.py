#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


required = [ ]


setup(
    name='iron_worker',
    version='0.0.1',
    description='A Python client for iron.io, the leader in cloud queueing systems.',
    author='iron.io',
    url='http://iron.io',
    install_requires=required,
    packages=[ 'iron_worker' ],
    package_data = { '' : [ 'poster/*' ] },
)
