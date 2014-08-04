# -*- coding: utf-8 -*-
import time
from datetime import datetime
from collections import defaultdict

from .base import BaseStorage


class StubStorage(BaseStorage):
    def __init__(self):
        self._uses = defaultdict(int)
        self._fails = defaultdict(int)
        self._balances = {}
        self._current_solver = None
        self._timer_ends = {}
        self._banned = set()
        self._last_charge_dates = {}

    #### unused

    def set_current_solver(self, solver_name):
        self._current_solver = solver_name

    def get_current_solver(self):
        return self._current_solver

    def get_balance(self, solver_name):
        return self._balances.get(solver_name)

    def set_balance(self, solver_name, value):
        self._balances[solver_name] = value

    #### counters

    def incr_uses(self, solver_name):
        self._uses[solver_name] += 1

    def get_uses(self, solver_name):
        return self._uses[solver_name]

    def incr_fails(self, solver_name):
        self._fails[solver_name] += 1

    def get_fails(self, solver_name):
        return self._fails[solver_name]

    def reset_counters(self):
        self._fails.clear()
        self._uses.clear()

    #### blocks

    def is_blocked(self, solver_name):
        return not self.timer_expired("bans:%s" % solver_name)

    def block(self, solver_name, seconds):
        self.start_timer("bans:%s" % solver_name, seconds)
        self._uses[solver_name] = 0
        self._fails[solver_name] = 0

    #### timers

    def start_timer(self, name, seconds):
        self._timer_ends[name] = time.time() + seconds

    def timer_expired(self, name):
        return self._timer_ends.get(name, 0) < time.time()

    #### charge

    def update_last_charge_date(self, solver_name):
        self._last_charge_dates[solver_name] = datetime.now()

    def get_last_charge_date(self, solver_name):
        return self._last_charge_dates[solver_name]
