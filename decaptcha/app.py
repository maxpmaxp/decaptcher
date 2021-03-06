# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging.config

from bottle import Bottle, run

import settings
from controllers import solve_captcha, show_stats


logging.config.dictConfig(settings.LOGGING)

app = Bottle()
app.route('/', 'POST', solve_captcha)
app.route('/stats', 'GET', show_stats)


if __name__ == '__main__':
    run(app, host='localhost', port=8020, reloader=True, debug=True)
