#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from setuptools import setup

setup(
    name='framsreader',
    version='0.1',
    description='Files parser for framsticks.',
    long_description="Files parser for framsticks.",
    author='Michał Kempka',
    author_email='kempka.michal@gmail.com',

    install_requires=['numpy'],
    setup_requires=['numpy'],
    packages=['framsreader'],
    classifiers=[
        # Development Status :: 1 - Planning
        # Development Status :: 2 - Pre-Alpha
        # Development Status :: 3 - Alpha
        # Development Status :: 4 - Beta
        # Development Status :: 5 - Production/Stable
        # Development Status :: 6 - Mature
        # Development Status :: 7 - Inactive
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords=['framsticks']

)
