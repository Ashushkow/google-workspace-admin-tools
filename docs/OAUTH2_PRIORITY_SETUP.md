# 🔐 OAuth 2.0 Setup Guide для Google Workspace

> **Приоритетный метод авторизации**: OAuth 2.0 обеспечивает интерактивную и безопасную авторизацию для Desktop приложений.

## 📋 Пошаговая настройка

### 1. Подготовка Google Cloud Console

#### 1.1 Создание проекта
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Нажмите **"Select a project"** → **"New Project"**
3. Введите название проекта: `Admin Team Tools`
4. Нажмите **"Create"**

#### 1.2 Включение API
1. В левом меню выберите **"APIs & Services"** → **"Library"**
2. Найдите и включите следующие API:
   - **Admin SDK API** ✅ (обязательно)
   - **Google Calendar API** (опционально)
   - **Gmail API** (опционально)

#### 1.3 Настройка OAuth consent screen
1. Перейдите в **"APIs & Services"** → **"OAuth consent screen"**
2. Выберите **"Internal"** (для G Suite) или **"External"**
3. Заполните обязательные поля:
   - **App name**: `Admin Team Tools`
   - **User support email**: ваш email
   - **Developer contact information**: ваш email
4. Нажмите **"Save and Continue"**

#### 1.4 Добавление Scopes
1. На странице **"Scopes"** нажмите **"Add or Remove Scopes"**
2. Добавьте следующие scopes:
   ```
   https://www.googleapis.com/auth/admin.directory.user
   https://www.googleapis.com/auth/admin.directory.group
   https://www.googleapis.com/auth/admin.directory.orgunit
   https://www.googleapis.com/auth/calendar
   ```
3. Нажмите **"Update"** → **"Save and Continue"**

### 2. Создание OAuth 2.0 Credentials

#### 2.1 Создание Client ID
1. Перейдите в **"APIs & Services"** → **"Credentials"**
2. Нажмите **"+ Create Credentials"** → **"OAuth client ID"**
3. Выберите **"Desktop application"**
4. Введите название: `Admin Team Tools Desktop`
5. Нажмите **"Create"**

#### 2.2 Скачивание credentials
1. В списке OAuth 2.0 Client IDs найдите созданный client
2. Нажмите на иконку скачивания (⬇️)
3. Переименуйте скачанный файл в `credentials.json`
4. Поместите файл в корневую папку проекта

### 3. Проверка настройки

#### 3.1 Структура credentials.json
Убедитесь, что файл содержит структуру:
```json
{
  "installed": {
    "client_id": "ваш-client-id.apps.googleusercontent.com",
    "project_id": "ваш-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "ваш-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

#### 3.2 Тест подключения
```bash
# Запустите тест OAuth 2.0
python test_oauth.py
```

## 🔄 Процесс авторизации

### Первый запуск
1. При первом запуске откроется браузер
2. Войдите в Google аккаунт с правами администратора
3. Разрешите доступ к Google Workspace
4. Токен будет автоматически сохранен в `token.pickle`

### Последующие запуски
- Токен автоматически загружается из `token.pickle`
- При истечении токена происходит автоматическое обновление
- Повторная авторизация через браузер не требуется

## 🛡️ Безопасность

### Файлы для .gitignore
```
# OAuth 2.0 секреты
credentials.json
token.pickle
```

### Права доступа
OAuth 2.0 запрашивает только необходимые права:
- **admin.directory.user**: Управление пользователями
- **admin.directory.group**: Управление группами  
- **admin.directory.orgunit**: Управление подразделениями
- **calendar**: Управление календарями (опционально)

## 🐛 Troubleshooting

### Ошибка: "Access blocked"
**Решение**: Убедитесь, что используете аккаунт с правами администратора Google Workspace

### Ошибка: "redirect_uri_mismatch"
**Решение**: Проверьте, что в OAuth client настроены redirect URIs: `http://localhost`

### Ошибка: "insufficient privileges"
**Решение**: Убедитесь, что все необходимые scopes добавлены в OAuth consent screen

### Ошибка: "API not enabled"
**Решение**: Включите Admin SDK API в Google Cloud Console

## 📞 Поддержка

Если возникли проблемы с настройкой OAuth 2.0:
1. Проверьте логи приложения
2. Запустите `python test_oauth.py` для диагностики
3. Убедитесь, что credentials.json имеет правильную структуру
4. Проверьте права администратора в Google Workspace

---

✅ **После успешной настройки OAuth 2.0 вы сможете безопасно управлять Google Workspace через Admin Team Tools!**
