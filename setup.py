#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


required = ["poster"]


setup(
    name='iron-worker',
    version='0.0.10',
    description='The Python client for IronWorker, a cloud service for background processing.',
    long_description='IronWorker is a background processing and task queuing system that lets your applications use the cloud to do their heavy lifting. This is the Python library to interface with the API.',
    keywords=['iron', 'ironio', 'iron.io', 'iron-io', 'ironworker', 'iron-worker', 'iron_worker', 'worker', 'cloud', 'task queue', 'background processing'],
    author='Iron.io',
    author_email="support@iron.io",
    url='http://iron.io/products/worker',
    install_requires=required,
    packages=[ 'iron_worker' ],
)
