@echo off
echo ======================================================================
echo 🚀 ADMIN TEAM TOOLS v2.2.0 - Запуск приложения
echo ======================================================================
echo.

REM Проверяем наличие credentials.json
if not exist "credentials.json" (
    echo ❌ ОШИБКА: Файл credentials.json не найден!
    echo.
    echo 📋 Для настройки:
    echo    1. Получите credentials.json из Google Cloud Console
    echo    2. Поместите файл в эту папку
    echo    3. Перезапустите приложение
    echo.
    pause
    exit /b 1
)

echo ✅ Файл credentials.json найден
echo 🔄 Запуск Admin Team Tools...
echo.

REM Запускаем приложение
start "" "AdminTeamTools_v2.2.0.exe"

REM Ждем 3 секунды и закрываем окно
timeout /t 3 /nobreak >nul
exit /b 0
