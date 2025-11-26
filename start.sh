#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status
set -o pipefail  # Fail on any error in a pipeline

# Log function for consistent output
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Wait for the database to be ready
log "Waiting for database..."
max_retries=30
retries=0
while [ $retries -lt $max_retries ]; do
    if python -c 'import os; import psycopg2; psycopg2.connect(os.getenv("DATABASE_URL"))' 2>/dev/null; then
        log "Database is ready!"
        break
    fi
    retries=$((retries + 1))
    if [ $retries -eq $max_retries ]; then
        log "Error: Could not connect to database after $max_retries attempts"
        exit 1
    fi
    log "Waiting for database connection... (Attempt $retries/$max_retries)"
    sleep 2
done

# Run migrations
log "Running migrations..."
python manage.py migrate --noinput || { log "Error: Migrations failed"; exit 1; }

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput || { log "Error: Collectstatic failed"; exit 1; }

# Start Gunicorn
log "Starting Gunicorn..."
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
