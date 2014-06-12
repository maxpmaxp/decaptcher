# -*- coding: utf-8 -*-
"""
Набор методов для доступа к сервисам-расшифровщикам
"""
from __future__ import absolute_import

from settings import Solvers
from .api_list import get_api


_SOLVERS_SORTED_BY_RANK = [
    {
        'name': Solvers.ANTIGATE,
        'rank': Solvers.ranks[Solvers.ANTIGATE],
        'cb': get_api(Solvers.ANTIGATE).solve,
    },
    {
        'name': Solvers.CAPTCHABOT,
        'rank': Solvers.ranks[Solvers.CAPTCHABOT],
        'cb': get_api(Solvers.CAPTCHABOT).solve,
    },
    {
        'name': Solvers.DEATH_BY_CAPTCHA,
        'rank': Solvers.ranks[Solvers.DEATH_BY_CAPTCHA],
        'cb': get_api(Solvers.DEATH_BY_CAPTCHA).solve,
    },
    {
        'name': Solvers.DE_CAPTCHER,
        'rank': Solvers.ranks[Solvers.DE_CAPTCHER],
        'cb': get_api(Solvers.DE_CAPTCHER).solve,
    },
]
LOWEST_SOLVER = _SOLVERS_SORTED_BY_RANK[-1]['name']


def get_highest_notblocked(storage):
    for solver in _SOLVERS_SORTED_BY_RANK:
        if not storage.is_blocked(solver['name']):
            return solver
    return _SOLVERS_SORTED_BY_RANK[-1]


def get_by_name(name):
    for solver in _SOLVERS_SORTED_BY_RANK:
        if solver['name'] == name:
            return solver


def get_next(solver_name):
    solvers = _SOLVERS_SORTED_BY_RANK
    solver = get_by_name(solver_name)
    index_of_solver = solvers.index(solver)
    try:
        return solvers[index_of_solver + 1]
    except IndexError:
        return solvers[-1]
