@echo off
setlocal enabledelayedexpansion

echo Cleaning up previous installation...

:: Remove virtual environment
if exist "venv" (
    echo Removing virtual environment...
    rmdir /s /q venv
)

:: Remove Python cache files
echo Removing Python cache files...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

:: Remove build artifacts
if exist "build" rd /s /q build
if exist "dist" rd /s /q dist
if exist "*.egg-info" rd /s /q *.egg-info

:: Remove Docker containers and images
echo Cleaning Docker resources...
docker compose down --rmi all --volumes --remove-orphans 2>nul

:: Backup .env if it exists
if exist ".env" (
    echo Backing up .env to .env.backup...
    copy .env .env.backup >nul
)

:: Run setup script
echo Running fresh setup...
call setup.bat

:: Restore .env if backup exists
if exist ".env.backup" (
    echo Restoring .env from backup...
    move /y .env.backup .env >nul
)

echo Clean installation complete!
echo To start the application, either:
echo 1. Run 'docker compose up' to use Docker
echo 2. Activate the virtual environment with 'venv\Scripts\activate.bat' and run 'python main.py'
