import sys
from os.path import dirname
sys.path.insert(0, dirname(dirname(__file__)))

import pytest
import webtest

import settings
from storage.stub import StubStorage
from app import app as our_app


@pytest.fixture
def stub_storage():
    return StubStorage()


@pytest.fixture
def auth_app():
    user = settings.APP_ACCESS
    test_app = webtest.TestApp(our_app)
    test_app.authorization = ('Basic', (user['username'], user['password']))
    return test_app


@pytest.fixture
def app():
    return webtest.TestApp(our_app)
