@echo off
rem Простой скрипт для автоматического коммита и пуша
rem Использование: auto_commit.bat "Сообщение коммита"

if "%~1"=="" (
    echo Использование: auto_commit.bat "Сообщение коммита"
    exit /b 1
)

rem Добавляем Git в PATH
set "PATH=%PATH%;C:\Program Files\Git\bin"

rem Переходим в папку проекта
cd /d "c:\Users\sputnik8\Documents\Project"

echo Проверяем статус репозитория...
git status

echo.
echo Добавляем все изменения...
git add .

echo.
echo Создаем коммит...
git commit -m "%~1"

echo.
echo Отправляем изменения на GitHub...
git push

echo.
echo Готово! Изменения отправлены на GitHub.
pause
