# --- BUILDER STAGE ---
# Purpose: Compile all Python packages and collect static files into a minimal layer.
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONFAULTHANDLER=1

# Set DJANGO_SETTINGS_MODULE for the build steps (collectstatic)
ENV DJANGO_SETTINGS_MODULE=config.settings.production

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
RUN python manage.py collectstatic --noinput --no-input

# --- PRODUCTION STAGE ---
# Purpose: Create the final, minimal image with only runtime dependencies.
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PORT=8000 \
    WEB_CONCURRENCY=3 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN addgroup --system django \
    && adduser --system --ingroup django django

# Set work directory and permissions
WORKDIR /app
RUN chown -R django:django /app

# Copy Python packages and application code from the builder stage
COPY --from=builder --chown=django:django /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder --chown=django:django /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder --chown=django:django /app /app

# Switch to non-root user
USER django

# Expose the port the app runs on
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health/ || exit 1

# Command to run the application
CMD ["gunicorn", \
    "--bind", "0.0.0.0:$PORT", \
    "--workers", "$WEB_CONCURRENCY", \
    "--worker-class", "gthread", \
    "--threads", "2", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--log-level", "info", \
    "--timeout", "120", \
    "config.wsgi:application"]