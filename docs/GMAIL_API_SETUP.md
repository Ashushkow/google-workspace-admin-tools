# 📧 Настройка Gmail API для отправки приветственных писем

## Обзор
Admin Team Tools теперь поддерживает автоматическую отправку приветственных писем новым пользователям Google Workspace через Gmail API.

## 🎯 Возможности
- ✅ Автоматическая отправка приветственных писем при создании пользователей
- ✅ Красиво оформленные HTML письма с корпоративным дизайном
- ✅ Текстовая версия письма для совместимости
- ✅ Информация о доступных сервисах Google Workspace
- ✅ Инструкции по безопасности и первому входу
- ✅ Возможность отключения отправки писем при создании пользователя

## 🔧 Настройка

### 1. Включение Gmail API

#### В Google Cloud Console:
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Выберите ваш проект
3. Перейдите в **"APIs & Services" → "Library"**
4. Найдите **"Gmail API"**
5. Нажмите **"Enable"**

### 2. Обновление OAuth 2.0 scopes

Gmail scope уже добавлен в конфигурацию:
```
https://www.googleapis.com/auth/gmail.send
```

#### Обновление токена:
1. Удалите файл `token.pickle` (если существует)
2. Запустите приложение - откроется браузер для повторной авторизации
3. Разрешите доступ к Gmail при авторизации

### 3. Настройка OAuth Consent Screen

В Google Cloud Console перейдите в **"APIs & Services" → "OAuth consent screen"**:

#### Добавьте scopes:
- `https://www.googleapis.com/auth/admin.directory.user`
- `https://www.googleapis.com/auth/admin.directory.group`
- `https://www.googleapis.com/auth/admin.directory.group.member`
- `https://www.googleapis.com/auth/admin.directory.orgunit`
- `https://www.googleapis.com/auth/admin.directory.domain.readonly`
- `https://www.googleapis.com/auth/calendar`
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/gmail.send` ← **Новый scope**

### 4. Тестирование

Запустите тестирование Gmail API:
```bash
python test_gmail_api.py
```

Ожидаемый результат:
```
✅ Gmail scope найден
✅ Google API клиент инициализирован  
✅ Gmail API сервис доступен
✅ Gmail сервис создан
✅ Доступ к Gmail API подтвержден
✅ Тестовое сообщение создано успешно
🎉 Все тесты Gmail API пройдены успешно!
```

## 📧 Как это работает

### При создании пользователя:
1. Пользователь создается в Google Workspace
2. Автоматически формируется приветственное письмо
3. Письмо отправляется с email администратора на email нового пользователя
4. Письмо содержит:
   - Данные для входа (email и временный пароль)
   - Список доступных сервисов
   - Инструкции по безопасности
   - Ссылки для входа

### Шаблон письма включает:
- 🎉 Приветствие
- 🔐 Данные для входа
- 📋 Список доступных сервисов (Gmail, Drive, Docs, Calendar, Meet)
- ⚠️ Напоминание о смене пароля
- 🛡️ Рекомендации по безопасности
- 📱 Информация о мобильных приложениях

## ⚙️ Настройки

### В интерфейсе создания пользователей:
- ✅ По умолчанию включена отправка приветственного письма
- 📧 Можно отключить через checkbox "Отправить приветственное письмо"

### В коде:
```python
# Создание пользователя с письмом
from src.api.user_creation_service import create_user_with_welcome_email

result = create_user_with_welcome_email(
    service=service,
    gmail_credentials=credentials,
    email="new.user@domain.com",
    first_name="Новый",
    last_name="Пользователь", 
    password="TempPass123!",
    admin_email="admin@domain.com",
    send_welcome_email=True
)
```

## 🔒 Безопасность

### Требования:
- Gmail API должен быть авторизован администратором домена
- Письма отправляются от имени администратора
- Используется OAuth 2.0 для безопасной авторизации
- Временные пароли передаются только по защищенному каналу

### Рекомендации:
- Убедитесь, что OAuth consent screen настроен корректно
- Используйте сложные временные пароли
- Настройте требование смены пароля при первом входе

## 🐛 Устранение неполадок

### Ошибка "Gmail API не инициализирован":
1. Проверьте, что Gmail API включен в Google Cloud Console
2. Убедитесь, что scope `gmail.send` добавлен в OAuth consent screen
3. Удалите `token.pickle` и повторите авторизацию

### Ошибка "Insufficient permissions":
1. Убедитесь, что аккаунт имеет права администратора Google Workspace
2. Проверьте настройки OAuth consent screen
3. Убедитесь, что все необходимые scopes авторизованы

### Письма не отправляются:
1. Запустите `python test_gmail_api.py` для диагностики
2. Проверьте логи приложения на наличие ошибок
3. Убедитесь, что email администратора корректно настроен в конфигурации

### Письма попадают в спам:
1. Настройте SPF записи для вашего домена
2. Включите DKIM в Google Workspace
3. Убедитесь, что отправитель авторизован в домене

## 📋 Конфигурация

В файле `src/config/enhanced_config.py`:
```python
class GoogleAPIConfig:
    scopes: list = [
        # ... другие scopes ...
        'https://www.googleapis.com/auth/gmail.send'  # Для отправки писем
    ]
```

## 🚀 Дополнительные возможности

### Планируется:
- 📋 Настраиваемые шаблоны писем
- 🌐 Многоязычная поддержка
- 📊 Статистика отправленных писем
- 🔄 Повторная отправка писем
- 📎 Прикрепление файлов-инструкций

## 📞 Поддержка

При возникновении проблем:
1. Запустите диагностику: `python test_gmail_api.py`
2. Проверьте логи приложения
3. Убедитесь в корректности настройки Google Cloud Console
4. Проверьте права доступа в Google Workspace Admin Console
