# -*- coding: utf-8 -*-

from os.path import dirname, join, abspath
import multiprocessing

loglevel = "info"
workers = multiprocessing.cpu_count() * 2 + 1

_ROOT_DIR = dirname(dirname(abspath(__file__)))
pythonpath = join(_ROOT_DIR, 'decaptcha')
accesslog = join(_ROOT_DIR, 'log/gunicorn.access.log')
errorlog = join(_ROOT_DIR, 'log/gunicorn.error.log')
