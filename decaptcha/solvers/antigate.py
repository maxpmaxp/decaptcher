# -*- coding: utf-8 -*-
from __future__ import absolute_import

from antigate import AntiGate, AntiGateError

import settings
from errors import SolverError


class MyAntiGate(AntiGate):
    def _go(self, *args, **kw):
        try:
            super(MyAntiGate, self)._go(*args, **kw)
        except AntiGateError as error:
            raise SolverError(error.message)


class BaseAntigateAPI(object):
    api_key = None
    domain = None

    def __init__(self, api_key=None, domain=None):
        self._api = MyAntiGate(
            key=(api_key or self.api_key),
            domain=(domain or self.domain),
            grab_config={'connect_timeout': settings.NET_TIMEOUT},
        )

    def solve(self, captcha_img):
        api = self._api
        captcha_id = api.send(captcha_img, binary=True)
        return api.get(captcha_id)

    def balance(self):
        return self._api.balance()


class AntigateAPI(BaseAntigateAPI):
    api_key = settings.API_KEYS['antigate']
    domain = 'antigate.com'

    def minbid(self):
        return self._api.load()['minbid']
