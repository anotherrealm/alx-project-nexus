# --- BUILDER STAGE ---
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONFAULTHANDLER=1

# Set build-time environment variables
ARG SECRET_KEY=temp_build_key
ENV SECRET_KEY=$SECRET_KEY
ENV DEBUG=False
ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project
COPY . .

# Collect static files with a temporary secret key
RUN python manage.py collectstatic --noinput

# --- PRODUCTION STAGE ---
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONFAULTHANDLER=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN addgroup --system django \
    && adduser --system --ingroup django django

# Set work directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy project files
COPY --from=builder --chown=django:django /app /app

# Copy and set up the entrypoint
COPY --chown=django:django start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Switch to non-root user
USER django

# Run the application
CMD ["./start.sh"]
