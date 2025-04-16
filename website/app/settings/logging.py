import os
import sys
import logging
import datetime
from pythonjsonlogger import jsonlogger

# 1. Pick the level from ENV
ENV = os.getenv("ENVIRONMENT", "local")  # prod | staging | local
LOG_LEVEL = "INFO" if ENV == "prod" else "DEBUG"

# 2. Build a JSON formatter
json_fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
formatter = jsonlogger.JsonFormatter(json_fmt)

# 3. Console handler (always)
console = logging.StreamHandler(sys.stdout)
console.setFormatter(formatter)

# 4. Optional CloudWatch handler (only when we detect AWS)
handlers = [console]
if os.getenv("AWS_EXECUTION_ENV"):  # present in Lambda, ECS, EB
    import watchtower

    cw_handler = watchtower.CloudWatchLogHandler(
        log_group=f"{os.getenv('APP_NAME','wagtail')}-{ENV}",
        stream_name=datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        create_log_group=False,  # let infra‑as‑code own this
    )
    cw_handler.setFormatter(formatter)
    handlers.append(cw_handler)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"default": {"class": "logging.NullHandler"}},
    "root": {"handlers": handlers, "level": LOG_LEVEL},
}
