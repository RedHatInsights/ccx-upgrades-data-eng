"""Tests for auth.py."""

import os
from unittest.mock import MagicMock, patch

from ccx_upgrades_data_eng.auth import get_session_manager
from ccx_upgrades_data_eng.config import get_settings
from ccx_upgrades_data_eng.tests import needed_env


@patch.dict(os.environ, needed_env)
def test_get_session_manager_cache():
    """Check that get_session_manager always return the same instance."""
    first_instance = get_session_manager()
    second_instance = get_session_manager()

    assert first_instance is second_instance


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.auth.OAuth2Session")
def test_refresh_token_new(session_init_mock):
    """Check that refresh_token won't update the token until needed."""
    get_session_manager.cache_clear()  # skip cache from other tests
    session_mock = MagicMock()

    session_init_mock.return_value = session_mock

    session_manager = get_session_manager()
    session_manager.refresh_token()

    assert session_mock.fetch_token.called


@patch.dict(os.environ, needed_env)
def test_allow_insecure_empty_allow_insecure():
    """Check that if ALLOW_INSECURE env var is empty, the verify is True."""
    get_settings.cache_clear()
    get_session_manager.cache_clear()  # skip cache from other tests

    session_manager = get_session_manager()
    assert session_manager.verify


@patch.dict(
    os.environ,
    {
        "CLIENT_ID": "client-id",
        "CLIENT_SECRET": "secret",
        "INFERENCE_URL": "http://inference:8000",
        "ALLOW_INSECURE": "True",
    },
)
def test_allow_insecure_with_allow_insecure():
    """Check that if ALLOW_INSECURE env var is True, the verify is False."""
    get_settings.cache_clear()
    get_session_manager.cache_clear()  # skip cache from other tests

    session_manager = get_session_manager()
    assert not session_manager.verify


@patch.dict(
    os.environ,
    {
        "CLIENT_ID": "client-id",
        "CLIENT_SECRET": "secret",
        "INFERENCE_URL": "http://inference:8000",
        "ALLOW_INSECURE": "0",
    },
)
def test_allow_insecure_0_allow_insecure():
    """Check that if ALLOW_INSECURE env var is 0, the verify is True."""
    get_settings.cache_clear()
    get_session_manager.cache_clear()  # skip cache from other tests

    session_manager = get_session_manager()
    assert session_manager.verify
