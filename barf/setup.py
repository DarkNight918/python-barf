#! /usr/bin/env python

from setuptools import setup
from setuptools import find_packages

setup(
    author           = 'Christian Heitman',
    author_email     = 'cnheitman@fundacionsadosky.org.ar',
    description      = 'A multiplatform open source Binary Analysis and Reverse engineering Framework',
    install_requires = [
        'networkx',
        'pybfd',
        'pydot',
        'pygments',
        'pyparsing',
        'sphinx',
    ],
    license          = 'BSD 2-Clause',
    name             = 'barf',
    packages         = find_packages(),
    url              = 'http://bitbucket.org/cnheitman/barf-project',
    scripts          = [
        'tools/gadgets/BARFgadgets'
    ],
    version          = '0.1',
    zip_safe         = False
)
