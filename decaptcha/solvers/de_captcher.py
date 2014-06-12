# -*- coding: utf-8 -*-

import requests

import settings
from errors import DecaptcherError


class ResultCodes:
    OK = "0"
    GENERAL = "-1"
    STATUS = "-2"
    NET_ERROR = "-3"
    TEXT_SIZE = "-4"
    OVERLOAD = "-5"
    BALANCE = "-6"
    TIMEOUT = "-7"
    BAD_PARAMS = "-8"
    UNKNOWN = "-200"

    msg = {
        OK: 'everything went OK',
        GENERAL: 'general internal error',
        STATUS: 'status is not correct',
        NET_ERROR: 'network data transfer error',
        TEXT_SIZE: 'text is not of an appropriate size',
        OVERLOAD: 'servers overloaded',
        BALANCE: 'not enough funds to complete the request',
        TIMEOUT: 'request timed out',
        BAD_PARAMS: 'provided parameters are not good for this function',
        UNKNOWN: 'unknown error',
    }


class DecaptcherAPI(object):
    _url = "http://poster.de-captcher.com/"
    _account = settings.DE_CAPTCHER_ACCOUNT

    def __init__(self, url=None, account=None):
        if url:
            self._url = url
        if account:
            self._account = account


    def _post(self, data):
        data.update(self._account)
        response = requests.post(self._url, data=data,
                                 timeout=settings.NET_TIMEOUT)
        if response.status_code != 200:
            raise DecaptcherError("%s HTTP status code" % response.status_code)
        return response


    def _parse_solver_response(self, response):
        parts = response.content.split("|")
        if len(parts) != 6:
            raise DecaptcherError("Wrong response format")
        error_code, captcha_code = parts[0], parts[-1]

        if error_code == ResultCodes.OK:
            return captcha_code

        try:
            raise DecaptcherError(ResultCodes.msg[error_code])
        except KeyError:
            raise DecaptcherError("Unknown error code: %r" % error_code)


    def solve(self, captcha_img):
        data = {"function": "picture2",
                "pict_to": "0",
                "pict_type": "0",
                "pict": captcha_img}
        response = self._post(data)
        return self._parse_solver_response(response)


    def balance(self):
        response = self._post({"function": "balance"})
        try:
            return float(response.content)
        except ValueError:
            return DecaptcherError("%s isn't a number" % response.content)
