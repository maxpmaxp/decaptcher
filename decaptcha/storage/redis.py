# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime

import redis

import settings
from .base import BaseStorage


DATE_FMT = "%Y-%m-%d %H:%M:%S"

class RedisStorage(BaseStorage):
    pool = redis.ConnectionPool(**settings.REDIS_CONF)

    def __init__(self):
        super(RedisStorage, self).__init__()
        self.r = redis.StrictRedis(connection_pool=self.pool)

    #### unused

    def set_current_solver(self, solver_name):
        self.r.set("current_solver", solver_name)

    def get_current_solver(self):
        return self.r.get("current_solver")

    def get_balance(self, solver_name):
        balance = self.r.hget("balances", solver_name)
        return balance if (balance is None) else int(balance)

    def set_balance(self, solver_name, value):
        self.r.hset("balances", solver_name, value)

    #### counters

    def _incr_counter(self, solver_name, counter_name):
        """
        Увеличиваем на 1 счетчик 'counter_name' для сервиса 'solver_name',
        но только при условии, что сервис не заблокирован.
        """
        with self.r.pipeline() as pipe:
            pipe.watch("blocks:" + solver_name)
            if not self.is_blocked(solver_name):
                pipe.multi()
                pipe.hincrby(counter_name, solver_name, 1)
                pipe.execute()

    def incr_uses(self, solver_name):
        self._incr_counter(solver_name, "counters:uses")

    def get_uses(self, solver_name):
        counter = self.r.hget("counters:uses", solver_name)
        return int(counter or 0)

    def incr_fails(self, solver_name):
        self._incr_counter(solver_name, "counters:fails")

    def get_fails(self, solver_name):
        counter = self.r.hget("counters:fails", solver_name)
        return int(counter or 0)

    #### blocks

    def block(self, solver_name, seconds):
        """
        Блокировка сервиса 'solver_name' на указанное число секунд
        и обнуление счетчиков для него.
        """
        self.start_timer("blocks:%s" % solver_name, seconds)
        self.r.hset("counters:uses", solver_name, 0)
        self.r.hset("counters:fails", solver_name, 0)

    def is_blocked(self, solver_name):
        return not self.timer_expired("blocks:%s" % solver_name)

    #### timers

    def timer_expired(self, name):
        return self.r.get("timers:%s" % name) is None

    def start_timer(self, name, seconds):
        now = datetime.now().strftime(DATE_FMT)
        self.r.setex("timers:%s" % name, seconds, now)

    #### charge

    def update_last_charge_date(self, solver_name):
        now = datetime.now().strftime(DATE_FMT)
        self.r.hset("last_charge:date", solver_name, now)

    def get_last_charge_date(self, solver_name):
        return self.r.hget("last_charge:date", solver_name)
