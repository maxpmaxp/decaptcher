# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


def split_and_strip(string):
    return filter(bool, (s.strip() for s in string.split('\n')))

setup(
    name = 'decaptcha',
    description = 'Decaptcha API aggregator',
    packages = find_packages(),
    include_package_data = True,
    install_requires = split_and_strip('''
        bottle==0.12.7
        gevent==1.0.1
        antigate==1.3
        redis==2.10.1
        requests==2.3.0
        gunicorn==18.0
    '''),
)
