import sys
import logging
import logging.config
import traceback
from pythonjsonlogger import jsonlogger
from django.conf import settings


def configure_logging():
    """Configure JSON-formatted logging for the application"""
    # Determine environment
    ENV = settings.ENVIRONMENT.lower()
    LOG_LEVEL = "INFO" if ENV == "production" else "DEBUG"

    # Define log format
    LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s:%(lineno)d %(message)s"

    # Console handler that writes to STDOUT
    console_handler = {
        "level": LOG_LEVEL,
        "class": "logging.StreamHandler",
        "stream": sys.stdout,
        "formatter": "json",
    }

    # Base logging config
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "fmt": LOG_FORMAT,
            },
        },
        "handlers": {
            "console": console_handler,
        },
        "root": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "PIL": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "wagtail": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
            "website": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
                "propagate": False,
            },
        },
    }

    # Apply configuration
    logging.config.dictConfig(LOGGING)
    return LOGGING


class JSONExceptionMiddleware:
    def __init__(self, get_response):
        # Configure logging when middleware is initialized
        configure_logging()
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


# This allows the logging configuration to be imported directly
# from this module without having to call configure_logging()
LOGGING = configure_logging()
