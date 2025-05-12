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


# Example of a simple middleware for debugging headers
# (add to the top of your MIDDLEWARE list in settings for temporary debugging)
class DebugHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "/admin/editing-sessions/ping/" in request.path:
            print(f"DEBUG PING Request Path: {request.path}")
            print(f"DEBUG PING Is Secure: {request.is_secure()}")
            print("DEBUG PING Headers:")
            for header, value in request.META.items():
                if header.startswith("HTTP_") or header in (
                    "CONTENT_TYPE",
                    "CONTENT_LENGTH",
                ):
                    print(f"  {header}: {value}")
        response = self.get_response(request)
        return response
