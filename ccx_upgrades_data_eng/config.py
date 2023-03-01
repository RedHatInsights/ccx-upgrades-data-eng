"""Service configuration helpers."""

import logging
from functools import lru_cache

from pydantic import BaseSettings
from pydantic import ValidationError


RH_OAUTH_ISSUER = "https://sso.redhat.com/auth/realms/redhat-external"
RHOBS_URL = "https://observatorium.api.stage.openshift.com"
RHOBS_DEFAULT_TENANT = "telemeter"

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Stores the environment configuration."""

    # SSO related configuration
    client_id: str
    client_secret: str
    sso_issuer: str = RH_OAUTH_ISSUER

    # Observatorium configuration
    rhobs_url: str = RHOBS_URL
    rhobs_tenant: str = RHOBS_DEFAULT_TENANT
    rhobs_request_timeout: float = None

    # Inference service configuration
    inference_url: str


@lru_cache()
def get_settings() -> Settings:
    """Create the Settings object for the cache."""
    try:
        return Settings()
    except ValidationError as exc:
        args = [arg.loc_tuple()[0] for arg in exc.args[0]]
        logger.fatal(
            "Cannot read expected environment variables: %s",
            args,
        )
        raise exc
