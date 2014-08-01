# -*- coding: utf-8 -*-
from datetime import timedelta
from os.path import dirname, join, abspath, exists
from ConfigParser import SafeConfigParser, NoOptionError

DEBUG = True

CONF_FILE = '/etc/decaptcher.conf'
if not exists(CONF_FILE):
    raise ValueError("Config file %r doesn't exist" % CONF_FILE)

conf = SafeConfigParser()
conf.read(CONF_FILE)

def get_var(section, option, default=None):
    try:
        return conf.get(section, option)
    except NoOptionError:
        if default is not None:
            return default
        else:
            raise

def get_account(service):
    return {'username': get_var(service, 'user'),
            'password': get_var(service, 'password')}


APP_ACCESS = get_account('self')

ACCOUNTS = {s: get_account(s) for s in
            ('de_captcher', 'captchabot', 'deathbycaptcha', 'antigate')}

API_KEYS = {
    'antigate': get_var('antigate', 'api_key'),
    'captchabot': get_var('captchabot', 'api_key'),
    'deathbycaptcha': get_var('deathbycaptcha', 'api_key'),
}

APP_ADDRESS = get_var('common', 'address')
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
LOG_DIR = get_var('common', 'logdir', join(ROOT_DIR, 'log'))

if not exists(LOG_DIR):
    raise ValueError("Log dir %r doesn't exist" % LOG_DIR)

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
            'filename': join(LOG_DIR, 'app.log'),
            'maxBytes': 5 * 2**20,  # 5MB
            'backupCount': 3
        },
        'recharger': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': join(LOG_DIR, 'recharges.log'),
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
        'recharger': {
            'handlers': ['recharger'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

### rechargers conf

MIN_BALANCE = 150
MIN_RECHARGE_AMOUNT = 150
MAX_RECHARGE_AMOUNT = 300
CHECK_BALANCE_INTERVAL = timedelta(hours=4).total_seconds()

def read_config_section(section, keys):
    return {key: get_var(section, key) for key in keys}

CARD_USER_KEYS = [
    'firstname',
    'lastname',
    'address',
    'city',
    'zipcode',
    'state',
    'email',
]
CARD_INFO_KEYS = [
    'number',
    'expmonth',
    'expyear',
    'cvv2',
    'nameoncard',
]
CARD_USER = read_config_section('card_user', CARD_USER_KEYS)
CARD_INFO = read_config_section('card_info', CARD_INFO_KEYS)
