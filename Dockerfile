FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy requirements first to leverage Docker cache
COPY --chown=appuser:appuser requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt uvicorn watchfiles python-socketio[asyncio]

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Run the application
CMD ["python", "main.py"]
