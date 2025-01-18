#!/bin/bash
set -e

# Check for Python 3.11
if ! command -v python3.11 &> /dev/null && ! python3 --version | grep -q "3.11"; then
    echo "Error: Python 3.11 is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -e .[dev]

# Set PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
EOL
    echo "Please update .env with your API keys"
fi

echo "Setup complete! Don't forget to:"
echo "1. Update your API keys in .env"
echo "2. Run 'source venv/bin/activate' to activate the virtual environment"
echo "3. Use 'docker compose up' to run with Docker"