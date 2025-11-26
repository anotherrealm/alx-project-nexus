# --- BUILDER STAGE ---
# Purpose: Compile all Python packages and collect static files into a minimal layer.
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install CRITICAL system dependencies for building Python packages.
# These include build tools and headers for common packages like psycopg2 (libpq-dev) 
# and image processing libraries (libjpeg-dev, zlib1g-dev for Pillow).
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
# This step requires the system dependencies installed above.
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
# Note: You must ensure config.settings.production points to the correct static file settings.
RUN python manage.py collectstatic --noinput

# --- PRODUCTION STAGE ---
# Purpose: Create the final, minimal image with only runtime dependencies.
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Ensure this is set to your production settings file
    DJANGO_SETTINGS_MODULE=config.settings 

# Install only RUNTIME system dependencies (e.g., the PostgreSQL client library)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy compiled Python packages and application code from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app /app

# Command to run the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "3", "--worker-class", "gthread", "--threads", "2", "config.wsgi"]