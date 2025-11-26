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

# Install CRITICAL system dependencies for building Python packages.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip and required packages
RUN pip install --upgrade pip

# Set work directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

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
    # The runtime setting uses the production/default settings path
    DJANGO_SETTINGS_MODULE=config.settings 

# Install only RUNTIME system dependencies (e.g., the PostgreSQL client library)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy compiled Python packages and application code from the builder stage
# Copy the entire Python local installation prefix to ensure all binaries and library dependencies are included.
COPY --from=builder /usr/local/ /usr/local/
COPY --from=builder /app /app

# Expose the port the app runs on
EXPOSE $PORT

# FINAL CRITICAL FIX: Run gunicorn as a Python module to avoid PATH/executable location issues.
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "3", "--worker-class", "gthread", "--threads", "2", "config.wsgi"]