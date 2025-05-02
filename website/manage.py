#!/usr/bin/env python
import os
import sys
import logging

logger = logging.getLogger("home")


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")
    from django.core.management import execute_from_command_line

    # initialize logging
    import django

    django.setup()

    logger.debug(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    logger.info("Healthy")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
