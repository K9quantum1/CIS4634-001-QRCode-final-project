@echo off
REM Launcher for RSA+AES Encryption GUI

echo ==========================================
echo RSA+AES Encryption GUI
echo ==========================================
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        echo Please make sure Python is installed and added to PATH.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Check if requirements are installed by testing for a key package
python -c "import cv2" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    echo This may take a few minutes on first run...
    echo.
    pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install required packages.
        pause
        exit /b 1
    )
    echo.
    echo All packages installed successfully.
)

echo.
echo Starting GUI application...
echo.

REM Run the GUI
python gui_app.py

pause
