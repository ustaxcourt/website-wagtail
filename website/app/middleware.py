import logging
import traceback

from django.conf import settings
from whitenoise.middleware import WhiteNoiseMiddleware


class JSONExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("django.request")

    def __call__(self, request):
        response = self.get_response(request)

        # Check for 404 responses
        if response.status_code == 404:
            self.logger.info(
                "404 Not Found",
                extra={
                    "path": request.path,
                    "referer": request.META.get("HTTP_REFERER", ""),
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                },
            )
        return response

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
                "remote_addr": request.META.get("REMOTE_ADDR", ""),
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
            response["Cache-Control"] = (
                "private, no-store, no-cache, must-revalidate, max-age=0"
            )
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["X-Logged-In-User"] = "true"

        # Rule 3: For all other requests (anonymous users on non-auth pages),
        # allow caching by shared caches for 5 minutes (300 seconds).
        else:
            response["Cache-Control"] = "max-age=300"

        return response


class NoIndexMiddleware:
    """
    Prevent search engines from indexing this environment.
    Intended to be enabled only in non-prod (e.g., train, dev, qa).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response


class CachedWhiteNoiseMiddleware(WhiteNoiseMiddleware):
    """
    WhiteNoiseMiddleware that indexes STATIC_ROOT once per process instead of
    on every instantiation.

    Wagtail builds a fresh middleware chain for every preview render
    (PreviewableMixin.make_preview_request calls BaseHandler.load_middleware()),
    and when autorefresh is off (DEBUG=False) WhiteNoise's __init__ walks and
    stats every file in STATIC_ROOT. With ~50k collected static files this added
    ~10 seconds to each preview refresh on AWS.

    The index only depends on settings and files baked into the image, so it is
    identical for every instance in a process and safe to share. In autorefresh
    mode (local DEBUG) WhiteNoise doesn't scan at init, so nothing is cached.
    """

    _shared_state: dict | None = None

    def __init__(self, get_response=None, settings=settings):
        shared_state = CachedWhiteNoiseMiddleware._shared_state
        if shared_state is None:
            super().__init__(get_response, settings=settings)
            if not self.autorefresh:
                CachedWhiteNoiseMiddleware._shared_state = self.__dict__.copy()
        else:
            self.__dict__.update(shared_state)
            self.get_response = get_response
