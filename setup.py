#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

required = [
    'pytest',
    'requests',
    'requests_oauthlib',
    'httplib2==0.9.1',
    'python-dateutil'
]

setup(
    name='readability-api',
    version='1.0.0',
    description='Python client for the Readability Reader and Parser APIs.',
    long_description=open('README.rst').read(),
    author='The Readability Team',
    author_email='philip@readability.com',
    url='https://github.com/arc90/python-readability-api',
    packages=['readability'],
    install_requires=required,
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
    ),
)
