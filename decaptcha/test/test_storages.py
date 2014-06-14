# -*- coding: utf-8 -*-
import time

import pytest

import settings
from storage.redis import RedisStorage
from storage.stub import StubStorage

settings.REDIS_CONF['db'] = 10


@pytest.fixture(params=[RedisStorage, StubStorage])
def storage(request):
    storage = request.param()

    def flushdb():
        if isinstance(storage, RedisStorage):
            storage.r.flushdb()
    request.addfinalizer(flushdb)
    flushdb()

    return storage


def test_manipulations_with_current_solver(storage):
    assert storage.get_current_solver() == None
    storage.set_current_solver('one')
    assert storage.get_current_solver() == 'one'
    storage.set_current_solver('two')
    assert storage.get_current_solver() == 'two'


def test_manipulations_with_solver_uses(storage):
    assert storage.get_uses('one') == 0
    storage.incr_uses('one')
    assert storage.get_uses('one') == 1
    storage.incr_uses('one')
    assert storage.get_uses('one') == 2


def test_manipulations_with_solver_fails(storage):
    assert storage.get_fails('one') == 0
    storage.incr_fails('one')
    assert storage.get_fails('one') == 1
    storage.incr_fails('one')
    assert storage.get_fails('one') == 2


def test_manipulations_with_balance(storage):
    assert storage.get_balance('one') == None
    storage.set_balance('one', 1000)
    assert storage.get_balance('one') == 1000
    storage.set_balance('one', 500)
    assert storage.get_balance('one') == 500


def test_solvers_blocking(storage):
    block_duration = 1
    assert not storage.is_blocked("one")

    storage.incr_uses("one")
    storage.incr_fails("one")
    storage.block('one', block_duration)
    assert storage.is_blocked("one")
    assert storage.get_uses("one") == 0
    assert storage.get_fails("one") == 0

    time.sleep(block_duration + 0.1)
    assert not storage.is_blocked('one')


def test_bans(storage):
    s = "some solver"
    assert not storage.is_banned(s)

    storage.ban(s)
    assert storage.is_banned(s)
    assert not storage.is_blocked(s)

    storage.unban(s)
    assert not storage.is_banned(s)


def test_timers(storage):
    duration = 1
    assert storage.timer_expired('first')

    storage.start_timer('first', duration)
    assert not storage.timer_expired('first')

    time.sleep(duration + 0.1)
    assert storage.timer_expired('first')
