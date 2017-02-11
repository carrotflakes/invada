# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from os.path import join, dirname
import sys
sys.path.insert(0, join(dirname(__file__), 'invada'))
from version import __version__
sys.path.pop(0)

setup(
    name='invada',
    version=__version__,
    description='Dialogue engine',
    author='carrotflakes',
    url='https://github.com/carrotflakes/invada',
    author_email='carrotflakes@gmail.com',
    license='MIT',
    keywords='',
    packages=find_packages(),
    install_requires=['parsy', 'marisa-trie']
)
