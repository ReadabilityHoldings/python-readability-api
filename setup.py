#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup

required = [
    'requests',
    'requests_oauthlib',
    'httplib2==0.8.0',
    'python-dateutil'
]

setup(
    name='readability-api',
    version='0.3.0',
    description='Python wrapper for the Readability API.',
    long_description=open('README.rst').read(),
    author='The Readability Team',
    author_email='feedback@readability.com',
    url='https://www.readability.com/developers/api',
    packages= ['readability'],
    install_requires=required,
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ),
)
