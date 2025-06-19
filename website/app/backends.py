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
        This will log the full session content, then let the parent method handle validation.
        """
        logger.debug(
            "DEBUG: validate_state called. About to let super() handle state validation."
        )
        session_content = dict(self.strategy.request.session)
        logger.debug(
            f"DEBUG: Full session content within validate_state: {session_content}"
        )
        # The key for social_core_state in session is typically backend_name + '_state'
        # e.g., 'azuread-tenant-oauth2_state'
        logger.debug(f"DEBUG: Expecting state under key: {self.name}_state")
        logger.debug(
            f"DEBUG: Value of {self.name}_state in session: {session_content.get(f'{self.name}_state', 'NOT_FOUND')}"
        )
        logger.debug(
            f"DEBUG: Value of 'test_oauth_state_manual' in session (from debug view): {session_content.get('test_oauth_state_manual', 'NOT_FOUND')}"
        )

        # Now, call the parent's validate_state method.
        # If the state is truly missing for social_core's logic, it will raise AuthStateMissing.
        return super().validate_state()
