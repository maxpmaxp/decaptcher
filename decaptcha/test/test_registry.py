# -*- coding: utf-8 -*-

import pytest

from solvers.registry import Level, SolversRegistry


def test_level_lower():
    levels = Level._order
    assert Level.lower(levels[0]) == levels[1]
    assert Level.lower(levels[1]) == levels[2]
    assert Level.lower(levels[-1]) == None

one = {
    'lvl': Level.PRIMARY,
    'cb': lambda x: 1,
    'name': 'one',
}
two = {
    'lvl': Level.SECONDARY,
    'cb': lambda x: 2,
    'name': 'two',
}
three = {
    'lvl': Level.ADDITIONAL,
    'cb': lambda x: 3,
    'name': 'three',
}
four = {
    'lvl': Level.ADDITIONAL,
    'cb': lambda x: 4,
    'name': 'four',
}

@pytest.fixture()
def fake_registry(request):

    registry = SolversRegistry()
    registry._solvers_params = [
        one,
        two,
        three,
        four,
    ]

    def fin():
        registry.rollback()
    request.addfinalizer(fin)

    return registry


class TestSolverRegistry(object):

    def test_get(self, fake_registry):
        assert fake_registry.get() == one
        assert fake_registry.get() == one
        assert fake_registry.get_next(descend=True) == two
        assert fake_registry.get() == two


    def test_get_by_name(self, fake_registry):
        get_by_name = fake_registry.get_by_name

        assert get_by_name('one') == one
        assert get_by_name('four') == four
        assert get_by_name('not_existing') == None


    def test_get_next(self, fake_registry):
        assert fake_registry.get_next() == one
        assert fake_registry.get_next(descend=False) == None
        assert fake_registry.get_next(descend=True) == two


    def test_solvers_names(self, fake_registry):
        assert fake_registry.solvers_names() == "one two three four".split()


    # testing 'private' funcs

    def test_get_unused_by_lvl(self, fake_registry):
        def get_solver():
            return fake_registry._get_unused_by_lvl(Level.ADDITIONAL)

        assert get_solver() in [three, four]

        fake_registry._used_solvers = {'three'}
        assert get_solver() == four

        fake_registry._used_solvers = {'three', 'four'}
        assert get_solver() == None


    def test_get_all(self, fake_registry):
        get_all = fake_registry._get_all

        get_all('lvl', Level.PRIMARY) == [one]
        get_all('lvl', Level.ADDITIONAL) == [three, four]
        fake_registry._used_solvers = {'one', 'two'}
        get_all('name', 'one') == one
