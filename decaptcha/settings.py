# -*- coding: utf-8 -*-
import os


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return os.environ[setting]
    except KeyError:
        raise ValueError("Set the %s env variable" % setting)

DE_CAPTCHER_ACCOUNT = {
    'username': get_env_setting('DE_CAPTCHER_USERNAME'),
    'password': get_env_setting('DE_CAPTCHER_PASSWORD'),
}

API_KEYS = {
    'antigate': get_env_setting('ANTIGATE_API_KEY'),
    'captchabot': get_env_setting('CAPTCHABOT_API_KEY'),
    'deathbycaptcha': get_env_setting('DEATHBYCAPTCHA_API_KEY'),
}

NET_TIMEOUT = 15
