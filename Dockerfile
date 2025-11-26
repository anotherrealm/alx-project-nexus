# --- BUILDER STAGE ---
# Purpose: Compile all Python packages and collect static files into a minimal layer.
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Set DJANGO_SETTINGS_MODULE for the build steps (collectstatic)
ENV DJANGO_SETTINGS_MODULE=config.settings

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies including Gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# --- PRODUCTION STAGE ---
# Purpose: Create the final, minimal image with only runtime dependencies.
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy Python packages and application code from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder /app /app

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:$PORT", "--workers", "3", "--worker-class", "gthread", "--threads", "2"]