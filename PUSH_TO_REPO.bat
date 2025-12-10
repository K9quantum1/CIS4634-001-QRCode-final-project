@echo off
REM Script to push changes to GitHub repository

echo ==========================================
echo Pushing to GitHub Repository
echo ==========================================
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Initialize git if not already initialized
if not exist ".git" (
    echo Initializing git repository...
    git init
    echo.
)

REM Add the remote repository
echo Setting up remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/K9quantum1/Final-Project-.git
echo.

REM Add all files
echo Adding files...
git add .
echo.

REM Commit changes
echo Committing changes...
git commit -m "Fix RUN.bat to work on fresh installations - auto-setup venv and dependencies"
echo.

REM Push to GitHub
echo Pushing to GitHub...
git branch -M main
git push -u origin main
echo.

echo ==========================================
echo Push complete!
echo ==========================================
pause

