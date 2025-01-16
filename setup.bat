@echo off
echo Setting up GPT-Pilot environment...

REM Remove existing venv if it exists
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

REM Create fresh virtual environment
echo Creating new virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install core dependencies
echo Installing core dependencies...
pip install -r requirements-minimal-test.txt

REM Set PYTHONPATH
echo Setting PYTHONPATH...
set PYTHONPATH=%CD%;%PYTHONPATH%

echo Setup complete! Running test_imports.py...
python test_imports.py

echo.
echo If all tests passed, your environment is ready.
echo If you need the full development environment, run: pip install -r requirements.txt
