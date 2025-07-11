# 🔧 Настройка Google Workspace API

Данное руководство поможет вам настроить доступ к Google Workspace API для работы с Admin Team Tools.

## 📋 Предварительные требования

- **Google Workspace** (ранее G Suite) аккаунт с правами администратора
- Доступ к **Google Cloud Console**
- **Super Admin** права в Google Workspace

## 🚀 Пошаговая настройка

### 1. Создание проекта в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Нажмите **"Создать проект"** или выберите существующий
3. Введите название проекта (например, "Admin Team Tools")
4. Выберите организацию (если применимо)
5. Нажмите **"Создать"**

### 2. Включение необходимых API

1. В боковом меню выберите **"API и сервисы" → "Библиотека"**
2. Найдите и включите следующие API:

#### Admin SDK API
- Поиск: "Admin SDK API"
- Нажмите **"Включить"**

#### Google Calendar API
- Поиск: "Google Calendar API" 
- Нажмите **"Включить"**

### 3. Создание учетных данных

#### Способ 1: Service Account (Рекомендуется)

1. Перейдите в **"API и сервисы" → "Учетные данные"**
2. Нажмите **"+ СОЗДАТЬ УЧЕТНЫЕ ДАННЫЕ" → "Аккаунт службы"**
3. Заполните данные:
   - **Название**: Admin Team Tools Service
   - **Описание**: Service account for Admin Team Tools
4. Нажмите **"Создать и продолжить"**
5. Пропустите настройку ролей (нажмите **"Продолжить"**)
6. Пропустите доступ пользователей (нажмите **"Готово"**)

#### Настройка Service Account

1. Найдите созданный Service Account в списке
2. Нажмите на его email для редактирования
3. Перейдите на вкладку **"Ключи"**
4. Нажмите **"Добавить ключ" → "Создать новый ключ"**
5. Выберите тип **JSON**
6. Нажмите **"Создать"**
7. Сохраните скачанный файл как `credentials.json` в корне проекта

### 4. Настройка Domain-wide Delegation

1. В настройках Service Account найдите **"Уникальный идентификатор"** (Client ID)
2. Перейдите в [Google Admin Console](https://admin.google.com/)
3. Выберите **"Безопасность" → "Доступ и контроль данных" → "Управление API"**
4. Нажмите **"Добавить новый"**
5. Заполните:
   - **Client ID**: скопируйте из Service Account
   - **OAuth Scopes**: 
     ```
     https://www.googleapis.com/auth/admin.directory.user,
     https://www.googleapis.com/auth/admin.directory.group,
     https://www.googleapis.com/auth/calendar
     ```
6. Нажмите **"Авторизовать"**

### 5. Обновление credentials.json

Добавьте в файл `credentials.json` информацию о домене:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "...",
  "token_uri": "...",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "...",
  "subject": "admin@yourdomain.com"
}
```

⚠️ **Важно**: Замените `admin@yourdomain.com` на реальный email Super Admin вашего домена.

## 🔐 Безопасность

### Важные правила

- 🚨 **Никогда не публикуйте** `credentials.json` в открытом доступе
- 🔒 **Ограничьте доступ** к файлу учетных данных (chmod 600)
- 🛡️ **Регулярно ротируйте** ключи Service Account
- 📋 **Используйте принцип минимальных привилегий**

### Переменные окружения (Альтернатива)

Для production используйте переменные окружения:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
export GOOGLE_WORKSPACE_DOMAIN="yourdomain.com"
export GOOGLE_WORKSPACE_ADMIN="admin@yourdomain.com"
```

## ✅ Проверка настройки

Запустите Admin Team Tools:

```bash
python main.py
```

Если все настроено правильно:
- ✅ Приложение запустится без ошибок
- ✅ В статусной строке будет "Подключен к Google Workspace API"
- ✅ Статистика пользователей и групп загрузится

## 🐛 Устранение неполадок

### Ошибка: "insufficient authentication scopes"

**Решение**: Проверьте OAuth Scopes в Google Admin Console

### Ошибка: "Not Authorized to access this resource/api"

**Решение**: 
1. Убедитесь, что Domain-wide Delegation настроен
2. Проверьте права Super Admin

### Ошибка: "The caller does not have permission"

**Решение**: 
1. Проверьте поле `subject` в credentials.json
2. Убедитесь, что указанный пользователь - Super Admin

### Ошибка: "API not enabled"

**Решение**: Включите Admin SDK API и Calendar API в Google Cloud Console

## 📞 Получение помощи

Если у вас возникли проблемы:

1. Проверьте [FAQ](FAQ.md)
2. Создайте [Issue](https://github.com/Ashushkow/admin-team-tools/issues)
3. Обратитесь в [Discussions](https://github.com/Ashushkow/admin-team-tools/discussions)
