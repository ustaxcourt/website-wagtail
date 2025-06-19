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
        session_state_key = self.state_parameter
        # social_core typically stores the state under a key like 'oauth_state' or 'state'
        # based on the backend name, it might be more specific.
        # Check social_core/backends/oauth.py, line 105 in validate_state for exact key used
        # In many cases, it's simply 'oauth_state' or derived from self.name + '_oauth_state'

        logger.debug("DEBUG: validate_state called. Checking for state in session.")
        logger.debug(
            f"DEBUG: Expected session state key (per backend): {session_state_key}"
        )

        # The actual key used by social_core is typically `self.name + '_oauth_state'`
        # for `AzureADTenantOAuth2` it's likely `azuread-tenant-oauth2_oauth_state`
        # OR it might just be `oauth_state` if SOCIAL_AUTH_FIELDS_STORED_IN_SESSION is simplified.
        # Let's inspect the session more broadly.
        session_content = dict(self.strategy.request.session)
        logger.debug(
            f"DEBUG: Full session content within validate_state: {session_content}"
        )
        logger.debug(
            f"DEBUG: Is '{session_state_key}' in session? {'state' in session_content}"
        )  # Change to match actual key if different
        logger.debug(
            f"DEBUG: Value of '{session_state_key}' in session: {session_content.get(session_state_key, 'NOT_FOUND')}"
        )
        logger.debug(
            f"DEBUG: Value of 'state' in session (generic): {session_content.get('state', 'NOT_FOUND')}"
        )
        logger.debug(
            f"DEBUG: Value of 'oauth_state' in session (generic): {session_content.get('oauth_state', 'NOT_FOUND')}"
        )
        logger.debug(
            f"DEBUG: Value of 'test_oauth_state' in session (from debug view): {session_content.get('test_oauth_state', 'NOT_FOUND')}"
        )

        return super().validate_state()
