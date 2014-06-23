# -*- coding: utf-8 -*-

import multiprocessing
import sys
from os.path import dirname, join, abspath

ROOT_DIR = dirname(dirname(abspath(__file__)))
APP_DIR = join(ROOT_DIR, 'decaptcha')
# adding app's dir to PATH to be able to import settings
sys.path.insert(0, APP_DIR)

from settings import LOG_DIR, APP_ADDRESS, get_var

accesslog = join(LOG_DIR, 'gunicorn.access.log')
errorlog = join(LOG_DIR, 'gunicorn.error.log')
loglevel = "info"

bind = APP_ADDRESS
worker_class = get_var('gunicorn', 'worker_cls', 'sync')
workers = multiprocessing.cpu_count() * 2 + 1
