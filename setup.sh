#!/bin/bash
echo "Setting up GPT-Pilot environment..."

# Remove existing venv if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create fresh virtual environment
echo "Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install core dependencies
echo "Installing core dependencies..."
pip install -r requirements-minimal-test.txt

# Set PYTHONPATH
echo "Setting PYTHONPATH..."
export PYTHONPATH=$(pwd):$PYTHONPATH

echo "Setup complete! Running test_imports.py..."
python test_imports.py

echo ""
echo "If all tests passed, your environment is ready."
echo "If you need the full development environment, run: pip install -r requirements.txt"