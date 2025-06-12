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


class DebugSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("django.request")

    def __call__(self, request):
        # Log session info before processing
        if "/complete/azuread-tenant-oauth2/" in request.path:
            self.logger.info(
                f"OAuth callback - Session key: {request.session.session_key}"
            )
            self.logger.info(
                f"OAuth callback - Session items: {list(request.session.keys())}"
            )
            self.logger.info(
                f"OAuth callback - Has state: {'state' in request.session}"
            )
            self.logger.info(f"OAuth callback - GET params: {request.GET}")

        response = self.get_response(request)
        return response
