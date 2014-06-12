# -*- coding: utf-8 -*-

import numbers

import pytest

from solvers.api_list import SOLVER_APIS


@pytest.fixture(params=SOLVER_APIS.values())
def solver_api(request):
    return request.param


def test_getting_balance(solver_api):
    assert isinstance(solver_api.balance(), numbers.Number)
