# -*- coding: utf-8 -*-
import os


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return os.environ[setting]
    except KeyError:
        raise ValueError("Set the %s env variable" % setting)


ANTIGATE_API_KEY = get_env_setting('ANTIGATE_API_KEY')
CAPTCHABOT_API_KEY = get_env_setting('CAPTCHABOT_API_KEY')
