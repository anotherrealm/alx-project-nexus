FROM python:3.11-slim

# Accept build arguments (TMDB_API_KEY is often needed for services that run 
# during collectstatic, but SECRET_KEY must be kept out of the build phase for security/consistency)
ARG TMDB_API_KEY

# Convert build arguments into standard ENV variables for the build phase
ENV TMDB_API_KEY=$TMDB_API_KEY
# The SECRET_KEY is intentionally NOT set here; it is sourced only at RUNTIME from Railway's environment variables.

# Set general environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOST=0.0.0.0
ENV DJANGO_SETTINGS_MODULE=config.settings.production

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

# Collect static files
RUN python manage.py collectstatic --noinput

# Run the application with Gunicorn, binding to the dynamic $PORT
CMD gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 4 --worker-class gthread --threads 2