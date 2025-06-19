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
    print("--- DEBUGGING SOCIAL AUTH PIPELINE ---")
    print(f"Backend: {kwargs.get('backend').name}")
    print(f"Session Keys: {list(strategy.session.keys())}")
    azuread_state = strategy.session.get("azuread-tenant-oauth2_state")
    print(f"Azure AD State in Session: {azuread_state}")
    print("------------------------------------")
