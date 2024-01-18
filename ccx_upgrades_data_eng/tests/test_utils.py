"""Tests for utils module."""

from unittest.mock import patch

from ccx_upgrades_data_eng.utils import LoggedTTLCache


@patch("ccx_upgrades_data_eng.utils.logger")
def test_logged_ttl_cache_popitem(logger_mock):
    """Test the LoggedTTLCache class."""
    cache = LoggedTTLCache(maxsize=1, ttl=10)

    cache[0] = 0
    key, value = cache.popitem()

    assert key == 0
    assert value == 0
    assert logger_mock.debug.called
