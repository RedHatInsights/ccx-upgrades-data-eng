"""Service configuration helpers."""

import logging
from functools import lru_cache
from pydantic import ValidationError
from pydantic_settings import BaseSettings

RH_OAUTH_ISSUER = "https://sso.redhat.com/auth/realms/redhat-external"
RHOBS_URL = "https://observatorium.api.stage.openshift.com"
RHOBS_DEFAULT_TENANT = "telemeter"
RHOBS_DEFAULT_REQUEST_TIMEOUT = 10.0

DEFAULT_CACHE_ENABLED = False
DEFAULT_CACHE_TTL = 0
DEFAULT_CACHE_SIZE = 128

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Stores the environment configuration."""

    # SSO related configuration
    client_id: str
    client_secret: str
    sso_issuer: str = RH_OAUTH_ISSUER
    allow_insecure: bool = False
    sso_retry_max_attempts: int = 5
    sso_retry_base_delay: int = 1
    sso_retry_max_delay: int = 30

    # Observatorium configuration
    rhobs_url: str = RHOBS_URL
    rhobs_tenant: str = RHOBS_DEFAULT_TENANT
    rhobs_request_timeout: float = RHOBS_DEFAULT_REQUEST_TIMEOUT
    rhobs_query_max_minutes_for_data: int = 60

    # Inference service configuration
    inference_url: str

    # Caching configuration
    cache_enabled: bool = DEFAULT_CACHE_ENABLED
    cache_ttl: int = DEFAULT_CACHE_TTL
    cache_size: int = DEFAULT_CACHE_SIZE


@lru_cache()
def get_settings() -> Settings:
    """Create the Settings object for the cache."""
    try:
        return Settings()
    except ValidationError as exc:
        if len(exc.args) == 0:
            logger.fatal("Cannot read expected environment variables.")
        else:
            args = [arg.loc_tuple()[0] for arg in exc.args[0]]
            logger.fatal("Cannot read expected environment variables: %s", args)

        raise exc
