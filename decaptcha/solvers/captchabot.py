# -*- coding: utf-8 -*-
from __future__ import absolute_import

import settings
from errors import DecaptcherError
from .de_captcher import DecaptcherAPI


class CaptchabotAPI(DecaptcherAPI):
    account = settings.ACCOUNTS["captchabot"]
    url = "http://poster.captchabot.com"

    def _parse_solver_response(self, response):
        """ Возвращает код ошибки, код капчи из ответа сервера """
        parts = response.content.split("|")
        if len(parts) == 1:
            return parts[0], None
        elif len(parts) != 6:
            raise DecaptcherError("Wrong response format: %s" % response.content)
        return parts[0], parts[-1]
