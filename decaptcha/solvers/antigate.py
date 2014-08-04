# -*- coding: utf-8 -*-
from __future__ import absolute_import

from antigate import AntiGate, AntiGateError
from grab.error import GrabNetworkError

import settings
from errors import SolverError


class MyAntiGate(AntiGate):
    def _go(self, *args, **kw):
        try:
            super(MyAntiGate, self)._go(*args, **kw)
        except (AntiGateError, GrabNetworkError) as error:
            raise SolverError(error)


class BaseAntigateAPI(object):
    api_key = None
    domain = None

    def __init__(self, api_key=None, domain=None):
        self._api = MyAntiGate(
            key=(api_key or self.api_key),
            domain=(domain or self.domain),
            grab_config={'connect_timeout': settings.NET_TIMEOUT},
        )

    def solve(self, captcha_raw, **kw):
        api = self._api
        try:
            captcha_id = api.send(captcha_raw, binary=True)
            return api.get(captcha_id)
        except AntiGateError as error:
            raise SolverError(error)

    def balance(self):
        return self._api.balance()


class AntigateAPI(BaseAntigateAPI):
    api_key = settings.API_KEYS['antigate']
    domain = 'antigate.com'

    def minbid(self):
        return self._api.load()['minbid']
