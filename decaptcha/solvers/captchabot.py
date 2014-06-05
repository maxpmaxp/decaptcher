# -*- coding: utf-8 -*-

from antigate import AntiGate, AntiGateError

import settings


api = AntiGate(settings.CAPTCHABOT_API_KEY, domain="captchabot.com")


def solve(captcha_img):
    try:
        captcha_id = api.send(captcha_img, binary=True)
        return api.get(captcha_id)
    except AntiGateError as e:
        return None, e.message


def get_balance():
    return 1
