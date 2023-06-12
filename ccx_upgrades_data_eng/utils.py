"""Utilities ysed in the other modules of this package."""

from datetime import datetime, timedelta
from functools import lru_cache, wraps
import logging
from ccx_upgrades_data_eng.config import (
    get_settings,
    DEFAULT_CACHE_ENABLED,
    DEFAULT_CACHE_SIZE,
    DEFAULT_CACHE_TTL,
)
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def timed_lru_cache():
    """Cache the results of the function decorated with @timed_lru_cache.

    - The caching must be enabled by setting the CACHE_ENABLED environment variable to true/1.
    - The TTL of the cached items can be configured by setting the CACHE_TTL environment variable.
    - The number of simultaneously cached items can be configured by setting the CACHE_SIZE
    environment variable.
    """

    def wrapper_cache(func):
        # check env variables related with cache before anything
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

        if not enabled:
            return func

        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=ttl)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime
            hits = func.cache_info().hits
            res = func(*args, **kwargs)
            if func.cache_info().hits == hits + 1:
                logger.debug("Returned cached result")
            return res

        return wrapped_func

    return wrapper_cache
