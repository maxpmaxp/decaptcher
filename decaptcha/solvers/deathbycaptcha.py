# -*- coding: utf-8 -*-
from __future__ import absolute_import

import settings
from .de_captcher import DecaptcherAPI


class DeathbycaptchaAPI(DecaptcherAPI):
    account = settings.ACCOUNTS['deathbycaptcha']
    url = "http://api.dbcapi.me/decaptcher"
