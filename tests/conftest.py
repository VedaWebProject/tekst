from functools import lru_cache

import pytest
import requests
from fastapi.testclient import TestClient
from textrig.config import TextRigConfig, get_config
from textrig.main import app as app_instance
from textrig.models.text import Text


"""
pytest fixtures go in here...
"""


@lru_cache()
def get_config_override():
    """config overrides for tests"""
    return TextRigConfig(app_name="TextRig Test Instance", dev_mode=True)


@pytest.fixture
def testing_config():
    return get_config_override


@pytest.fixture
def app(testing_config):
    """
    Provides an app instance with overridden
    config according to get_config_override()
    """
    app_instance.dependency_overrides[get_config] = testing_config
    return app_instance


@lru_cache()
@pytest.fixture
def client(app):
    """
    Provides a TestClient instance configured with an app instance
    with overridden config according to get_config_override()
    """
    return TestClient(app)


@pytest.fixture
def dummy_data_text():
    return Text(
        title="Rigveda",
        subtitle="An ancient Indian collection of Vedic Sanskrit hymns",
        levels=["Book", "Hymn", "Stanza"],
    )


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
