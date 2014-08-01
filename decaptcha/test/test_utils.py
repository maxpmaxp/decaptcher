# -*- coding: utf-8 -*-

from utils import union_dicts


def test_union_dicts():
    d1 = {'1': 1, '2': 2}
    d2 = {'3': 3, '4': 4}
    d = union_dicts(d1, d2)
    assert d1 == {'1': 1, '2': 2}
    assert d2 == {'3': 3, '4': 4}
    assert d == {'1': 1, '2': 2, '3': 3, '4': 4}
