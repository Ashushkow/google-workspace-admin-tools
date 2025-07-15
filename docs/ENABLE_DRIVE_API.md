# Включение Google Drive API

## Проблема
Google Drive API не включен в проекте Google Cloud Console.

## Решение

### Автоматическое решение (рекомендуется)
Перейдите по ссылке для автоматического включения API:

**🔗 [ВКЛЮЧИТЬ DRIVE API АВТОМАТИЧЕСКИ](https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=547622531218)**

### Ручное решение

1. **Откройте Google Cloud Console:**
   - Перейдите по ссылке: https://console.cloud.google.com/
   - Убедитесь, что выбран проект `547622531218`

2. **Перейдите в раздел APIs & Services:**
   - В левом меню найдите "APIs & Services"
   - Нажмите на "Library"

3. **Найдите Google Drive API:**
   - В поиске введите "Drive API"
   - Выберите "Google Drive API"

4. **Включите API:**
   - Нажмите кнопку "Enable"
   - Дождитесь завершения процесса (может занять 1-2 минуты)

5. **Проверьте статус:**
   - API должен появиться в разделе "Enabled APIs"

### Альтернативное решение через gcloud CLI

Если у вас установлен gcloud CLI, выполните:

```bash
gcloud config set project 547622531218
gcloud services enable drive.googleapis.com
```

## После включения API

1. Подождите 2-3 минуты для распространения изменений
2. Перезапустите приложение
3. Попробуйте открыть управление документами

## Проверка статуса

Для проверки статуса API используйте команду:
```bash
gcloud services list --enabled --filter="name:drive.googleapis.com"
```
