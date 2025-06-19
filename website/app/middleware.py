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


class CacheControlMiddleware:
    """
    Sets the Cache-Control header based on the request path and user authentication state.
    This single middleware consolidates all caching policies for the application.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Rule 1: Never cache the SSO authentication flow pages.
        # This is the most specific and critical rule to prevent login errors.
        if request.path.startswith("/login/") or request.path.startswith("/complete/"):
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

        # Rule 2: For any other page, if the user is authenticated, prevent caching.
        # 'private' indicates the response is for a single user and should not be
        # stored by a shared cache.
        elif request.user.is_authenticated:
            response[
                "Cache-Control"
            ] = "private, no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["X-Logged-In-User"] = "true"

        # Rule 3: For all other requests (anonymous users on non-auth pages),
        # allow caching by shared caches for 5 minutes (300 seconds).
        else:
            response["Cache-Control"] = "public, max-age=300"

        return response
