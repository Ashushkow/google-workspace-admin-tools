# Быстрый запуск Admin Team Tools
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "БЫСТРЫЙ ЗАПУСК Admin Team Tools" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Устанавливаем режим быстрой загрузки..." -ForegroundColor Yellow
$env:FAST_LOAD_MODE = "true"
Write-Host ""
Write-Host "Запускаем приложение с демо-данными..." -ForegroundColor Green
python main.py
Write-Host ""
Write-Host "Приложение завершено." -ForegroundColor Cyan
Read-Host "Нажмите Enter для закрытия"
