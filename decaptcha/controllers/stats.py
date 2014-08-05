# -*- coding: utf-8 -*-
from __future__ import absolute_import

from bottle import template

import settings
import solvers.api as solvers
from errors import SolverError
from storage.redis import RedisStorage
from rechargers import RECHARGERS
from .auth import requires_auth


def get_balance_str(service):
    api = solvers.get_api(service)
    try:
        return api.balance()
    except SolverError:
        return '-'


@requires_auth
def show_stats():
    """ Renders stats page with
    - current balances for all solvers with the time of the recent payment
    - failures/success stats for past 24 hours
    """
    storage = RedisStorage()
    balances = {
        service: get_balance_str(service) for service in RECHARGERS.keys()
    }
    last_charge_dates = {
        service: storage.get_last_charge_date(service) or '-'
        for service in RECHARGERS.keys()
    }

    solvers = settings.Solvers.names
    fails = {s: storage.get_fails(s) for s in solvers}
    uses = {s: storage.get_uses(s) for s in solvers}

    context = {'balances': balances,
               'fails': fails,
               'uses': uses,
               'last_charge_dates': last_charge_dates}
    return template('stats', context)
