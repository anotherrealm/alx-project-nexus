#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# Wait for the database to be ready
echo "Waiting for database..."
until python -c 'import os; import sys; import psycopg2; \
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))' 2>/dev/null; do
  echo "Waiting for database connection..."
  sleep 1
done

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn \
    --bind "0.0.0.0:$PORT" \
    --workers "$WEB_CONCURRENCY" \
    --worker-class "gthread" \
    --threads "2" \
    --access-logfile "-" \
    --error-logfile "-" \
    --log-level "info" \
    --timeout "120" \
    "config.wsgi:application"
