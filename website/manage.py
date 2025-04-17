#!/usr/bin/env python
import os
import sys
import logging
import logging.config


def main():
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")

    from app.settings import logging as logger

    logging.config.dictConfig(logger.LOGGING)
    log = logging.getLogger("website")
    log.debug(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    log.info("Healthy")

    try:
        main()
    except Exception as e:
        log.exception("Unhandled exception in manage.py")
        raise e
