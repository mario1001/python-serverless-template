import pytest


@pytest.fixture
def mock_env_variable(monkeypatch):
    monkeypatch.setenv("LOGGER_LEVEL", "INFO")
