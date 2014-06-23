# -*- coding: utf-8 -*-
import os
from os.path import dirname, join, abspath


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return os.environ[setting]
    except KeyError:
        raise ValueError("Set the %s env variable" % setting)

APP_ACCESS = {
    'username': get_env_setting("APP_USERNAME"),
    'password': get_env_setting("APP_PASSWORD"),
}

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
MAX_ATTEMPTS_TO_SOLVE = 20

MAX_FAILS_PERCENTAGE = 70
FAILS_CHECK_INTERVAL = 60 * 15

ANTIGATE_MAX_PRICE = 1  # за 1000 капч
MINBID_CHECK_INTERVAL = 60 * 10

MAX_COSTS = {}
def get_max_cost(solver_name):
    return MAX_COSTS.get(solver_name, 1)


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


BANNED_SOLVERS = []


class CheckErrors:
    FAILS = 'fails'
    MINBID = 'minbid'

BLOCK_PERIODS = {
    CheckErrors.FAILS: 60 * 15,
    CheckErrors.MINBID: 60 * 10,
}


REDIS_CONF = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
}


ROOT_DIR = dirname(dirname(abspath(__file__)))
root = lambda *x: join(ROOT_DIR, *x)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(message)s',
            'datefmt': '%d/%m %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple',
        },
        'app': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': root('log/app.log'),
            'maxBytes': 5 * 2**20,  # 5MB
            'backupCount': 3
        },
    },
    'loggers': {
        'app': {
            'handlers': ['app'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
