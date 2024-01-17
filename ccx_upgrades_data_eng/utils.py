"""Utilities ysed in the other modules of this package."""

from cachetools import TTLCache
import logging
from ccx_upgrades_data_eng.config import (
    get_settings,
    DEFAULT_CACHE_ENABLED,
    DEFAULT_CACHE_SIZE,
    DEFAULT_CACHE_TTL,
)
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class LoggedTTLCache(TTLCache):
    """TTL Cache with log for items eviction."""

    def popitem(self):
        """Overwrite TTLCache's popitem method to log evicted keys."""
        key, value = super().popitem()
        logger.debug(f"Key {key} evicted")
        print("#" * 50)
        return key, value

    def expire(self, time=None):
        """Overwrite TTLCache's expire to add logs."""
        logger.debug("expiring items from cache")
        return super().expire(time)


class CustomTTLCache(LoggedTTLCache):
    """TTL Cache with TTL for items eviction.

    Use CACHE_ENABLED, CACHE_TTL, and CACHE size env vars to configure it.
    """

    def __init__(self):
        """Read settings or use default values to configure the cache."""
        try:
            settings = get_settings()
            ttl = settings.cache_ttl
            enabled = settings.cache_enabled
            maxsize = settings.cache_size
        except ValidationError:
            logger.debug("Settings not loaded yet. Using default values")
            enabled = DEFAULT_CACHE_ENABLED
            ttl = DEFAULT_CACHE_TTL
            maxsize = DEFAULT_CACHE_SIZE

        logger.debug(f"Cache settings: Enabled: {enabled}, Max size: {maxsize}, TTL: {ttl} seconds")
        if enabled:
            super().__init__(maxsize=maxsize, ttl=ttl)
        else:
            super().__init__(maxsize=0, ttl=0)
