@echo off
echo Nuking everything from orbit...
rmdir /s /q venv 2>nul
rmdir /s /q __pycache__ 2>nul
rmdir /s /q core\__pycache__ 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q gpt_pilot.egg-info 2>nul
del /f pythagora.db 2>nul
del /f *.pyc 2>nul

echo Creating fresh venv with Python 3.11...
python3.11 -m venv venv

echo Activating venv...
call venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip wheel setuptools

echo Installing requirements...
pip install -r requirements.txt

echo Setting PYTHONPATH...
set PYTHONPATH=%CD%

echo Done! Try running:
echo python main.py
