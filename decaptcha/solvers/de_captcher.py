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
    url = "http://poster.de-captcher.com/"
    account = settings.DE_CAPTCHER_ACCOUNT

    def __init__(self, url=None, account=None):
        if url:
            self.url = url
        if account:
            self.account = account


    def _post(self, data, files=None):
        data.update(self.account)
        request_params = {
            'url': self.url,
            'data': data,
            'files': files,
            'timeout': settings.NET_TIMEOUT,
        }
        response = requests.post(**request_params)
        if response.status_code != 200:
            raise DecaptcherError("%s HTTP status code" % response.status_code)
        return response


    def _parse_solver_response(self, response):
        """ Возвращает код ошибки, код капчи из ответа сервера """
        parts = response.content.split("|")
        if len(parts) != 6:
            raise DecaptcherError("Wrong response format: %s" % response.content)
        return parts[0], parts[-1]


    def _process_solver_response(self, response):
        error_code, captcha_code = self._parse_solver_response(response)
        if error_code == ResultCodes.OK:
            return captcha_code
        try:
            raise DecaptcherError(ResultCodes.msg[error_code])
        except KeyError:
            raise DecaptcherError("Unknown error code: %r" % error_code)


    def solve(self, captcha_file, **kw):
        data = {"function": "picture2",
                "pict_type": kw.get("pict_type") or "0",
                "pict_to": "0",
                "submit": "Send"}
        response = self._post(data, files={'pict': captcha_file})
        return self._process_solver_response(response)


    def balance(self):
        response = self._post({"function": "balance"})
        try:
            return float(response.content)
        except ValueError:
            return DecaptcherError("%s isn't a number" % response.content)
