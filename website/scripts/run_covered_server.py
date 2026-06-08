#!/usr/bin/env python
"""
Run Django's dev server under coverage instrumentation with reliable shutdown.

Standard `coverage run manage.py runserver` relies on Python's atexit to flush
coverage data, but atexit doesn't run after SIGKILL. Django's threaded dev
server often ignores SIGINT long enough that the workflow's 30-second kill
timer fires, resulting in SIGKILL and no coverage file.

This script installs explicit SIGINT and SIGTERM handlers that call
coverage.stop() / coverage.save() and then os._exit(), bypassing both the
atexit problem and any non-daemon threads that would otherwise block sys.exit().
"""

import os
import runpy
import signal
import sys

# runpy.run_path on a .py file does not update sys.path the way `python
# manage.py` does. Add website/ (parent of this scripts/ dir) explicitly so
# that `app`, `home`, and other project packages are importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import coverage

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")

cov = coverage.Coverage(
    config_file=".coveragerc.e2e",
    data_file=os.environ.get("COVERAGE_FILE", ".coverage.e2e"),
    data_suffix=True,
)
cov.start()


def _shutdown(signum, frame):
    cov.stop()
    cov.save()
    os._exit(0)


signal.signal(signal.SIGTERM, _shutdown)
signal.signal(signal.SIGINT, _shutdown)

sys.argv = ["manage.py", "runserver", "--noreload", "0.0.0.0:8000"]
runpy.run_path("manage.py", run_name="__main__")

cov.stop()
cov.save()
