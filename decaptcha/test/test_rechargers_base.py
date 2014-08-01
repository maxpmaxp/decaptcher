# -*- coding: utf-8 -*-

from mock import patch

import settings
from rechargers.base import RechargerViaAvangate, find_elem


@patch.object(RechargerViaAvangate, 'balance_checker')
@patch.object(RechargerViaAvangate, 'data_cls')
def test_get_sum_to_recharge(data_cls, balance_checker):
    recharger = RechargerViaAvangate({}, {})
    get_sum = recharger.get_sum_to_recharge
    lo, hi = settings.MIN_RECHARGE_AMOUNT, settings.MAX_RECHARGE_AMOUNT

    # any balance greater than MIN
    balance_checker.return_value = settings.MIN_BALANCE + 1
    assert get_sum() == 0

    # any balance less than MIN
    for balance in range(0, settings.MIN_BALANCE + 1):
        balance_checker.return_value = balance
        assert lo <= get_sum() <= hi


def test_find_elem():
    html = "<html><form name='dl'></form></html>"
    assert find_elem(html, "form[name=dl]")
    assert not find_elem(html, "form[name=dl2]")
