# -*- coding: utf-8 -*-

from .one import one
from .two import two
from .three import three


class Level(object):
    PRIMARY = 1
    SECONDARY = 2
    ADDITIONAL = 3

    _order = [
        PRIMARY,
        SECONDARY,
        ADDITIONAL,
    ]

    @classmethod
    def lower(cls, lvl):
        """
        Возвращает "уровень", который находится
        на ступеньку ниже переданного "уровня".
        """
        try:
            i = cls._order.index(lvl)
        except IndexError:
            print 'WTF'
            return None
        try:
            return cls._order[i + 1]
        except IndexError:
            return None


def to_list(func):
    def wrapped_func(*args, **kw):
        return list(func(*args, **kw))
    return wrapped_func


class SolversRegistry(object):
    """
    Доступ к решателям
    """
    _solvers_params = [
        {
            'lvl': Level.PRIMARY,
            'cb': one,
            'name': 'one',
        },
        {
            'lvl': Level.SECONDARY,
            'cb': two,
            'name': 'two',
        },
        {
            'lvl': Level.ADDITIONAL,
            'cb': three,
            'name': 'three',
        },
    ]

    def __init__(self):
        self.rollback()

    def rollback(self):
        self._current_lvl = Level.PRIMARY
        self._current_solver = None
        self._used_solvers = []

    @to_list
    def solvers_names(self):
        for solver in self._solvers_params:
            yield solver['name']

    def get(self):
        if not self._current_solver:
            solver = self._get_one('lvl', self._current_lvl)
            if not solver:
                return None
            self._set_current(solver)
        return self._current_solver

    def get_by_name(self, name):
        return self._get_one('name', name)

    def _set_current(self, solver):
        self._used_solvers.append(solver['name'])
        self._current_solver = solver
        return self._current_solver

    def _get_one(self, param, val):
        solvers = self._get_all(param, val)
        return solvers[0] if solvers else None

    @to_list
    def _get_all(self, param, val):
        for solver in self._solvers_params:
            if solver[param] == val:
                yield solver

    def _get_unused_by_lvl(self, lvl):
        """
        Возвращает еще неиспользованный "расшифровщик" уровня "lvl"
        или None, если такой не найдется.
        """
        for solver in self._get_all('lvl', lvl):
            if solver['name'] not in self._used_solvers:
                return solver
        return None

    def get_next(self, descend=True):
        """
        По каким-то причинам пользователя не устраивает _current_solver,
        мы возвращаем следующий по "желанности".
        """
        solver = self._get_unused_by_lvl(self._current_lvl)
        if solver is not None:
            return self._set_current(solver)
        elif descend:
            lower_lvl = Level.lower(self._current_lvl)
            if lower_lvl:
                self._current_lvl = lower_lvl
                return self.get_next(descend)
        return None

