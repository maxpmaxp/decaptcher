# -*- coding: utf-8 -*-
from __future__ import absolute_import

from bottle import auth_basic

import settings


def check_user(username, password):
    user = settings.APP_ACCESS
    return username == user['username'] and password == user['password']

requires_auth = auth_basic(check_user)
