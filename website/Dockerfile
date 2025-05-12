# Use an official Python runtime based on Debian 12 "bookworm" as a parent image.
FROM --platform=linux/amd64 python:3.12-slim-bookworm

# Add build argument for GitHub SHA
ARG GITHUB_SHA
ENV GITHUB_SHA=${GITHUB_SHA}

ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT}

# Add user that will be used in the container.
RUN useradd wagtail

# Port used by this container to serve HTTP.
EXPOSE 8000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that isa used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install the application server.
RUN pip install "gunicorn==23.0.0"

# Install the project requirements.
COPY requirements/base.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN if [ "$ENVIRONMENT" = "sandbox" ]; then pip install django-debug-toolbar; fi

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Set this directory to be owned by the "wagtail" user. This Wagtail project
# uses SQLite, the folder needs to be owned by the user that
# will be writing to the database file.
RUN chown wagtail:wagtail /app

# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail . .

# Use user "wagtail" to run the build commands below and the server itself.
USER wagtail

# Collect static files.
RUN python manage.py collectstatic --noinput --clear

# Run the service
CMD set -xe; gunicorn --worker-class gevent --workers 3 --timeout 120 app.wsgi:application
