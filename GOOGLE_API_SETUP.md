# Настройка Google Workspace API

## Статус подключения
✅ **Google API успешно интегрирован в приложение!**

Приложение теперь поддерживает работу с реальным Google Workspace API для управления пользователями и группами.

## 🔐 Приоритет OAuth 2.0

### 🥇 OAuth 2.0 (Приоритетный метод)
- **Интерактивная авторизация** через браузер
- **Удобство**: Минимальная настройка и быстрый старт
- **Безопасность**: Credentials хранятся на клиенте
- **Обновление**: Автоматическое обновление токенов
- **[Подробная инструкция по настройке](docs/OAUTH2_PRIORITY_SETUP.md)**

### 🥈 Service Account (Запасной метод)
- Серверная авторизация без взаимодействия с пользователем
- Требует Domain-wide delegation в Google Workspace
- Используется автоматически при отсутствии OAuth 2.0 credentials

## Режимы работы

### Режим разработки 
- Переменная `DEV_MODE=True` в файле `.env`
- Использует демонстрационные данные
- Не требует настоящих учетных данных Google
- Идеально для тестирования и демонстрации

### Производственный режим
Для работы с реальными данными Google Workspace:

## Инструкция по настройке Google API

### 1. Создание проекта в Google Cloud Console
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите следующие API:
   - Admin SDK API
   - Directory API
   - Calendar API (опционально)

### 2. Настройка OAuth 2.0 (приоритетный метод) 🔐

#### Шаг 1: Создание OAuth 2.0 Client ID
1. В Google Cloud Console перейдите в "APIs & Services" > "Credentials"
2. Нажмите "Create Credentials" > "OAuth 2.0 Client ID"
3. Выберите тип приложения: "Desktop Application"
4. Введите название: "Admin Team Tools"
5. Нажмите "Create"
6. Скачайте JSON-файл с учетными данными

#### Шаг 2: Установка учетных данных
1. Переименуйте скачанный файл в `credentials.json`
2. Поместите файл в корень проекта
3. Файл должен содержать структуру с элементом "installed":
   ```json
   {
     "installed": {
       "client_id": "your-client-id",
       "client_secret": "your-client-secret",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       ...
     }
   }
   ```

#### Шаг 3: Настройка разрешений
1. В Google Cloud Console перейдите в "APIs & Services" > "OAuth consent screen"
2. Настройте consent screen для вашего приложения
3. Добавьте следующие scopes:
   - `https://www.googleapis.com/auth/admin.directory.user`
   - `https://www.googleapis.com/auth/admin.directory.group`
   - `https://www.googleapis.com/auth/admin.directory.orgunit`
   - `https://www.googleapis.com/auth/calendar` (опционально)

#### Шаг 4: Тестирование OAuth 2.0
1. Запустите утилиту для проверки OAuth 2.0 подключения:
   ```bash
   python test_oauth.py
   ```
2. При успешной настройке утилита выведет информацию о подключении
3. После успешной авторизации токен сохранится в `token.pickle`

### 3. Альтернатива: Service Account (запасной метод) ⚙️
1. В Google Cloud Console перейдите в "IAM & Admin" > "Service Accounts"
2. Создайте новый Service Account
3. Скачайте JSON-файл с ключами
4. Переименуйте в `credentials.json` и поместите в корень проекта
5. В Google Workspace Admin Console настройте Domain-wide delegation:
   - Перейдите в "Security" > "API controls" > "Domain-wide delegation"
   - Добавьте Client ID вашего Service Account
   - Добавьте следующие scopes:
   ```
   https://www.googleapis.com/auth/admin.directory.user
   https://www.googleapis.com/auth/admin.directory.group
   https://www.googleapis.com/auth/admin.directory.orgunit
   https://www.googleapis.com/auth/calendar
   ```

> ⚠️ **Примечание**: Если в credentials.json присутствуют как OAuth 2.0, так и Service Account данные, приоритет будет отдан OAuth 2.0.

### 4. Настройка приложения
1. Отредактируйте файл `.env`:
   ```env
   # Отключить режим разработки для работы с реальным API
   DEV_MODE=False
   
   # Настроить ваш домен (опционально)
   GOOGLE_WORKSPACE_DOMAIN=yourdomain.com
   GOOGLE_WORKSPACE_ADMIN=admin@yourdomain.com
   ```

2. Убедитесь, что файл `credentials.json` содержит ваши учетные данные
3. При наличии обоих типов учетных данных, OAuth 2.0 будет использоваться как приоритетный

### 5. Первый запуск с OAuth 2.0
1. Запустите приложение: `python main.py`
2. При первом запуске автоматически откроется браузер
3. Войдите в свой Google аккаунт (должен иметь права администратора Google Workspace)
4. Разрешите доступ приложению к запрошенным данным
5. Токен будет автоматически сохранен в файл `token.pickle`
6. При следующих запусках повторная авторизация не потребуется, если токен действителен

### 6. Устранение неполадок OAuth 2.0
- **Ошибка**: "Invalid client" - Проверьте правильность credentials.json
- **Ошибка**: "Access denied" - Убедитесь, что аккаунт имеет права администратора
- **Ошибка**: "Token expired" - Удалите token.pickle для повторной авторизации
- **Ошибка**: "API not enabled" - Включите необходимые API в Google Cloud Console

Подробная инструкция по устранению неполадок: [OAUTH2_PRIORITY_SETUP.md](docs/OAUTH2_PRIORITY_SETUP.md)

#### Браузер не открывается
- Убедитесь что `DEV_MODE=False` в `.env`
- Проверьте что файл `credentials.json` содержит OAuth 2.0 данные (должен быть ключ "installed")

#### Ошибка "access_denied" 
- Убедитесь что ваш Google аккаунт имеет права администратора Google Workspace
- Проверьте что все необходимые API включены в Google Cloud Console

#### Ошибка "invalid_scope"
- Убедитесь что в OAuth consent screen добавлены все необходимые scopes
- Удалите файл `token.pickle` и повторите авторизацию

## 🧪 Быстрый тест OAuth 2.0

После настройки учетных данных вы можете протестировать подключение:

```bash
# Запуск тестовой утилиты
python test_oauth.py
```

Утилита автоматически:
- ✅ Проверит наличие файла credentials.json
- ✅ Запустит процесс авторизации OAuth 2.0
- ✅ Протестирует подключение к API
- ✅ Покажет примеры пользователей и групп

При первом запуске откроется браузер для авторизации.

## 🚀 Запуск с реальным API

1. Настройте учетные данные (см. выше)
2. Измените `.env`: `DEV_MODE=False`
3. Запустите приложение: `python main.py`
4. При первом запуске с OAuth2 откроется браузер для авторизации

## Текущие возможности API

### Пользователи 👤
- ✅ Получение списка пользователей
- ✅ Поиск пользователей
- ✅ Фильтрация по организационным подразделениям
- 🔄 Создание/обновление/удаление (в разработке)

### Группы 👥
- ✅ Получение списка групп
- ✅ Получение информации о группе
- 🔄 Управление участниками (в разработке)
- 🔄 Создание/обновление/удаление (в разработке)

### Подключение 🔌
- ✅ OAuth 2.0 с интерактивной авторизацией (приоритет)
- ✅ Service Account с domain-wide delegation (запасной метод)
- ✅ Автоматическое обновление токенов
- ✅ Переключение на demo-режим при проблемах

### Безопасность 🛡️
- ✅ Защищенное хранение токенов
- ✅ Управление scopes для минимизации привилегий
- ✅ Логирование ошибок авторизации
- ✅ Защита от превышения квот API

## Поддержка

Если возникают проблемы:
1. Проверьте логи в папке `logs/`
2. Убедитесь что все API включены в Google Cloud Console
3. Проверьте права доступа Service Account или OAuth2 клиента
4. В случае проблем приложение автоматически переключится в demo-режим

---
**Примечание**: В текущем состоянии приложение полностью функционально и готово к работе как в demo-режиме, так и с реальным Google Workspace API.
