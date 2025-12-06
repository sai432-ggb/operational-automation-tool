"""
@echo off

echo ==========================================
echo Operational Automation Tool Setup
echo ==========================================

REM Check Python version
python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\\Scripts\\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Ask about dev dependencies
set /p INSTALL_DEV="Install development dependencies? (y/n): "
if /i "%INSTALL_DEV%"=="y" (
    pip install -r requirements-dev.txt
)

REM Create directories
echo Creating directories...
if not exist "data\\input" mkdir data\\input
if not exist "data\\output" mkdir data\\output
if not exist "data\\logs" mkdir data\\logs

REM Create .gitkeep files
type nul > data\\input\\.gitkeep
type nul > data\\output\\.gitkeep
type nul > data\\logs\\.gitkeep

REM Copy configuration files
echo Setting up configuration...
if not exist ".env" (
    copy .env.example .env
    echo Created .env file - please update with your settings
)

if not exist "config\\config.yaml" (
    copy config\\config.example.yaml config\\config.yaml
    echo Created config.yaml - please update with your settings
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env with your configuration
echo 2. Edit config\\config.yaml with your settings
echo 3. Activate virtual environment: venv\\Scripts\\activate.bat
echo 4. Run the tool: python src\\main.py
echo.

pause
