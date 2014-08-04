# -*- coding: utf-8 -*-

from mock import patch, MagicMock, DEFAULT

import settings
from settings import CheckErrors
from checkers import (
    is_service_expensive, update_balance,
    is_antigate_minbid_ok, is_fails_percentage_ok, check_solver)
from solvers.api_list import SOLVER_APIS

eps = 0.0001
solver_name = settings.Solvers.ANTIGATE
settings.MAX_COSTS[solver_name] = max_delta = 1
antigate_api = SOLVER_APIS[solver_name]


def reset_mocks(locals_):
    for obj_name, obj in locals_.items():
        if not obj_name.startswith('_') and isinstance(obj, MagicMock):
            obj.reset_mock()


# TODO: удалить два теста ниже при удалении других balance-функций
@patch.multiple(antigate_api, balance=DEFAULT)
def test_update_balance(balance, stub_storage):
    balance.return_value = 100

    update_balance(solver_name, stub_storage)
    assert stub_storage.get_balance(solver_name) == 100


@patch.multiple(antigate_api, balance=DEFAULT)
def test_is_service_expensive(balance, stub_storage):
    start_balance = 100
    stub_storage.set_balance(solver_name, start_balance)

    # текущий баланс сервиса не отличается от стартового
    balance.return_value = start_balance
    assert not is_service_expensive(solver_name, stub_storage)

    # текущий баланс сервиса меньше стартового на допустимую величину
    balance.return_value = start_balance - max_delta / 2.
    assert not is_service_expensive(solver_name, stub_storage)

    # текущий баланс сервиса меньше стартового на НЕдопустимую величину
    balance.return_value = start_balance - max_delta * 2
    assert is_service_expensive(solver_name, stub_storage)


@patch.multiple(antigate_api, minbid=DEFAULT)
def test_checking_minbid(minbid, stub_storage):
    max_price = settings.ANTIGATE_MAX_PRICE / 1000.
    minbid.return_value = max_price + eps
    assert not is_antigate_minbid_ok()

    minbid.return_value = max_price
    assert is_antigate_minbid_ok()

    minbid.return_value = max_price - eps
    assert is_antigate_minbid_ok()


def test_checking_fails_percentage():
    s = MagicMock()
    service = "some service"
    threshold = settings.MAX_FAILS_PERCENTAGE

    s.get_uses.return_value = 0
    s.get_fails.return_value = 100
    assert is_fails_percentage_ok(service, s)

    s.get_uses.return_value = 1
    s.get_fails.return_value = 100
    assert not is_fails_percentage_ok(service, s)

    uses = 100
    # ок: % фейлов на грани допустимого
    s.get_uses.return_value = uses
    s.get_fails.return_value = uses / 100 * threshold
    assert is_fails_percentage_ok(service, s)

    # не ок: % фейлов стал недопустимым
    s.get_uses.return_value = uses
    s.get_fails.return_value = uses / 100 * (threshold + 1)
    assert not is_fails_percentage_ok(service, s)


@patch("checkers.is_fails_percentage_ok")
@patch("checkers.is_antigate_minbid_ok")
def test_checking_fails_percentage_with_timer(
        is_antigate_minbid_ok,
        is_fails_percentage_ok):
    s = MagicMock()
    # проверяем функцию 'check_solver' для сервиса != 'antigate'
    service = "not_antigate"
    locals_ = locals()

    # ок: таймер не завершен
    s.timer_expired.return_value = False
    assert is_fails_percentage_ok.call_count == 0
    assert check_solver(service, s) is None
    reset_mocks(locals_)

    # ок: таймер завершен, но мало фейлов
    s.timer_expired.return_value = True
    is_fails_percentage_ok.return_value = True
    assert check_solver(service, s) is None
    assert is_fails_percentage_ok.call_count == 1
    assert s.start_expired_timer.call_count == 1
    assert is_antigate_minbid_ok.call_count == 0
    reset_mocks(locals_)

    # ок: таймер завершен и много фейлов
    s.timer_expired.return_value = True
    is_fails_percentage_ok.return_value = False
    assert check_solver(service, s) == CheckErrors.FAILS
    assert is_fails_percentage_ok.call_count == 1
    assert s.start_expired_timer.call_count == 1
    assert is_antigate_minbid_ok.call_count == 0


@patch("checkers.is_fails_percentage_ok")
@patch("checkers.is_antigate_minbid_ok")
def test_checking_minbid_and_fails_percentage_with_timer(
        is_antigate_minbid_ok,
        is_fails_percentage_ok):
    s = MagicMock()
    service = settings.Solvers.ANTIGATE
    locals_ = locals()

    # ок: оба таймера не завершены
    s.timer_expired.return_value = False
    assert check_solver(service, s) is None
    assert is_fails_percentage_ok.call_count == 0
    assert is_antigate_minbid_ok.call_count == 0
    reset_mocks(locals_)

    # не ок: оба таймера завершены, minbid не ок
    s.timer_expired.return_value = True
    is_antigate_minbid_ok.return_value = False
    is_fails_percentage_ok.return_value = False
    assert check_solver(service, s) is CheckErrors.MINBID
    assert is_antigate_minbid_ok.call_count == 1
    assert is_fails_percentage_ok.call_count == 0
    reset_mocks(locals_)

    # не ок: оба таймера завершены, minbid ок, но много ошибок
    s.timer_expired.return_value = True
    is_antigate_minbid_ok.return_value = True
    is_fails_percentage_ok.return_value = False
    assert check_solver(service, s) is CheckErrors.FAILS
    assert is_antigate_minbid_ok.call_count == 1
    assert is_fails_percentage_ok.call_count == 1
    reset_mocks(locals_)

    # не ок: завершен только таймер 'fails', много ошибок
    s.timer_expired.side_effect = lambda x: x == 'fails'
    is_antigate_minbid_ok.return_value = False
    is_fails_percentage_ok.return_value = False
    assert check_solver(service, s) is CheckErrors.FAILS
    assert is_antigate_minbid_ok.call_count == 0
    assert is_fails_percentage_ok.call_count == 1
