"""Test for config module."""

import os
import pytest

from ccx_upgrades_data_eng.config import (
    get_settings,
    RH_OAUTH_ISSUER,
    RHOBS_URL,
    RHOBS_DEFAULT_TENANT,
)


def test_get_settings_fail():
    """Test get_settings with improper environment configured."""
    get_settings.cache_clear()
    with pytest.raises(Exception):
        get_settings()


def test_default_settings_not_set():
    """Test that the settings with default value do not need to be set."""
    get_settings.cache_clear()

    old_envs = os.environ.copy()

    os.environ = {
        "CLIENT_ID": "test-client_id",
        "CLIENT_SECRET": "test-client_secret",
        "INFERENCE_URL": "test-inference_url",
    }

    settings = get_settings()

    # clear the envs so that we don't interfere with other tests
    os.environ = old_envs

    assert settings.client_id == "test-client_id"
    assert settings.client_secret == "test-client_secret"
    assert settings.sso_issuer == RH_OAUTH_ISSUER
    assert settings.allow_insecure is False
    assert settings.rhobs_url == RHOBS_URL
    assert settings.rhobs_tenant == RHOBS_DEFAULT_TENANT
    assert settings.rhobs_request_timeout is None
    assert settings.rhobs_query_max_minutes_for_data == 60
    assert settings.inference_url == "test-inference_url"
    assert settings.cache_enabled is False
    assert settings.cache_ttl == 0
    assert settings.cache_size == 128
    assert settings.sso_retry_max_attempts == 5
    assert settings.sso_retry_base_delay == 1
    assert settings.sso_retry_max_delay == 30


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
        "CACHE_ENABLED": "true",
        "CACHE_TTL": "30",
        "CACHE_SIZE": "10",
    }

    os.environ.update(
        {
            "SSO_RETRY_MAX_ATTEMPTS": "3",
            "SSO_RETRY_BASE_DELAY": "2",
            "SSO_RETRY_MAX_DELAY": "60",
        }
    )

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
    assert settings.cache_enabled
    assert settings.cache_ttl == 30
    assert settings.cache_size == 10
    assert settings.sso_retry_max_attempts == 3
    assert settings.sso_retry_base_delay == 2
    assert settings.sso_retry_max_delay == 60
