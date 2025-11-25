# Use Python 3.11 slim image
FROM python:3.11-slim

# 1. Accept build arguments from railway.json (required for collectstatic)
ARG TMDB_API_KEY
ARG SECRET_KEY

# 2. Convert build arguments into standard ENV variables for the build phase
ENV TMDB_API_KEY=$TMDB_API_KEY
ENV SECRET_KEY=$SECRET_KEY

# Set general environment variables
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
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (This step should now succeed)
RUN python manage.py collectstatic --noinput


# Run the application with Gunicorn, binding to the dynamic $PORT
# CMD gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 4 --worker-class gthread --threads 2