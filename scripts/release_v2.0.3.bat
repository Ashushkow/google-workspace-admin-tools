@echo off
echo =========================================
echo   Admin Team Tools v2.0.3 Release
echo =========================================
echo.

echo Checking git...
git --version >nul 2>&1
if errorlevel 1 (
    echo Error: Git is not installed
    pause
    exit /b 1
)

echo Adding all files...
git add .

echo Creating commit...
git commit -m "feat: Release v2.0.3 - Организованная структура и исправления"

echo Creating tag...
git tag -a v2.0.3 -m "v2.0.3 - Организованная структура файлов и исправления импортов"

echo Pushing changes...
git push origin main

echo Pushing tags...
git push origin --tags

echo.
echo ========================================
echo   Release v2.0.3 completed successfully!
echo ========================================
echo.
echo Changes included:
echo   * Organized folder structure
echo   * Fixed module imports  
echo   * Updated documentation
echo   * Ready-to-use version
echo.
pause
