FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including ttyd
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && wget https://github.com/tsl0922/ttyd/releases/download/1.7.3/ttyd.x86_64 -O /usr/local/bin/ttyd \
    && chmod +x /usr/local/bin/ttyd

# Install Python dependencies first
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install the package in editable mode
COPY setup.py .
COPY core core/
RUN pip install -e .

# Copy remaining project files
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create example config if it doesn't exist
RUN if [ ! -f "config.json" ]; then cp example-config.json config.json; fi

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Test the installation
RUN python -c "import core.config; print('Core config imported successfully')"

# Run the server
CMD ttyd -p 7681 bash & python main.py