#!/usr/bin/env python3

from setuptools import setup

setup(
    name='markers-to-gma2-timecode',
    version='0.0.1',
    py_modules=['midi2gma2tc'],
    install_requires=[
        'Click',
        'mido',
    ],
    entry_points='''
        [console_scripts]
        midi2gma2tc=midi2gma2tc:midi2gma2tc
    ''',
)
