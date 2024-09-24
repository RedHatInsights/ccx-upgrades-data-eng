"""Tests for utils module."""

from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from ccx_upgrades_data_eng.utils import LoggedTTLCache, retry_with_exponential_backoff


# ----------------------------------------------------------------------
# Tests for LoggedTTLCache
# ----------------------------------------------------------------------
@patch("ccx_upgrades_data_eng.utils.logger")
def test_logged_ttl_cache_popitem(logger_mock):
    """Test the LoggedTTLCache class."""
    cache = LoggedTTLCache(maxsize=1, ttl=10)

    cache[0] = 0
    key, value = cache.popitem()

    assert key == 0
    assert value == 0
    assert logger_mock.debug.called


# ----------------------------------------------------------------------
# Synchronous tests for retry_with_exponential_backoff
# ----------------------------------------------------------------------
def test_retry_with_exponential_backoff_success():
    """Test that the function succeeds without retries."""
    mock_func = MagicMock(return_value="success")

    decorated_func = retry_with_exponential_backoff()(mock_func)
    result = decorated_func()

    assert result == "success"
    assert mock_func.call_count == 1


@patch("time.sleep", return_value=None)  # Mock sleep to avoid delays
def test_retry_with_exponential_backoff_retries(mock_sleep):
    """Test that the function retries on exception."""
    mock_func = MagicMock(side_effect=[Exception("fail"), "success"])

    decorated_func = retry_with_exponential_backoff()(mock_func)
    result = decorated_func()

    assert result == "success"
    assert mock_func.call_count == 2
    assert mock_sleep.call_count == 1


@patch("time.sleep", return_value=None)
def test_retry_with_exponential_backoff_max_attempts(mock_sleep):
    """Test that the function raises an exception after max attempts."""
    mock_func = MagicMock(side_effect=Exception("fail"))

    decorated_func = retry_with_exponential_backoff(max_attempts=3)(mock_func)

    with pytest.raises(Exception, match="fail"):
        decorated_func()

    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2


@patch("time.sleep", return_value=None)
def test_retry_with_exponential_backoff_delay(mock_sleep):
    """Test that the function uses exponential backoff delay."""
    mock_func = MagicMock(side_effect=[Exception("fail"), Exception("fail"), "success"])

    decorated_func = retry_with_exponential_backoff(base_delay=1, max_delay=5)(mock_func)
    result = decorated_func()

    assert result == "success"
    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2
    # Check that the delays are within the expected range
    delays = [call[0][0] for call in mock_sleep.call_args_list]
    assert all(1 <= delay <= 5 for delay in delays)


@patch("time.sleep", return_value=None)
def test_retry_with_exponential_backoff_custom_delays(mock_sleep):
    """Test that the function respects custom base delay and max delay."""
    mock_func = MagicMock(side_effect=[Exception("fail"), Exception("fail"), "success"])

    decorated_func = retry_with_exponential_backoff(base_delay=2, max_delay=10)(mock_func)
    result = decorated_func()

    assert result == "success"
    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2
    # Check that the delays are within the expected range
    delays = [call[0][0] for call in mock_sleep.call_args_list]
    assert all(2 <= delay <= 10 for delay in delays)


@patch("time.sleep", return_value=None)
def test_retry_with_exponential_backoff_different_exceptions(mock_sleep):
    """Test that the function retries on different types of exceptions."""
    mock_func = MagicMock(side_effect=[ValueError("fail"), KeyError("fail"), "success"])

    decorated_func = retry_with_exponential_backoff()(mock_func)
    result = decorated_func()

    assert result == "success"
    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2


# ----------------------------------------------------------------------
# Asynchronous tests for retry_with_exponential_backoff
# ----------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_retry_with_exponential_backoff_success():
    """Test that the async function succeeds without retries."""
    mock_func = AsyncMock(return_value="success")

    decorated_func = retry_with_exponential_backoff()(mock_func)
    result = await decorated_func()

    assert result == "success"
    assert mock_func.call_count == 1


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_async_retry_with_exponential_backoff_retries(mock_sleep):
    """Test that the async function retries on exception."""
    mock_func = AsyncMock(side_effect=[Exception("fail"), "success"])

    decorated_func = retry_with_exponential_backoff()(mock_func)
    result = await decorated_func()

    assert result == "success"
    assert mock_func.call_count == 2
    assert mock_sleep.call_count == 1


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_async_retry_with_exponential_backoff_max_attempts(mock_sleep):
    """Test that the async function raises an exception after max attempts."""
    mock_func = AsyncMock(side_effect=Exception("fail"))

    decorated_func = retry_with_exponential_backoff(max_attempts=3)(mock_func)

    with pytest.raises(Exception, match="fail"):
        await decorated_func()

    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_async_retry_with_exponential_backoff_delay(mock_sleep):
    """Test that the async function uses exponential backoff delay."""
    mock_func = AsyncMock(side_effect=[Exception("fail"), Exception("fail"), "success"])

    decorated_func = retry_with_exponential_backoff(base_delay=1, max_delay=5)(mock_func)
    result = await decorated_func()

    assert result == "success"
    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2
    # Check that the delays are within the expected range
    delays = [call[0][0] for call in mock_sleep.call_args_list]
    assert all(1 <= delay <= 5 for delay in delays)


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_async_retry_with_exponential_backoff_different_exceptions(mock_sleep):
    """Test that the async function retries on different types of exceptions."""
    mock_func = AsyncMock(side_effect=[ValueError("fail"), KeyError("fail"), "success"])

    decorated_func = retry_with_exponential_backoff()(mock_func)
    result = await decorated_func()

    assert result == "success"
    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2
