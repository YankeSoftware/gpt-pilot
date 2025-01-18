#!/bin/bash
set -e

echo "Cleaning up previous installation..."

# Remove virtual environment
if [ -d "venv" ]; then
    echo "Removing virtual environment..."
    rm -rf venv
fi

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete

# Remove build artifacts
rm -rf build dist *.egg-info

# Remove Docker containers and images
echo "Cleaning Docker resources..."
docker compose down --rmi all --volumes --remove-orphans 2>/dev/null || true

# Backup .env if it exists
if [ -f ".env" ]; then
    echo "Backing up .env to .env.backup..."
    cp .env .env.backup
fi

# Run setup script
echo "Running fresh setup..."
bash setup.sh

# Restore .env if backup exists
if [ -f ".env.backup" ]; then
    echo "Restoring .env from backup..."
    mv .env.backup .env
fi

echo "Clean installation complete!"
echo "To start the application, either:"
echo "1. Run 'docker compose up' to use Docker"
echo "2. Activate the virtual environment with 'source venv/bin/activate' and run 'python main.py'"

# Make script executable
chmod +x clean_install.sh 