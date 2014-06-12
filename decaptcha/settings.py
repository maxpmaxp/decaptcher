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


class SolverRanks:
    PRIMARY = 1
    SECONDARY = 2
    ADDITIONAL = 3

    @classmethod
    def lower(cls, rank):
        return rank + 1 if (rank != cls.ADDITIONAL) else rank


class Solvers:
    ANTIGATE = 'antigate'
    CAPTCHABOT = 'captchabot'
    DE_CAPTCHER = 'de_captcher'
    DEATH_BY_CAPTCHA = 'deathbycaptcha'

    ranks = {
        ANTIGATE: SolverRanks.PRIMARY,
        CAPTCHABOT: SolverRanks.SECONDARY,
        DE_CAPTCHER: SolverRanks.ADDITIONAL,
        DEATH_BY_CAPTCHA: SolverRanks.ADDITIONAL,
    }
    names = ranks.keys()
