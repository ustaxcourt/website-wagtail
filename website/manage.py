#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.dev")

    from django.core.management import execute_from_command_line

    print("we are here")
    print(os.environ)

    execute_from_command_line(sys.argv)
