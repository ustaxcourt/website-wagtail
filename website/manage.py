#!/usr/bin/env python
import os
import sys
import logging
import logging.config

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")

    from app.settings import logging as logger

    logging.config.dictConfig(logger.LOGGING)
    log = logging.getLogger("django")
    log.debug(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    log.info("Healthy")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
