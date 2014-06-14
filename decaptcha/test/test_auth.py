# -*- coding: utf-8 -*-

import pytest
import webtest

from app import app as our_app, requires_auth


@our_app.route('/ping')
@requires_auth
def ping():
    return 'pong'


def test_requires_auth(app):
    auth = app.authorization
    app.authorization = None
    pytest.raises(webtest.app.AppError, app.get, '/ping')

    app.authorization = auth
    resp = app.get('/ping')
    assert 'pong' in resp.body