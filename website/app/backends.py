import logging
from social_core.backends.azuread_tenant import AzureADTenantOAuth2
from social_core.exceptions import AuthStateMissing

logger = logging.getLogger(__name__)


class DebugAzureADTenantOAuth2(AzureADTenantOAuth2):
    """Custom Azure AD backend with enhanced debugging"""

    def validate_state(self):
        """Override state validation with better debugging"""
        logger.info("=== OAuth State Validation Debug ===")

        # Check what we got from the callback
        state_from_request = self.data.get("state")
        logger.info(f"State from OAuth callback: {state_from_request}")

        # Check what's in session
        session = self.strategy.session
        logger.info(
            f"Session keys: {list(session.keys()) if hasattr(session, 'keys') else 'No keys method'}"
        )
        logger.info(
            f"Session contents: {dict(session) if hasattr(session, 'items') else 'Cannot iterate'}"
        )

        # Check for state in various possible session keys
        possible_state_keys = [
            "state",
            f"{self.name}_state",
            "social_auth_state",
            "azuread-tenant-oauth2_state",
        ]

        for key in possible_state_keys:
            value = session.get(key)
            logger.info(f"Session key '{key}': {value}")

        # Try the original validation
        try:
            return super().validate_state()
        except AuthStateMissing as e:
            logger.error(f"State validation failed: {e}")
            logger.error(
                f"Expected state from session, got state from request: {state_from_request}"
            )
            raise

    def auth_complete(self, *args, **kwargs):
        """Override auth_complete with debugging"""
        logger.info("=== OAuth Auth Complete Debug ===")
        logger.info(f"Request data: {dict(self.data)}")
        logger.info(f"Session before validation: {dict(self.strategy.session)}")

        return super().auth_complete(*args, **kwargs)


# Update your AUTHENTICATION_BACKENDS in base.py to use this:
# AUTHENTICATION_BACKENDS = [
#     "app.backends.DebugAzureADTenantOAuth2",  # Use debug backend
#     "django.contrib.auth.backends.ModelBackend",
# ]
