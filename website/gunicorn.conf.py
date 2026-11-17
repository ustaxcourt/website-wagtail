"""
Gunicorn settings for the ECS container (see the Dockerfile CMD).

Worker and thread counts are sized per environment in the ECS task definition
(infra/modules/app/locals.tf) and passed in as environment variables.
"""

import os

# gthread workers let quick requests (health checks, admin pings, DB/S3 waits)
# proceed while another request in the same worker is busy rendering.
worker_class = "gthread"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "4"))
timeout = 90

# Load Django once in the master process so the workers share the loaded app
# (including WhiteNoise's static file index) via copy-on-write.
preload_app = True
