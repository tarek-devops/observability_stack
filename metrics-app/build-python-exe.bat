@echo off
REM Build Windows executable from Python script using PyInstaller

echo ========================================
echo Building Metrics Sender Executable
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from python.org
    pause
    exit /b 1
)

echo.
echo Installing required packages...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building executable...
pyinstaller --onefile --name metrics-sender simple-metrics-sender.py

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Executable location: dist\metrics-sender.exe
    echo.
    echo To run:
    echo   1. Set OTEL_ENDPOINT environment variable
    echo      set OTEL_ENDPOINT=your-ip:4318
    echo   2. Run: dist\metrics-sender.exe
    echo ========================================
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    pause
    exit /b 1
)

pause