#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re

__version__ = find_version('rdflib_web/__init__.py')

config = dict(
    name = 'rdflib-web',
    version = __version__,
    description = "RDFLib Web Apps.",
    author = "Gunnar Aastrand Grimnes",
    author_email = "gromgull@gmail.com",
    url = "https://github.com/RDFLib/rdflib-web",
    license = "BSD",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python",
                   "License :: OSI Approved :: BSD License",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Operating System :: OS Independent",
                   ],
    packages = ['rdflib_web'],
    package_dir = { 'rdflib_web': 'rdflib_web' },
    package_data = { 'rdflib_web': ['templates/*.html','static/*',]}
)

from setuptools import setup


install_requires = [
    'flask',
    'rdflib>=5.0',
]

tests_require = install_requires
                      
extras_require = { 
    "web-conneg": ["mimeparse"],

    }


config.update(
    entry_points = {
        'console_scripts': [
            'rdfsparqlapp = rdflib_web.endpoint:main',
            'rdflodapp = rdflib_web.lod:main',                
        ],
        'rdf.plugins.serializer': [
            'html = rdflib_web.htmlresults:HTMLSerializer',
        ],
        'rdf.plugins.resultserializer': [
            'html = rdflib_web.htmlresults:HTMLResultSerializer',
        ],

    },
    install_requires = install_requires,
    tests_require = tests_require,
    extras_require = extras_require 
)
    
setup(**config)

