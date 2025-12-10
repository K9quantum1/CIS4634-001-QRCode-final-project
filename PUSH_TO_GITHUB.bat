@echo off
echo ========================================
echo   PUSH CLEARED REPO TO GITHUB
echo ========================================
echo.
echo This will DELETE EVERYTHING on GitHub!
echo.
pause
echo.
echo Pushing to GitHub...
git push origin main --force
echo.
echo Done! Check GitHub - it should be empty now.
echo.
pause

