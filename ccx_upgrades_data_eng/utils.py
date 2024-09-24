"""Utilities ysed in the other modules of this package."""

import asyncio
from functools import wraps
from cachetools import TTLCache
import logging
import time
import random
from ccx_upgrades_data_eng.config import (
    get_settings,
    DEFAULT_CACHE_ENABLED,
    DEFAULT_CACHE_SIZE,
    DEFAULT_CACHE_TTL,
)
from pydantic import ValidationError

logger = logging.getLogger(__name__)

DEFAULT_SSO_RETRY_MAX_ATTEMPTS = 5
DEFAULT_SSO_RETRY_BASE_DELAY = 1
DEFAULT_SSO_RETRY_MAX_DELAY = 30


class LoggedTTLCache(TTLCache):
    """TTL Cache with log for items eviction."""

    def popitem(self):
        """Overwrite TTLCache's popitem method to log evicted keys."""
        key, value = super().popitem()
        logger.debug(f"Key {key} evicted")
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


def retry_with_exponential_backoff(
    max_attempts=DEFAULT_SSO_RETRY_MAX_ATTEMPTS,
    base_delay=DEFAULT_SSO_RETRY_BASE_DELAY,
    max_delay=DEFAULT_SSO_RETRY_MAX_DELAY,
):
    """
    Decorate a function with exponential backoff on any exception.

    :param max_attempts: Maximum number of retry attempts
    :param base_delay: Initial delay between retries in seconds
    :param max_delay: Maximum delay between retries in seconds
    """

    def decorator(func):
        # Check if the function is async
        if asyncio.iscoroutinefunction(func):
            # Async wrapper
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts + 1):
                    try:
                        logger.debug(f"Attempt {attempt} of {max_attempts}")
                        return await func(*args, **kwargs)  # Await the async function
                    except Exception as e:
                        if attempt == max_attempts:
                            logger.debug(f"Max retries reached: {attempt}")
                            raise e
                        delay = min(
                            base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1), max_delay
                        )
                        logger.debug(f"Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)

            return async_wrapper
        else:
            # Sync wrapper
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts + 1):
                    try:
                        logger.debug(f"Attempt {attempt} of {max_attempts}")
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_attempts:
                            logger.debug(f"Max retries reached: {attempt}")
                            raise e
                        delay = min(
                            base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1), max_delay
                        )
                        logger.debug(f"Retrying in {delay} seconds... (attempt {attempt})")
                        time.sleep(delay)

            return wrapper

    return decorator


def get_retry_decorator():
    """Get the retry decorator with current settings."""
    try:
        settings = get_settings()
        return retry_with_exponential_backoff(
            max_attempts=settings.sso_retry_max_attempts,
            base_delay=settings.sso_retry_base_delay,
            max_delay=settings.sso_retry_max_delay,
        )
    except ValidationError:
        logger.debug("Settings not loaded yet. Using default values")
        return retry_with_exponential_backoff(
            max_attempts=DEFAULT_SSO_RETRY_MAX_ATTEMPTS,
            base_delay=DEFAULT_SSO_RETRY_BASE_DELAY,
            max_delay=DEFAULT_SSO_RETRY_MAX_DELAY,
        )
