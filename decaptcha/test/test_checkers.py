# -*- coding: utf-8 -*-
import time

from mock import patch, DEFAULT

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


def _incrby_uses(service, value, storage):
    for _ in range(value): storage.incr_uses(service)

def _incrby_fails(service, value, storage):
    for _ in range(value): storage.incr_fails(service)


settings.MAX_FAILS_PERCENTAGE = max_fails = 2

settings.MINBID_CHECK_INTERVAL = 1
settings.FAILS_CHECK_INTERVAL = 2


@patch.multiple(antigate_api, minbid=DEFAULT)
def test_checking_minbid(minbid, stub_storage):
    max_price = settings.ANTIGATE_MAX_PRICE / 1000.
    minbid.return_value = max_price + eps
    assert not is_antigate_minbid_ok()

    minbid.return_value = max_price
    assert is_antigate_minbid_ok()

    minbid.return_value = max_price - eps
    assert is_antigate_minbid_ok()



def test_checking_fails_percentage(stub_storage):
    service = "one"
    assert is_fails_percentage_ok(service, stub_storage)

    _incrby_uses(service, 100, stub_storage)
    assert is_fails_percentage_ok(service, stub_storage)

    # ок: % фейлов на грани допустимого
    _incrby_fails(service, max_fails, stub_storage)
    assert is_fails_percentage_ok(service, stub_storage)

    # не ок: % фейлов стал недопустимым
    _incrby_fails(service, 1, stub_storage)
    assert not is_fails_percentage_ok(service, stub_storage)


def test_checking_fails_percentage_with_timer(stub_storage):
    timer_duration = 1
    service = "one"
    storage = stub_storage
    storage.start_timer('fails', timer_duration)

    # ок: сервис еще не использовался
    assert check_solver(service, storage) is None

    # ок: хотя фейлов много, но таймер еще не закончился
    _incrby_uses(service, 1, storage)
    _incrby_fails(service, 2, storage)
    assert not storage.timer_expired('fails')
    assert check_solver(service, storage) is None

    # не ок: произошла проверка % фейлов;
    time.sleep(timer_duration + eps)
    assert storage.timer_expired('fails')
    assert check_solver(service, storage) == CheckErrors.FAILS

    # ок: % фейлов понизился
    _incrby_uses(service, 99, storage)
    assert check_solver(service, storage) is None


@patch.multiple(antigate_api, minbid=DEFAULT)
def test_checking_minbid_and_fails_percentage_with_timer(minbid, stub_storage):
    storage = stub_storage
    service = settings.Solvers.ANTIGATE

    min_bid = settings.ANTIGATE_MAX_PRICE / 1000.
    cheap_bid = min_bid - eps
    expensive_bid = min_bid + eps

    time_fails = 1

    minbid.return_value = expensive_bid
    storage.start_timer('minbid', time_fails)
    storage.start_timer('fails', time_fails + 1)

    # не ок: при первом использовании сервиса 'antigate'
    # проверяется ставка, а она велика
    assert check_solver(service, storage) == CheckErrors.MINBID

    # ок: фейлов много, ставка велика,
    # но оба таймера еще не закончились
    _incrby_uses(service, 1, storage)
    _incrby_fails(service, 2, storage)
    assert not storage.timer_expired('minbid')
    assert not storage.timer_expired('fails')
    assert check_solver(service, storage) is None

    # не ок: таймер minbid закончился,
    # произошла проверка значения мин. ставки
    time.sleep(time_fails + eps)
    assert storage.timer_expired('minbid')
    assert not storage.timer_expired('fails')
    assert check_solver(service, storage) == CheckErrors.MINBID

    # не ок: оба таймера закончились,
    # % фейлов и ставка по-прежнему нас не удовлетворяют
    time.sleep(1)
    assert storage.timer_expired('minbid')
    assert storage.timer_expired('fails')
    assert check_solver(service, storage) == CheckErrors.MINBID

    # не ок: хотя minbid понизился, но % фейлов по-прежнему велик
    minbid.return_value = cheap_bid
    assert check_solver(service, storage) == CheckErrors.FAILS

    # не ок: % фейлов понизился, но minbid повысился
    minbid.return_value = expensive_bid
    _incrby_uses(service, 99, storage)
    assert check_solver(service, storage) == CheckErrors.MINBID

    # ок: обе величины стали допустимыми
    minbid.return_value = cheap_bid
    assert check_solver(service, storage) is None

    # ок: % фейлов повысился, но т.к. мы запустили таймер 'fails',
    # то проверяется только ставка minbid, которая осталась низкой.
    _incrby_fails(service, 2, storage)
    storage.start_timer('fails', 1)
    assert check_solver(service, storage) is None
