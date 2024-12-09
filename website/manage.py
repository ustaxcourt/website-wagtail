#!/usr/bin/env python
import os
import sys

env = os.getenv("ENV", "dev")

print(f"ENV was set to ${env}")

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"app.settings.{env}")

    print(os.envron)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
