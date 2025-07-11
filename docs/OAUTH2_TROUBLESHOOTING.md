# Устранение неполадок OAuth 2.0

Это руководство поможет решить распространенные проблемы при настройке и использовании OAuth 2.0 для подключения к Google Workspace API.

## 🔍 Диагностика проблем

### Быстрая проверка
Запустите утилиту тестирования OAuth 2.0:
```bash
python test_oauth.py
```

### Проверка файлов
1. `credentials.json` - файл с OAuth 2.0 учетными данными
2. `token.pickle` - файл с токеном доступа
3. `.env` - файл с настройками окружения

## 🚫 Распространенные ошибки

### 1. Invalid Client
```
Error: invalid_client
```
#### Причины:
- Неверный формат credentials.json
- Повреждённый файл credentials.json
- Неправильный тип OAuth 2.0 клиента

#### Решение:
1. Проверьте что credentials.json содержит правильную структуру:
   ```json
   {
     "installed": {
       "client_id": "...",
       "client_secret": "...",
       "redirect_uris": ["http://localhost"]
     }
   }
   ```
2. Скачайте credentials.json заново из Google Cloud Console
3. Убедитесь, что создали OAuth 2.0 клиент типа "Desktop Application"

### 2. Access Denied
```
Error: access_denied
```
#### Причины:
- Недостаточно прав у Google аккаунта
- Не включены необходимые API
- Не настроен OAuth consent screen

#### Решение:
1. Убедитесь, что используете аккаунт администратора Google Workspace
2. Включите необходимые API в Google Cloud Console:
   - Admin SDK API
   - Directory API
3. Настройте OAuth consent screen:
   - Добавьте все необходимые scopes
   - Заполните обязательные поля

### 3. Token Expired
```
Error: token_expired
```
#### Решение:
1. Удалите файл token.pickle
2. Запустите приложение снова для новой авторизации
3. Проверьте системное время компьютера

### 4. Invalid Scope
```
Error: invalid_scope
```
#### Решение:
1. Проверьте настройки OAuth consent screen
2. Убедитесь, что добавлены все необходимые scopes:
   ```
   https://www.googleapis.com/auth/admin.directory.user
   https://www.googleapis.com/auth/admin.directory.group
   https://www.googleapis.com/auth/admin.directory.orgunit
   ```

### 5. API Not Enabled
```
Error: API not enabled
```
#### Решение:
1. Перейдите в Google Cloud Console
2. Выберите ваш проект
3. Включите необходимые API в разделе "APIs & Services"

## 🌐 Проблемы с браузером

### Браузер не открывается
#### Причины:
- Системные ограничения
- Проблемы с правами доступа

#### Решение:
1. Запустите приложение с правами администратора
2. Проверьте настройки брандмауэра
3. Попробуйте использовать другой браузер по умолчанию

### Ошибка localhost
#### Решение:
1. Проверьте что в credentials.json указан redirect_uri: "http://localhost"
2. Убедитесь, что порт 8080 свободен
3. Проверьте файл hosts

## 🔒 Проблемы с токеном

### Токен не сохраняется
#### Решение:
1. Проверьте права на запись в директорию
2. Убедитесь, что нет конфликтов с антивирусом
3. Попробуйте запустить с правами администратора

### Токен постоянно инвалидируется
#### Решение:
1. Проверьте системное время
2. Убедитесь, что scopes не изменились
3. Проверьте ограничения в Google Workspace

## ⚙️ Проблемы с настройками

### DEV_MODE не отключается
#### Решение:
1. Проверьте файл .env:
   ```env
   DEV_MODE=False
   ```
2. Перезапустите приложение
3. Удалите кэш Python

### Не применяются настройки домена
#### Решение:
1. Проверьте формат в .env:
   ```env
   GOOGLE_WORKSPACE_DOMAIN=yourdomain.com
   GOOGLE_WORKSPACE_ADMIN=admin@yourdomain.com
   ```
2. Перезапустите приложение

## 📞 Дополнительная помощь

Если проблема не решена:
1. Проверьте логи в папке logs/
2. Запустите с повышенным уровнем логирования:
   ```env
   APP_LOG_LEVEL=DEBUG
   ```
3. Обратитесь к [полной документации](OAUTH2_PRIORITY_SETUP.md)
