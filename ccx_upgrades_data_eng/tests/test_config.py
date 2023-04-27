"""Test for config module."""

from ccx_upgrades_data_eng.config import get_settings

import os
import pytest


def test_get_settings_fail():
    """Test get_settings with improper environment configured."""
    get_settings.cache_clear()
    with pytest.raises(Exception):
        get_settings()


def test_get_settings_from_env():
    """Test get_settings with the configuration exported as env variables."""
    get_settings.cache_clear()

    old_envs = os.environ.copy()

    os.environ = {
        "CLIENT_ID": "test-client_id",
        "CLIENT_SECRET": "test-client_secret",
        "SSO_ISSUER": "test-sso_issuer",
        "ALLOW_INSECURE": "1",
        "RHOBS_URL": "test-rhobs_url",
        "RHOBS_TENANT": "test-rhobs_tenant",
        "RHOBS_REQUEST_TIMEOUT": "1",
        "RHOBS_QUERY_MAX_MINUTES_FOR_DATA": "2",
        "INFERENCE_URL": "test-inference_url",
    }

    settings = get_settings()

    # clear the envs so that we don't interfere with other tests
    os.environ = old_envs

    assert settings.client_id == "test-client_id"
    assert settings.client_secret == "test-client_secret"
    assert settings.sso_issuer == "test-sso_issuer"
    assert settings.allow_insecure
    assert settings.rhobs_url == "test-rhobs_url"
    assert settings.rhobs_tenant == "test-rhobs_tenant"
    assert settings.rhobs_request_timeout == 1
    assert settings.rhobs_query_max_minutes_for_data == 2
    assert settings.inference_url == "test-inference_url"
