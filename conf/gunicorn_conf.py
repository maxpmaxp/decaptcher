# -*- coding: utf-8 -*-

import multiprocessing

bind = "127.0.0.1:8020"
worker_class = "gevent"
loglevel = "debug"
workers = multiprocessing.cpu_count() * 2 + 1
