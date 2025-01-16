@echo off
echo [1/7] Cleaning up any existing environment...
if exist venv rmdir /s /q venv
if exist __pycache__ rmdir /s /q __pycache__
if exist core\__pycache__ rmdir /s /q core\__pycache__

echo [2/7] Getting Python 3.11 path (tiktoken requirement)...
FOR /F "tokens=* USEBACKQ" %%F IN (`py -3.11 -c "import sys; print(sys.executable)"`) DO (
SET PYTHON_PATH=%%F
)

echo [3/7] Creating virtual environment with Python 3.11...
"%PYTHON_PATH%" -m venv venv

echo [4/7] Activating virtual environment...
call venv\Scripts\activate.bat

echo [5/7] Upgrading pip to latest version...
python -m pip install --upgrade pip

echo [6/7] Installing core dependencies in correct order...
pip install wheel setuptools
pip install pydantic==2.10.5
pip install tiktoken==0.6.0 --no-deps
pip install -r requirements.txt

echo [7/7] Setting up environment variables...
set PYTHONPATH=%CD%;%PYTHONPATH%

echo.
echo Testing imports...
python test_imports.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Setup completed successfully!
) else (
    echo [ERROR] Setup failed. Please check the error messages above.
)
