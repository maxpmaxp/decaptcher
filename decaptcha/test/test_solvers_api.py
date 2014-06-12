# -*- coding: utf-8 -*-

from mock import MagicMock

from settings import Solvers
from solvers.api import (
    get_highest_notblocked, get_next, get_by_name,
    _SOLVERS_SORTED_BY_RANK, LOWEST_SOLVER)


SOLVERS = _SOLVERS_SORTED_BY_RANK

def lowest_solver():
    assert LOWEST_SOLVER == SOLVERS[-1]['name']


def test_get_solver_by_name():
    for name in Solvers.names:
        assert get_by_name(name)['name'] == name


def _all_except_deathbycaptcha(solver_name):
    return solver_name != Solvers.DEATH_BY_CAPTCHA


def test_get_highest_notblocked_solver():
    storage = MagicMock()

    storage.is_blocked.return_value = False
    assert get_highest_notblocked(storage)['name'] == Solvers.ANTIGATE

    storage.is_blocked.return_value = True
    assert get_highest_notblocked(storage)['name'] == SOLVERS[-1]['name']

    storage.is_blocked.side_effect = _all_except_deathbycaptcha
    assert get_highest_notblocked(storage)['name'] == Solvers.DEATH_BY_CAPTCHA


def test_get_next_solver(stub_storage):
    current_solver = SOLVERS[0]
    for solver in SOLVERS[1:]:
        assert solver == get_next(current_solver['name'])
        current_solver = solver
    assert SOLVERS[-1] == get_next(SOLVERS[-1]['name'])
