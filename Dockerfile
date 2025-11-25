# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    DJANGO_SETTINGS_MODULE=config.settings.production
# The PORT variable is now provided dynamically by the Railway platform.

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* # Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .
# Collect static files
RUN python manage.py collectstatic --noinput

# Create a start script
RUN echo '#!/bin/sh\n\
exec gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 4 --worker-class gthread --threads 2' > /start && \
    chmod +x /start

# Run the application
CMD ["/start"]