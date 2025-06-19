import logging
import traceback


class JSONExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("django.request")

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Process exceptions and log them as JSON
        """
        trace = traceback.format_exc()
        self.logger.error(
            "Unhandled exception",
            extra={
                "path": request.path,
                "method": request.method,
                "exception": str(exception),
                "traceback": trace,
            },
        )

        # Let Django handle the response normally
        return None


class NoCacheForLoggedInUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            response[
                "Cache-Control"
            ] = "private, no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["X-Logged-In-User"] = "true"
        else:
            response["Cache-Control"] = "max-age=300"
        return response


def debug_session_and_request(strategy, *args, **kwargs):
    # Log as an ERROR to ensure it has high visibility in your logs
    backend_name = kwargs.get("backend").name
    session_key = f"{backend_name}_state"

    print("--- EXECUTION PROOF: DEBUG PIPELINE STEP IS RUNNING ---")
    print(f"Backend: {kwargs.get('backend').name}")
    print(f"Session Keys: {list(strategy.session.keys())}")
    azuread_state = strategy.session.get("azuread-tenant-oauth2_state")
    print(f"Azure AD State in Session: {azuread_state}")
    print(f"Session Keys: {list(strategy.session.keys())}")
    print(f"Looking for session key: {session_key}")
    print(f"State value in session: {strategy.session.get(session_key)}")
    print("-----------------------------------------------------")
