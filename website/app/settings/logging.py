import sys
from pythonjsonlogger import jsonlogger
from django.conf import settings

# Determine environment
ENV = settings.ENVIRONMENT.lower()
LOG_LEVEL = "INFO" if ENV == "production" else "DEBUG"

# Define log format
LOG_FORMAT = (
    "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s:%(lineno)d %(message)s"
)
formatter = jsonlogger.JsonFormatter(LOG_FORMAT)

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
        "website": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}
