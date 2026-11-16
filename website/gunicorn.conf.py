"""
Gunicorn configuration.

Worker and thread counts come from the GUNICORN_WORKERS / GUNICORN_THREADS
environment variables, which Terraform sets per environment on the ECS task.
The defaults below are used when they're unset (e.g. running the image locally).
"""

import os

wsgi_app = "app.wsgi:application"
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# gthread lets each worker serve several requests at once, so a slow page
# render doesn't block health checks or other users.
worker_class = "gthread"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "4"))

# Load the app once in the master before forking so workers share memory.
preload_app = True

timeout = 90
