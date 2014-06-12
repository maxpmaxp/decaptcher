# -*- coding: utf-8 -*-
from __future__ import absolute_import

import settings
from .antigate import BaseAntigateAPI


class CaptchabotAPI(BaseAntigateAPI):
    api_key = settings.API_KEYS['captchabot']
    domain = "captchabot.com"
