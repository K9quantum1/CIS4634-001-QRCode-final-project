@echo off
echo ========================================
echo   PUSH CLEAN REPO TO GITHUB
echo ========================================
echo.
echo This will REPLACE GitHub with clean history!
echo Only ONE commit with current files.
echo.
echo Your LOCAL files are safe.
echo GitHub will have CLEAN history.
echo.
pause
echo.
echo Pushing to GitHub...
git push -u origin main --force
echo.
echo ========================================
echo   DONE!
echo ========================================
echo.
echo Check GitHub now:
echo https://github.com/K9quantum1/QR-Code-Project
echo.
echo You should see:
echo - Clean repository
echo - Only ONE commit
echo - All current files
echo.
pause

