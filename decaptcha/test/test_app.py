# -*- coding: utf-8 -*-

import pytest
from bottle import FormsDict, HTTPError
from mock import patch, MagicMock
from webtest.forms import Upload

import settings
from solvers.de_captcher import ResultCodes
from errors import SolverError
from controllers.solve import (
    decaptcher_response, check_user, check_request,
    check_solver_name)


def test_decaptcher_response():
    string = decaptcher_response(captcha_code="abc")
    parts = string.split("|")
    assert len(parts) == 6
    result, captcha = parts[0], parts[-1]
    assert result == ResultCodes.OK
    assert captcha == "abc"

    string = decaptcher_response(result_code=ResultCodes.GENERAL)
    parts = string.split("|")
    assert len(parts) == 6
    result = parts[0]
    assert result == ResultCodes.GENERAL


def test_check_user():
    correct_username = settings.APP_ACCESS['username']
    correct_password = settings.APP_ACCESS['password']
    assert not check_user(correct_username, correct_password + '111')
    assert not check_user(correct_username + '111', correct_password)
    assert check_user(correct_username, correct_password)


class FakeRequest(object):
    def __init__(self, post, query=None, files=None):
        self.POST = FormsDict(**post)
        self.query = FormsDict(query) if query else FormsDict()
        self.files = FormsDict(files) if files else FormsDict()


def test_check_solver_name():
    assert check_solver_name(settings.Solvers.ANTIGATE) is None
    pytest.raises(HTTPError, check_solver_name, "not_existing")


@patch("controllers.solve.check_user")
@patch("controllers.solve.check_solver_name")
def test_check_request(check_solver_name, check_user):
    username = 'some user'
    password = 'some passwd'
    files = {'pict': Upload('captcha.png', '\xc9')}
    bad_args = [
        {'post': {}}, # empty
        {'post': {'username': username}, 'files': files}, # no password
        {'post': {'password': password}, 'files': files}, # no username
        {'post': {'username': username, 'password': password}}, # no pict
    ]
    good_args = {
        'post': {'username': username, 'password': password},
        'files': files
    }

    # если проверка проходит, то возвращается None,
    # иначе - строка с описанием ошибки
    # (булево значение непустой строки = True)
    for args in bad_args:
        bad_request = FakeRequest(**args)
        assert check_request(bad_request)

    good_request = FakeRequest(**good_args)
    assert check_request(good_request) is None
    assert not check_solver_name.called

    solver = 'solver_name'
    request = FakeRequest(query={'upstream_service': solver}, **good_args)
    check_request(request)
    check_solver_name.assert_called_with(solver)


def _patch(path, *args, **kw):
    return patch(path, *args, **kw).start()


def reset_mocks(locals_):
    for obj_name, obj in locals_.items():
        if not obj_name.startswith('_') and isinstance(obj, MagicMock):
            obj.reset_mock()


@patch.dict("settings.BLOCK_PERIODS", {"errcode": 7})
def test_solve_captcha(app):

    m = 'controllers.solve'
    check_request = _patch("%s.check_request" % m)
    decaptcher_response = _patch("%s.decaptcher_response" % m)
    solvers = _patch("%s.solvers" % m)
    check_solver = _patch("%s.check_solver" % m)
    storage = _patch("%s.RedisStorage" % m)()

    solve = MagicMock()
    solvers.get_highest_notblocked.return_value.__getitem__.return_value\
            = solvers.get_by_name.return_value.__getitem__.return_value\
            = solvers.get_next.return_value.__getitem__.return_value\
            = solve

    pict = Upload('captcha.png', 'picture_binary_data')
    some_data = {'pict': pict}

    # моделирование запроса с невалидными POST-данными
    check_request.return_value = "error description"
    decaptcher_response.return_value = "error"
    app.post('/', some_data)
    #
    assert check_request.called
    assert decaptcher_response.called
    assert not solve.called
    reset_mocks(locals())

    # моделирование запроса с валидными POST-данными
    # без явного указания сервиса-расшифровщика
    check_request.return_value = None
    check_solver.side_effect = ["errcode", None]
    solve.side_effect = [SolverError, "captchacode1"]
    decaptcher_response.return_value = "resp1"
    app.post('/', some_data)
    #
    assert solvers.get_highest_notblocked.call_count == 2
    assert not solvers.get_by_name.called
    assert check_solver.call_count == 2
    assert storage.block.call_count == 1
    assert storage.incr_uses.call_count == 2
    assert solve.call_count == 2
    assert storage.incr_fails.call_count == 1
    assert solvers.get_next.call_count == 1
    assert decaptcher_response.called
    reset_mocks(locals())
    check_solver.side_effect = None

    # моделирование запроса с валидными POST-данными
    # с явным указанием сервиса-расшифровщика
    check_request.return_value = None
    decaptcher_response.return_value = "resp2"
    solve.side_effect = ["captchacode2"]
    app.post('/?upstream_service=captchabot', some_data)
    #
    assert solvers.get_by_name.called
    assert not solvers.get_highest_notblocked.called
    assert not check_solver.called
    assert storage.incr_uses.call_count == 1
    assert solve.call_count == 1
    assert not storage.incr_fails.called
    assert not solvers.get_next.called
    assert decaptcher_response.called
    reset_mocks(locals())
    check_solver.side_effect = None

    # моделирование случая, при котором число попыток
    # расшифровать капчу превышает допустимое
    check_request.return_value = None
    check_solver.return_value = None
    solve.side_effect = SolverError
    decaptcher_response.return_value = "resp1"
    app.post('/', some_data)
    #
    assert storage.incr_uses.call_count\
            == storage.incr_fails.call_count\
            == solve.call_count\
            == solvers.get_next.call_count\
            == settings.MAX_ATTEMPTS_TO_SOLVE
    assert decaptcher_response.called
    reset_mocks(locals())

    # проверяем, что параметры "pict_type" и "pict" передаются в расшифровщик
    some_data = {'pict': pict, 'pict_type': 'some_type'}
    check_request.return_value = None
    check_solver.return_value = None
    solve.side_effect = None
    decaptcher_response.return_value = "resp1"
    app.post('/', some_data)
    #
    assert solve.call_args[1]['pict_type'] == some_data['pict_type']
    reset_mocks(locals())

    patch.stopall()
