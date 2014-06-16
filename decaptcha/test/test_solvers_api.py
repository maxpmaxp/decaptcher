# -*- coding: utf-8 -*-

from mock import MagicMock, patch

import settings
from settings import Solvers
from solvers.api import (
    get_highest_notblocked, get_next, get_by_name, is_banned,
    _SOLVERS_SORTED_BY_RANK, LOWEST_SOLVER)
from test_app import reset_mocks


SOLVERS = _SOLVERS_SORTED_BY_RANK

def lowest_solver():
    assert LOWEST_SOLVER == SOLVERS[-1]['name']


def test_get_solver_by_name():
    for name in Solvers.names:
        assert get_by_name(name)['name'] == name


def test_is_banned():
    backup = settings.BANNED_SOLVERS
    s = 'some service'
    settings.BANNED_SOLVERS = []
    assert not is_banned(s)
    settings.BANNED_SOLVERS = [s]
    assert is_banned(s)
    settings.BANNED_SOLVERS = backup


def _all_except_deathbycaptcha(solver_name):
    return solver_name != Solvers.DEATH_BY_CAPTCHA


@patch('solvers.api.is_banned')
def test_get_highest_notblocked_solver(is_banned):
    storage = MagicMock()

    is_banned.return_value = False
    storage.is_blocked.return_value = False
    assert get_highest_notblocked(storage)['name'] == SOLVERS[0]['name']
    assert is_banned.call_count == 1
    assert storage.is_blocked.call_count == 1
    reset_mocks(locals())

    is_banned.return_value = True
    storage.is_blocked.return_value = False
    assert get_highest_notblocked(storage)['name'] == SOLVERS[-1]['name']
    assert is_banned.call_count == len(SOLVERS)
    reset_mocks(locals())

    is_banned.return_value = False
    storage.is_blocked.side_effect = _all_except_deathbycaptcha
    assert get_highest_notblocked(storage)['name'] == Solvers.DEATH_BY_CAPTCHA


def test_get_next_solver(stub_storage):
    current_solver = SOLVERS[0]
    for solver in SOLVERS[1:]:
        assert solver == get_next(current_solver['name'])
        current_solver = solver
    assert SOLVERS[-1] == get_next(SOLVERS[-1]['name'])
