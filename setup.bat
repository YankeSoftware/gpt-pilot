@echo off
setlocal enabledelayedexpansion

:: Check for Python 3.11
python --version 2>nul | findstr "3.11" >nul
if errorlevel 1 (
    echo Error: Python 3.11 is required
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
python -m pip install --upgrade pip

:: Install dependencies
echo Installing dependencies...
pip install -e .[dev]

:: Set PYTHONPATH
set PYTHONPATH=%CD%;%PYTHONPATH%

:: Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    echo OPENAI_API_KEY=your_key_here> .env
    echo ANTHROPIC_API_KEY=your_key_here>> .env
    echo GROQ_API_KEY=your_key_here>> .env
    echo Please update .env with your API keys
)

echo Setup complete! Don't forget to:
echo 1. Update your API keys in .env
echo 2. Run 'venv\Scripts\activate.bat' to activate the virtual environment
echo 3. Use 'docker compose up' to run with Docker
