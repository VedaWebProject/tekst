from functools import lru_cache

import pytest
from fastapi.testclient import TestClient
from textrig.config import TextRigConfig, get_config
from textrig.main import app as app_instance
from textrig.models.text import Level, Text, Unit


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
        structure=[
            Level(label="Book"),
            Level(label="Hymn"),
            Level(label="Stanza"),
        ],
    )


@pytest.fixture
def dummy_data_units():
    return [
        Unit(location="1.1.1"),
        Unit(location="1.1.2"),
        Unit(location="1.2.1"),
        Unit(location="1.2.2"),
        Unit(location="1.2.3"),
        Unit(location="2.2.4"),
        Unit(location="2.2.1"),
        Unit(location="2.2.2"),
        Unit(location="2.3.1"),
    ]
