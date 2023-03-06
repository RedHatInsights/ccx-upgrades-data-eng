"""Test for config module."""

from ccx_upgrades_data_eng.config import get_settings

import pytest


def test_get_settings_fail():
    """Test get_settings with improper environment configured."""
    get_settings.cache_clear()
    with pytest.raises(Exception):
        get_settings()
