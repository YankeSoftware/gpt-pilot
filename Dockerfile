FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user first to avoid long file ownership operations
RUN useradd -m -u 1000 appuser

# Copy and install requirements first for better caching
COPY --chown=appuser:appuser requirements.txt requirements-dev.txt* ./
COPY --chown=appuser:appuser setup.py .
COPY --chown=appuser:appuser core ./core
COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser example-config.json .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create config if it doesn't exist
RUN if [ ! -f "config.json" ]; then cp example-config.json config.json; fi

USER appuser

# Run the application
CMD ["python", "main.py"]
