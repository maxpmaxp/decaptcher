import sys
from os.path import dirname
sys.path.insert(0, dirname(dirname(__file__)))

import pytest
from storage.stub import StubStorage


@pytest.fixture
def stub_storage():
    return StubStorage()
