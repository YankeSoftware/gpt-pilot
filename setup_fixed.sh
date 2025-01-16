#!/bin/bash
set -e  # Exit on any error

echo "[1/7] Cleaning up any existing environment..."
rm -rf venv __pycache__ core/__pycache__

echo "[2/7] Checking Python version..."
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD=python3.10
else
    echo "Error: Python 3.11 or 3.10 is required but not found"
    exit 1
fi

echo "[3/7] Creating virtual environment with $PYTHON_CMD..."
$PYTHON_CMD -m venv venv

echo "[4/7] Activating virtual environment..."
source venv/bin/activate

echo "[5/7] Upgrading pip to latest version..."
python -m pip install --upgrade pip

echo "[6/7] Installing core dependencies in correct order..."
pip install wheel setuptools
pip install pydantic==2.10.5
pip install tiktoken==0.6.0 --no-deps
pip install -r requirements.txt

echo "[7/7] Setting up environment variables..."
export PYTHONPATH=$(pwd):$PYTHONPATH

echo ""
echo "Testing imports..."
python test_imports.py

echo ""
if [ $? -eq 0 ]; then
    echo "[SUCCESS] Setup completed successfully!"
else
    echo "[ERROR] Setup failed. Please check the error messages above."
fi