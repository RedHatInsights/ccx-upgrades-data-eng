"""Test functions of the utils.py module."""
import time
import os
import unittest
from unittest.mock import patch

from ccx_upgrades_data_eng.config import get_settings
from ccx_upgrades_data_eng.tests import needed_env, needed_env_cache_enabled
from ccx_upgrades_data_eng.utils import timed_lru_cache

CACHE_ENABLED_TTL_0, CACHE_ENABLED_SIZE_0 = (
    needed_env_cache_enabled.copy(),
    needed_env_cache_enabled.copy(),
)
CACHE_ENABLED_TTL_0.update(
    {
        "CACHE_ENABLED": "true",
        "CACHE_TTL": "0",
        "CACHE_SIZE": "10",
    }
)
CACHE_ENABLED_SIZE_0.update(
    {
        "CACHE_ENABLED": "true",
        "CACHE_TTL": "10",
        "CACHE_SIZE": "0",
    }
)


class TestLRUCacheDisabled(unittest.TestCase):
    """Test timed_lru_cache function with cache disabled."""

    @classmethod
    def setUpClass(cls):
        """Set up before each test within the class."""
        cls.calls = 0
        get_settings.cache_clear()

    @patch.dict(os.environ, needed_env)
    def test_wrapper_with_cache_disabled(self):
        """Test that items are not cached if CACHE_ENABLED is false."""

        @timed_lru_cache()
        def dummy(x):
            self.calls += 1
            return x + 1

        dummy(1)
        dummy(1)
        assert self.calls == 2


class TestLRUCacheTimeElapsed(unittest.TestCase):
    """Test timed_lru_cache function when TTL passes."""

    @classmethod
    def setUpClass(cls):
        """Set up before each test within the class."""
        cls.calls = 0
        get_settings.cache_clear()

    @patch.dict(os.environ, needed_env_cache_enabled)
    def test_wrapper_with_cache_enabled_time_elapsed(self):
        """Test that cached items are evicted after CACHE_TTL has passed."""

        @timed_lru_cache()
        def dummy(x):
            self.calls += 1
            return x + 1

        dummy(1)
        time.sleep(1)
        dummy(1)
        assert self.calls == 2


class TestLRUCacheTTLZero(unittest.TestCase):
    """Test timed_lru_cache function with different TTLs."""

    @classmethod
    def setUpClass(cls):
        """Set up before each test within the class."""
        cls.calls = 0
        get_settings.cache_clear()

    @patch.dict(os.environ, CACHE_ENABLED_TTL_0)
    def test_wrapper_with_cache_enabled_ttl_0(self):
        """Test that with TTL 0, items are not cached."""

        @timed_lru_cache()
        def dummy(x):
            self.calls += 1
            return x + 1

        dummy(1)
        dummy(1)
        assert self.calls == 2


class TestLRUCacheSize(unittest.TestCase):
    """Test timed_lru_cache function with different cache sizes."""

    @classmethod
    def setUpClass(cls):
        """Set up before each test within the class."""
        cls.calls = 0
        get_settings.cache_clear()

    @patch.dict(os.environ, CACHE_ENABLED_SIZE_0)
    def test_wrapper_with_cache_enabled_size_0(self):
        """Test that with size 0, items are not cached."""

        @timed_lru_cache()
        def dummy(x):
            self.calls += 1
            return x + 1

        dummy(1)
        assert self.calls == 1
        dummy(1)
        assert self.calls == 2
