"""Contains the manager for Oauth2 session."""

import logging
import time
from functools import lru_cache

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from ccx_upgrades_data_eng.config import get_settings


logger = logging.getLogger(__name__)


class SessionManagerException(Exception):
    """An exception related to the initialization of the session manager."""


class TokenException(Exception):
    """An exception related to the refreshment of the SSO token."""


class Oauth2Manager:
    """Allows to keep track of the authentication token and refresh it when needed."""

    def __init__(
        self, client_id: str, client_secret: str, issuer: str, allow_insecure: bool
    ) -> None:
        """Initialize the Oauth2Manager with the given credentials."""
        logger.debug("Initializing session manager")
        self.client_id = client_id
        self.client_secret = client_secret
        self.issuer = issuer
        self.verify = not allow_insecure

        oauth_config_uri = f"{self.issuer}/.well-known/openid-configuration"

        logger.debug(f"Getting SSO configuration from {oauth_config_uri}")
        try:
            oidc_config = requests.get(oauth_config_uri, verify=self.verify).json()
        except Exception as ex:
            raise SessionManagerException(
                f"Error getting the oauth config from the SSO server:\n{ex}"
            ) from ex

        self._token_endpoint = oidc_config["token_endpoint"]
        logger.debug("Configured token endpoint: %s", self._token_endpoint)

        self.client = BackendApplicationClient(client_id=self.client_id)
        self.session = OAuth2Session(client=self.client)
        self._token = None

    def refresh_token(self) -> str:
        """Refresh the token when it is near to its expiration."""
        logger.debug("Refreshing the token")
        if self._token and self._token["expires_at"] > time.time() + 30.0:
            logger.debug("Token still valid. Not refreshing")
            return

        logger.debug("Token is expired or about to expire. Refreshing")
        try:
            self._token = self.session.fetch_token(
                token_url=self._token_endpoint,
                client_id=self.client_id,
                client_secret=self.client_secret,
                verify=self.verify,
            )
        except Exception as ex:
            raise TokenException(f"Error refreshing the token:\n{ex}") from ex

    def get_session(self) -> OAuth2Session:
        """Return the OauthSession2 after refreshing the auth token."""
        self.refresh_token()
        return self.session


@lru_cache()
def get_session_manager() -> Oauth2Manager:
    """Oauth2Manager cache."""
    settings = get_settings()
    return Oauth2Manager(
        settings.client_id, settings.client_secret, settings.sso_issuer, settings.allow_insecure
    )
