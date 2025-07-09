# 🔧 Создание OAuth 2.0 Credentials для Admin Team Tools

## 🎯 Быстрая настройка OAuth 2.0

OAuth 2.0 проще в настройке, чем Service Account, и отлично подходит для desktop приложений.

## 🚀 Пошаговая инструкция

### Шаг 1: Откройте Google Cloud Console

1. Перейдите по ссылке: https://console.cloud.google.com/
2. Выберите проект: **admin-project-464720**

### Шаг 2: Создайте OAuth 2.0 Credentials

1. В боковом меню: **APIs & Services** → **Credentials**
2. Нажмите **+ CREATE CREDENTIALS**
3. Выберите **OAuth 2.0 Client IDs**

### Шаг 3: Настройте OAuth Client

1. **Application type**: `Desktop application`
2. **Name**: `Admin Team Tools Desktop`
3. Нажмите **CREATE**

### Шаг 4: Скачайте credentials.json

1. После создания появится окно с Client ID и Secret
2. Нажмите **DOWNLOAD JSON**
3. Сохраните файл как `credentials.json` в корневую папку проекта:
   ```
   c:\Users\sputnik8\Documents\Project\credentials.json
   ```

### Шаг 5: Замените текущий файл

1. **Удалите или переименуйте** текущий `credentials.json` (Service Account)
2. **Поместите новый** OAuth 2.0 `credentials.json` в корень проекта

## ✅ Формат OAuth 2.0 credentials.json

Ваш новый файл должен выглядеть примерно так:

```json
{
  "installed": {
    "client_id": "123456789-abcdef.apps.googleusercontent.com",
    "project_id": "admin-project-464720",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-abcdef123456",
    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
  }
}
```

## 🧪 Проверка настройки

После создания файла запустите проверку:

```bash
python check_setup.py
```

Если все настроено правильно, запустите приложение:

```bash
python main.py
```

## 🌐 Первый запуск

При первом запуске приложения:

1. **Откроется браузер** с запросом на авторизацию
2. **Войдите** под аккаунтом `andrei.shushkov@sputnik8.com`
3. **Разрешите доступ** к Google Workspace Admin API
4. **Браузер покажет** "The authentication flow has completed"
5. **Приложение запустится** автоматически

## ✨ Преимущества OAuth 2.0

- ✅ **Простая настройка** - не нужен Domain-wide delegation
- ✅ **Безопасность** - токены автоматически обновляются
- ✅ **Удобство** - один раз авторизуется, потом работает без браузера
- ✅ **Отладка** - понятные сообщения об ошибках

## 🔄 Переключение с Service Account

Если у вас был Service Account:

1. **Переименуйте** старый файл: `credentials.json` → `credentials_service_account_backup.json`
2. **Создайте новый** OAuth 2.0 credentials (шаги выше)
3. **Удалите** старый токен: `token.pickle` (если есть)
4. **Запустите** `python main.py`

---

**OAuth 2.0 готов к использованию! Никакой дополнительной настройки не требуется.** 🎉
