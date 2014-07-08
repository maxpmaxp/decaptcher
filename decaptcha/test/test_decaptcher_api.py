# -*- coding: utf-8 -*-
from StringIO import StringIO

import pytest
from mock import patch

from solvers.de_captcher import DecaptcherAPI, ResultCodes
from errors import DecaptcherError


class FakeResponse(object):
    # формат ответа: "ResultCode|MajorID|MinorID|Type|Timeout|Text"
    _content_template = "%s|1|2|3|4|captchacode"

    def __init__(self, status_code=200, error_code=ResultCodes.OK, content=None):
        self.status_code = status_code
        if content:
            self.content = content
        else:
            self.content = self._content_template % error_code


@pytest.fixture
def solver_api():
    return DecaptcherAPI()


@pytest.fixture(params=[{'error_code': ResultCodes.GENERAL},
                        # здесь и ниже неверный формат ответа
                        {'content': 'bac 1'},
                        {'content': '0|2|3|4|captchacode'},
                        {'content': 'abc|1|2|3|4|captchacode'}])
def error_response(request):
    return FakeResponse(**request.param)


def test_parse_bad_solver_response(solver_api, error_response):
    pytest.raises(DecaptcherError,
                  "solver_api._parse_solver_response(error_response)")


def test_parse_good_solver_response(solver_api):
    resp = FakeResponse(content='0|1|2|3|4|captchacode')
    assert solver_api._parse_solver_response(resp) == 'captchacode'


@patch("requests.post")
def test_post(requests_post, solver_api):
    some_data = {}
    requests_post.return_value = FakeResponse(status_code=500)
    pytest.raises(DecaptcherError, "solver_api._post(some_data)")
    assert requests_post.called


@patch.object(DecaptcherAPI, '_parse_solver_response')
@patch.object(DecaptcherAPI, '_post')
def test_using_pict_type(_post, _parse_solver_response, solver_api):
    pict = StringIO("captcha img data")
    pict.name = 'captcha.png'
    default_pict_type = "0"
    another_pict_type = "another"

    data = {"function": "picture2",
            "pict_to": "0",
            "submit": "Send",
            "pict_type": default_pict_type}
    files = {"pict": pict}
    # если pict_type не передается или он равен None,
    # то используется "0" - значение по умолчанию
    solver_api.solve(pict, pict_type=None)
    _post.assert_called_with(data, files=files)

    solver_api.solve(pict)
    _post.assert_called_with(data, files=files)

    # если же pict_type != None, то используется переданное значение
    data["pict_type"] = another_pict_type
    solver_api.solve(pict, pict_type=another_pict_type)
    _post.assert_called_with(data, files=files)
