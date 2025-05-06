#!/bin/bash

source ./setup.sh

echo "Exporting DATABASE_URL for local connection through tunnel..."
export DATABASE_URL="postgresql://master:${DATABASE_PASSWORD}@localhost:5432/postgres"

echo "DATABASE_URL exported."
echo "Running database migrations (make migrate)..."

cd ../website
make migrate || { echo "ERROR: 'make migrate' failed"; exit 1; }
echo "'make migrate' completed."
echo "Running custom commands (make createpages)..."

make createpages settings="app.settings.${ENVIRONMENT}" || { echo "ERROR: 'make createpages' failed"; exit 1; }
echo "'make createpages' completed."
echo "Migration step finished successfully."

echo "Applied Migrations to database ${DATABASE_HOSTNAME}."
