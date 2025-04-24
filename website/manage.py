#!/usr/bin/env python
import os
import sys
import logging
import logging.config
log = logging.getLogger("website")


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")
    from django.core.management import execute_from_command_line
    # initialize logging
    import django
    django.setup()

    log.debug(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    log.info("Healthy")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
