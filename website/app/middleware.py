import sys
import logging
import logging.config
import traceback
from pythonjsonlogger import jsonlogger
from django.conf import settings


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
    