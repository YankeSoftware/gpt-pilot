@echo off
setlocal EnableDelayedExpansion

echo [1/7] Nuclear cleanup in progress...
echo.

REM Kill all Python-related directories
rmdir /s /q venv 2>nul
rmdir /s /q __pycache__ 2>nul
rmdir /s /q core\__pycache__ 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q gpt_pilot.egg-info 2>nul
del /f /q pythagora.db 2>nul

echo [2/7] Checking Python installation...
py -3.11 --version 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python 3.11 not found! Please install it from:
    echo https://www.python.org/downloads/release/python-3116/
    echo And make sure to check "Add to PATH" during installation
    exit /b 1
)

echo [3/7] Creating fresh virtual environment with Python 3.11...
py -3.11 -m venv venv
if %ERRORLEVEL% neq 0 (
    echo Failed to create virtual environment!
    exit /b 1
)

echo [4/7] Activating virtual environment...
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment!
    exit /b 1
)

echo [5/7] Upgrading pip...
python -m pip install --upgrade pip --no-warn-script-location

echo [6/7] Installing core dependencies in correct order...
pip install --no-warn-script-location wheel setuptools
pip install --no-warn-script-location pydantic==2.10.5
pip install --no-warn-script-location openai==1.40.6
pip install --no-warn-script-location sqlalchemy[asyncio]==2.0.32
pip install --no-warn-script-location aiosqlite==0.20.0
pip install --no-warn-script-location python-dotenv==1.0.1
pip install --no-warn-script-location -r requirements.txt

echo [7/7] Setting up environment...
set PYTHONPATH=%CD%

echo.
echo Testing installation...
python -c "import core.config" 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Installation verification failed!
    echo Please screenshot any errors and report them.
) else (
    echo [SUCCESS] Installation verified!
    echo.
    echo You can now run: python main.py
)

echo.
echo If you need to clean up user-level packages, run:
echo pip uninstall -y openai anthropic groq sqlalchemy pydantic tiktoken

pause