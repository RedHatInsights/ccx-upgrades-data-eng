"""Tests for SSO refresh logic functionality."""

import os
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from fastapi import Request

from ccx_upgrades_data_eng.main import (
    refresh_sso_token,
    get_session_and_refresh_token,
    get_retry_decorator
)
from ccx_upgrades_data_eng.auth import SessionManagerException, TokenException
from ccx_upgrades_data_eng.tests import needed_env

# Mock for the call_next function in middleware
async def mock_call_next(request):
    return "next called"

@pytest.mark.asyncio
@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
@patch("ccx_upgrades_data_eng.utils.asyncio.sleep", new_callable=AsyncMock)
@patch("ccx_upgrades_data_eng.utils.time.sleep", return_value=None)
async def test_refresh_sso_token_session_ok(time_sleep_mock, asyncio_sleep_mock, get_session_manager_mock):
    """Check that refresh_sso_token tries to get the session and refresh the token."""
    session_manager_mock = MagicMock()
    get_session_manager_mock.return_value = session_manager_mock

    resp = await refresh_sso_token(Request({"type": "http"}), mock_call_next)

    assert get_session_manager_mock.called
    assert session_manager_mock.refresh_token.called
    assert not time_sleep_mock.called
    assert not asyncio_sleep_mock.called
    assert resp == "next called"

@pytest.mark.asyncio
@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
@patch("ccx_upgrades_data_eng.utils.asyncio.sleep", new_callable=AsyncMock)
@patch("ccx_upgrades_data_eng.utils.time.sleep", return_value=None)
async def test_refresh_sso_token_session_manager_exception(time_sleep_mock, asyncio_sleep_mock, get_session_manager_mock):
    """Check that refresh_sso_token handles SessionManagerException."""
    get_session_manager_mock.side_effect = SessionManagerException("test")

    resp = await refresh_sso_token(Request({"type": "http"}), mock_call_next)

    assert get_session_manager_mock.called
    assert not time_sleep_mock.called
    assert asyncio_sleep_mock.called
    assert resp.status_code == 503
    assert resp.body == b'"Unable to initialize SSO session"'

@pytest.mark.asyncio
@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
@patch("ccx_upgrades_data_eng.utils.asyncio.sleep", new_callable=AsyncMock)
@patch("ccx_upgrades_data_eng.utils.time.sleep", return_value=None)
async def test_refresh_sso_token_token_exception(time_sleep_mock, asyncio_sleep_mock, get_session_manager_mock):
    """Check that refresh_sso_token handles TokenException."""
    session_manager_mock = MagicMock()
    session_manager_mock.refresh_token.side_effect = TokenException("test")
    get_session_manager_mock.return_value = session_manager_mock

    resp = await refresh_sso_token(Request({"type": "http"}), mock_call_next)

    assert get_session_manager_mock.called
    assert session_manager_mock.refresh_token.called
    assert not time_sleep_mock.called
    assert asyncio_sleep_mock.called
    assert resp.status_code == 503
    assert resp.body == b'"Unable to update SSO token"'

@pytest.mark.asyncio
@patch("ccx_upgrades_data_eng.main.get_session_manager")
@patch("ccx_upgrades_data_eng.utils.asyncio.sleep", new_callable=AsyncMock)
@patch("ccx_upgrades_data_eng.utils.time.sleep", return_value=None)
async def test_get_session_and_refresh_token_success(time_sleep_mock, asyncio_sleep_mock, get_session_manager_mock):
    """Test successful execution of get_session_and_refresh_token."""
    session_manager_mock = MagicMock()
    get_session_manager_mock.return_value = session_manager_mock

    await get_session_and_refresh_token()

    assert get_session_manager_mock.called
    assert session_manager_mock.refresh_token.called
    assert not time_sleep_mock.called
    assert not asyncio_sleep_mock.called

@pytest.mark.asyncio
@patch("ccx_upgrades_data_eng.main.get_session_manager")
@patch("ccx_upgrades_data_eng.utils.asyncio.sleep", new_callable=AsyncMock)
@patch("ccx_upgrades_data_eng.utils.time.sleep", return_value=None)
async def test_get_session_and_refresh_token_with_retries(time_sleep_mock, asyncio_sleep_mock, get_session_manager_mock):
    """Test get_session_and_refresh_token with retries."""
    session_manager_mock = MagicMock()
    session_manager_mock.refresh_token.side_effect = [TokenException("test"), None]
    get_session_manager_mock.return_value = session_manager_mock

    retry_decorator = get_retry_decorator()
    await retry_decorator(get_session_and_refresh_token)()

    assert get_session_manager_mock.called
    assert session_manager_mock.refresh_token.call_count == 2
    assert not time_sleep_mock.called
    assert asyncio_sleep_mock.called
    assert asyncio_sleep_mock.call_count == 1