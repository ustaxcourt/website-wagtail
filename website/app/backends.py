import logging
from social_core.backends.azuread_tenant import AzureADTenantOAuth2
from social_core.exceptions import AuthStateMissing

logger = logging.getLogger(__name__)


class DebugAzureADTenantOAuth2(AzureADTenantOAuth2):
    def auth_url(self):
        """
        Overrides the method that generates the authorization URL.
        This is where the 'state' parameter is generated and stored in the session.
        """
        url = super().auth_url()
        # Log session details *after* super().auth_url() has potentially stored state
        # The 'state' will be stored by social_core.backends.oauth.OAuthAuth.state_token()
        # which is called during the auth_url generation.
        logger.debug(
            f"DEBUG: auth_url called. Session key: {self.strategy.request.session.session_key}"
        )
        logger.debug(
            f"DEBUG: Session content after auth_url generation: {dict(self.strategy.request.session)}"
        )
        logger.debug(f"DEBUG: Redirecting to Azure AD URL: {url}")
        return url

    def auth_complete(self, *args, **kwargs):
        """
        Overrides the method that handles the callback from Azure AD.
        This is where 'state' validation occurs.
        """
        logger.debug(
            f"DEBUG: auth_complete called. Request path: {self.strategy.request.path}"
        )
        logger.debug(
            f"DEBUG: Session key during auth_complete: {self.strategy.request.session.session_key}"
        )
        logger.debug(
            f"DEBUG: Session content during auth_complete (before validation): {dict(self.strategy.request.session)}"
        )
        logger.debug(f"DEBUG: Request GET parameters: {self.strategy.request.GET}")
        logger.debug(
            f"DEBUG: Received 'state' from Azure AD in request: {self.data.get('state')}"
        )

        try:
            return super().auth_complete(*args, **kwargs)
        except AuthStateMissing as e:
            logger.error(
                f"DEBUG: AuthStateMissing caught in auth_complete. Exception: {e}",
                exc_info=True,
            )
            # Re-raise the exception after logging for the middleware to catch
            raise

    def validate_state(self):
        """
        Overrides the method specifically responsible for validating the 'state'.
        This will log directly before the core validation logic.
        """
        logger.debug("DEBUG: validate_state called. Checking for state in session.")

        session_content = dict(self.strategy.request.session)

        # The state is typically stored under self.name + '_oauth_state' or just 'oauth_state'
        # based on the backend.name.
        # Let's try to find it dynamically or check common keys.
        expected_state_keys = [
            "oauth_state",  # Common key used by social_core
            f"{self.name}_oauth_state",  # Specific to backend name
            "state",  # Sometimes just 'state' if configured very simply
        ]

        found_state_in_session = "NOT_FOUND"
        for key in expected_state_keys:
            if key in session_content:
                found_state_in_session = session_content.get(key)
                break  # Found a state, use it for logging

        logger.debug(
            f"DEBUG: Full session content within validate_state: {session_content}"
        )
        logger.debug(
            f"DEBUG: Value of potential state in session: {found_state_in_session}"
        )
        logger.debug(
            f"DEBUG: Value of 'test_oauth_state_manual' in session (from debug view): {session_content.get('test_oauth_state_manual', 'NOT_FOUND')}"
        )

        return super().validate_state()
