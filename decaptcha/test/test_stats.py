# -*- coding: utf-8 -*-

from mock import patch

from settings import Solvers


@patch("solvers.de_captcher.DecaptcherAPI.balance")
@patch("solvers.antigate.AntigateAPI.balance")
def test_stats(antigate_balance, decaptcher_balance, app):
    b1, b2 = '137', '150.49'
    antigate_balance.return_value = b1
    decaptcher_balance.return_value = b2
    resp = app.get('/stats').body
    assert Solvers.ANTIGATE in resp
    assert b1 in resp
    assert b2 in resp
