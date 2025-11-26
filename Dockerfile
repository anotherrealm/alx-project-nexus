FROM python:3.10-slim

# Set general environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOST=0.0.0.0
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Set work directory
WORKDIR /app

# 1. TEMPORARILY SET BUILD-TIME ENV FOR COLLECTSTATIC
# This is necessary because SimpleJWT tries to read settings.SECRET_KEY 
# during the build phase (collectstatic) but Railway's real SECRET_KEY 
# is only available at runtime.
ARG TMDB_API_KEY
ARG SECRET_KEY_BUILD

# Set ENV variables needed for the build (collectstatic)
ENV TMDB_API_KEY=$TMDB_API_KEY
# Use a simple, non-sensitive dummy value for the build only
ENV SECRET_KEY=${SECRET_KEY_BUILD:-TEMPORARY_BUILD_KEY_4789} 


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (This step will now succeed using the TEMPORARY_BUILD_KEY)
RUN python manage.py collectstatic --noinput

# Run the application with Gunicorn, binding to the dynamic $PORT
CMD gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 4 --worker-class gthread --threads 2