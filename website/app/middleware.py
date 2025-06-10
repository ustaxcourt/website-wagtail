import logging
import traceback
from django.utils.deprecation import MiddlewareMixin
from django.utils.cache import patch_cache_control


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


class NoCacheForLoggedInUsersMiddleware(MiddlewareMixin):
    """
    Prevents CloudFront from caching pages served to logged-in users.
    """

    def process_response(self, request, response):
        if request.user.is_authenticated:
            patch_cache_control(response, no_store=True, private=True)
        return response
