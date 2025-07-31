# PowerShell скрипт для управления UX версиями Admin Team Tools
# Позволяет переключаться между оригинальной и улучшенной версией

Write-Host "🔄 UX Version Manager - Admin Team Tools" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Проверяем наличие файлов
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Основной файл main.py не найден!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "main_ux_improved.py")) {
    Write-Host "❌ Улучшенная версия main_ux_improved.py не найдена!" -ForegroundColor Red
    exit 1
}

# Определяем текущую версию
$currentVersion = ""
$mainContent = Get-Content "main.py" -Raw
if ($mainContent -match "UX IMPROVED VERSION") {
    $currentVersion = "improved"
} else {
    $currentVersion = "original"
}

Write-Host "📊 Текущая версия: " -NoNewline
Write-Host $currentVersion -ForegroundColor Blue
Write-Host ""

Write-Host "Выберите действие:"
Write-Host "1) Переключиться на улучшенную UX версию"
Write-Host "2) Вернуться к оригинальной версии"
Write-Host "3) Показать информацию о версиях"
Write-Host "4) Создать резервную копию текущей версии"
Write-Host "5) Тестовый запуск улучшенной версии"
Write-Host "6) Выход"
Write-Host ""

$choice = Read-Host "Введите номер (1-6)"

switch ($choice) {
    "1" {
        if ($currentVersion -eq "improved") {
            Write-Host "⚠️ Уже используется улучшенная версия!" -ForegroundColor Yellow
        } else {
            Write-Host "🔄 Переключение на улучшенную UX версию..." -ForegroundColor Blue
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            Copy-Item "main.py" "main_original_backup_$timestamp.py"
            Copy-Item "main_ux_improved.py" "main.py"
            Write-Host "✅ Успешно переключено на улучшенную версию!" -ForegroundColor Green
            Write-Host "💾 Оригинал сохранен как main_original_backup_$timestamp.py" -ForegroundColor Yellow
        }
    }
    "2" {
        if ($currentVersion -eq "original") {
            Write-Host "⚠️ Уже используется оригинальная версия!" -ForegroundColor Yellow
        } else {
            Write-Host "🔄 Возврат к оригинальной версии..." -ForegroundColor Blue
            
            # Ищем последний backup оригинала
            $backupFiles = Get-ChildItem "main_original_backup_*.py" | Sort-Object LastWriteTime -Descending
            if ($backupFiles.Count -gt 0) {
                $latestBackup = $backupFiles[0].Name
                Copy-Item $latestBackup "main.py"
                Write-Host "✅ Успешно восстановлена оригинальная версия из $latestBackup" -ForegroundColor Green
            } else {
                Write-Host "❌ Backup оригинальной версии не найден!" -ForegroundColor Red
                Write-Host "💡 Попробуйте восстановить из git: git checkout HEAD~1 main.py" -ForegroundColor Yellow
            }
        }
    }
    "3" {
        Write-Host "📋 Информация о версиях:" -ForegroundColor Blue
        Write-Host ""
        Write-Host "🔸 Оригинальная версия:"
        Write-Host "  • Стандартный баннер запуска"
        Write-Host "  • Базовая обработка ошибок"
        Write-Host "  • Проверенная стабильность"
        Write-Host ""
        Write-Host "🔸 Улучшенная UX версия:"
        Write-Host "  • Красивый прогресс-бар загрузки"
        Write-Host "  • Анимированные индикаторы"
        Write-Host "  • Подробная диагностика подключения"
        Write-Host "  • Информативные сообщения об ошибках"
        Write-Host "  • Подсказки по горячим клавишам"
        Write-Host "  • Улучшенная визуальная структура"
        Write-Host ""
        
        # Показываем размеры файлов
        $originalSize = (Get-Item "main.py").Length
        $improvedSize = (Get-Item "main_ux_improved.py").Length
        Write-Host "📊 Размеры файлов:"
        Write-Host "  • main.py: $originalSize байт"
        Write-Host "  • main_ux_improved.py: $improvedSize байт"
    }
    "4" {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupName = "main_manual_backup_$timestamp.py"
        Copy-Item "main.py" $backupName
        Write-Host "✅ Резервная копия создана: $backupName" -ForegroundColor Green
    }
    "5" {
        Write-Host "🧪 Тестовый запуск улучшенной версии..." -ForegroundColor Blue
        Write-Host "💡 Это покажет новый интерфейс без изменения основного файла" -ForegroundColor Yellow
        Write-Host ""
        python main_ux_improved.py
    }
    "6" {
        Write-Host "👋 Выход из менеджера версий" -ForegroundColor Blue
        exit 0
    }
    default {
        Write-Host "❌ Неверный выбор!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎯 Операция завершена!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Полезные команды:"
Write-Host "  • python main.py                    - запуск приложения"
Write-Host "  • PowerShell .\switch_ux.ps1        - повторный вызов этого скрипта"
Write-Host "  • Get-ChildItem main*.py             - список всех версий"
Write-Host "  • python main_ux_improved.py        - тестовый запуск улучшенной версии"
Write-Host ""

# Предлагаем протестировать если переключились на улучшенную версию
if ($choice -eq "1" -and $currentVersion -eq "original") {
    Write-Host "🚀 Хотите сразу протестировать новую версию? (y/n): " -ForegroundColor Cyan -NoNewline
    $testChoice = Read-Host
    if ($testChoice -eq "y" -or $testChoice -eq "Y") {
        Write-Host "▶️ Запуск приложения с новым UX..." -ForegroundColor Green
        python main.py
    }
}
