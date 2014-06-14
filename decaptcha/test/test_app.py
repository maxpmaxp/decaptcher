# -*- coding: utf-8 -*-

import pytest
from bottle import FormsDict, HTTPError
from mock import patch, MagicMock
from webtest import TestApp

import settings
from solvers.de_captcher import ResultCodes
from errors import SolverError
from app import (
    decaptcher_response, check_user, check_request,
    check_solver_name, app as wsgi_app)


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
    def __init__(self, post, query=None):
        self.POST = FormsDict(**post)
        self.query = FormsDict(query) if query else FormsDict()


def test_check_solver_name():
    assert check_solver_name(settings.Solvers.ANTIGATE) is None
    pytest.raises(HTTPError, check_solver_name, "not_existing")


@patch("app.check_user")
@patch("app.check_solver_name")
def test_check_request(check_solver_name, check_user):
    username = settings.APP_ACCESS['username']
    password = settings.APP_ACCESS['password']
    pict = '\xc9\x87\x8cWD6$X\x1er\xaeB`\x82'

    good_post_data = {
        'username': username,
        'password': password,
        'pict': pict,
    }
    bad_post_data = [
        # empty
        {},
        # no password
        {
            'username': username,
            'pict': pict
        },
        # no username
        {
            'password': password,
            'pict': pict
        },
        # no pict
        {
            'username': username,
            'password': password
        },
    ]

    # если проверка проходит, то возвращается None,
    # иначе - строку с описанием ошибки
    # (булево значение непустой строки True)

    for data in bad_post_data:
        bad_request = FakeRequest(post=data)
        assert check_request(bad_request)

    good_request = FakeRequest(post=good_post_data)
    assert check_request(good_request) is None
    assert not check_solver_name.called
    check_user.assert_called_with(username, password)

    solver = 'solver_name'
    request = FakeRequest(good_post_data, {'upstream_service': solver})
    check_request(request)
    check_solver_name.assert_called_with(solver)


def _patch(path, *args, **kw):
    return patch(path, *args, **kw).start()


@patch.dict("settings.BLOCK_PERIODS", {"errcode": 7})
def test_solve_captcha():
    def reset_mocks(locals_):
        for obj_name, obj in locals_.items():
            if not obj_name.startswith('_') and isinstance(obj, MagicMock):
                obj.reset_mock()

    check_request = _patch("app.check_request")
    decaptcher_response = _patch("app.decaptcher_response")
    start_expired_timers = _patch("app.start_expired_timers")
    solvers = _patch("app.solvers")
    check_solver = _patch("app.check_solver")
    storage = _patch("app.RedisStorage")()

    solve = MagicMock()
    solvers.get_highest_notblocked.return_value.__getitem__.return_value\
            = solvers.get_by_name.return_value.__getitem__.return_value\
            = solvers.get_next.return_value.__getitem__.return_value\
            = solve

    app = TestApp(wsgi_app)
    some_data = {'pict': 'pict_data'}

    # моделирование запроса с невалидными POST-данными
    check_request.return_value = "error description"
    decaptcher_response.return_value = "error"
    app.post('/', some_data)
    #
    assert check_request.called
    assert decaptcher_response.called
    assert not solve.called
    assert not start_expired_timers.called
    reset_mocks(locals())

    # моделирование запроса с валидными POST-данными
    # без явного указания сервиса-расшифровщика
    check_request.return_value = None
    check_solver.side_effect = ["errcode", None]
    solve.side_effect = [SolverError, "captchacode1"]
    decaptcher_response.return_value = "resp1"
    app.post('/', some_data)
    #
    assert start_expired_timers.called
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

    # моделирование запроса с валидными POST-данными
    # с явным указанием сервиса-расшифровщика
    check_request.return_value = None
    decaptcher_response.return_value = "resp2"
    solve.side_effect = ["captchacode2"]
    app.post('/?upstream_service=captchabot', some_data)
    #
    assert start_expired_timers.called
    assert solvers.get_by_name.called
    assert not solvers.get_highest_notblocked.called
    assert not check_solver.called
    assert storage.incr_uses.call_count == 1
    assert solve.call_count == 1
    assert not storage.incr_fails.called
    assert not solvers.get_next.called
    assert decaptcher_response.called
    reset_mocks(locals())


def test_ban_unban():
    storage = _patch("app.RedisStorage")()
    app = TestApp(wsgi_app)

    s = 'antigate'
    app.get('/ban/%s' % s)
    storage.ban.assert_called_once_with(s)

    app.get('/unban/%s' % s)
    storage.unban.assert_called_once_with(s)
