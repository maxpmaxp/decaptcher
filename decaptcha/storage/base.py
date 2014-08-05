# -*- coding: utf-8 -*-

import abc


class BaseStorage(object):
    __metaclass__ = abc.ABCMeta

    #### unused

    @abc.abstractmethod
    def get_current_solver(self):
        pass

    @abc.abstractmethod
    def set_current_solver(self, solver_name):
        pass

    @abc.abstractmethod
    def get_balance(self, solver_name):
        pass

    @abc.abstractmethod
    def set_balance(self, solver_name, value):
        pass

    #### counters

    @abc.abstractmethod
    def get_uses(self, solver_name):
        pass

    @abc.abstractmethod
    def incr_uses(self, solver_name):
        pass

    @abc.abstractmethod
    def get_fails(self, solver_name):
        pass

    @abc.abstractmethod
    def incr_fails(self, solver_name):
        pass

    @abc.abstractmethod
    def reset_counters(self):
        pass

    #### block

    @abc.abstractmethod
    def block(self, solver_name, seconds):
        pass

    @abc.abstractmethod
    def is_blocked(self, solver_name):
        pass

    #### timer

    @abc.abstractmethod
    def start_timer(self, name, seconds):
        pass

    @abc.abstractmethod
    def timer_expired(self, name):
        pass

    def start_expired_timer(self, name, seconds):
        if self.timer_expired(name):
            self.start_timer(name, seconds)

    #### charge

    @abc.abstractmethod
    def update_last_charge_date(self, solver_name):
        pass

    @abc.abstractmethod
    def get_last_charge_date(self, solver_name):
        pass
