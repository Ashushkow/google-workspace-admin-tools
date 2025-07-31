# 🔧 Пошаговая инструкция: Исправление Gmail API

## 📊 Результат детальной диагностики

✅ **Gmail scope добавлен** в конфигурацию приложения  
✅ **OAuth токен содержит** Gmail scope  
❌ **Gmail scope НЕ ДОБАВЛЕН в OAuth Consent Screen** в Google Cloud Console

## 🎯 Точная причина проблемы

Хотя Gmail scope присутствует в токене, Google возвращает ошибку "insufficient authentication scopes", потому что **Gmail scope не был добавлен в OAuth Consent Screen** в Google Cloud Console.

## 🛠️ КРИТИЧЕСКИ ВАЖНЫЕ шаги

### Шаг 1: ОБЯЗАТЕЛЬНО добавьте Gmail scope в OAuth Consent Screen
1. Перейдите на [console.cloud.google.com](https://console.cloud.google.com/)
2. Выберите ваш проект (где настроены OAuth credentials)
3. Перейдите в **"APIs & Services" → "OAuth consent screen"**
4. Нажмите **"EDIT APP"**
5. Перейдите к шагу **"Scopes"** (это КРИТИЧЕСКИ ВАЖНО!)
6. Нажмите **"ADD OR REMOVE SCOPES"**
7. В поиске найдите **"Gmail API"**
8. **ОБЯЗАТЕЛЬНО** отметьте: **"Send email on your behalf"**
   - Scope: `https://www.googleapis.com/auth/gmail.send`
9. Нажмите **"UPDATE"**
10. **Завершите настройку до конца** и сохраните

### Шаг 2: Включите Gmail API (если ещё не включен)
1. В том же проекте: **"APIs & Services" → "Library"**
2. Найдите **"Gmail API"**
3. Убедитесь, что он **"ENABLED"**

### Шаг 3: ПЕРЕСОЗДАЙТЕ токен авторизации
```bash
rm token.pickle
python main.py  # Повторная авторизация с правильными scopes
```

### Шаг 4: Проверьте результат
```bash
python setup_gmail_api.py
```

Ожидаемый результат:
```
✅ Учетные данные
✅ Gmail scopes  
✅ Токен авторизации
✅ Google API
✅ Gmail функциональность

🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!
```

## � Если проблема ВСЁЁ ещё остается

### Проверьте OAuth Consent Screen статус
```bash
python debug_gmail_scope.py
```

### Убедитесь, что Gmail scope точно добавлен:
1. В Google Cloud Console откройте **OAuth consent screen**
2. На шаге **"Scopes"** должен быть виден:
   ```
   ../auth/gmail.send
   Send email on your behalf
   ```
3. Если его НЕТ - добавьте заново!

### Альтернативный способ проверки:
1. Создайте **НОВЫЙ** OAuth Client ID
2. При создании сразу добавьте все scopes
3. Скачайте новый credentials.json
4. Удалите token.pickle
5. Запустите приложение

## ⚠️ ВОЗМОЖНЫЕ ДОПОЛНИТЕЛЬНЫЕ ПРОБЛЕМЫ

### Проблема 1: Приложение не верифицировано
Если OAuth consent screen показывает "This app isn't verified":
1. Нажмите **"Advanced"**
2. Нажмите **"Go to [App Name] (unsafe)"**
3. Разрешите доступ

### Проблема 2: Gmail API заблокирован для домена
Проверьте в Google Workspace Admin Console:
1. **Security → API controls → App access control**
2. Убедитесь, что Gmail API не заблокирован

### Проблема 3: Аккаунт не имеет прав
Убедитесь, что ваш аккаунт:
- Супер-администратор Google Workspace
- Имеет права на отправку писем

## 📧 Тестирование после настройки

1. **Запустите приложение:**
   ```bash
   python main.py
   ```

2. **Создайте тестового пользователя:**
   - Нажмите "Создать пользователя"
   - Заполните данные
   - ✅ Отметьте "Отправить приветственное письмо"
   - Нажмите "Создать"

3. **Проверьте результат:**
   - Пользователь должен быть создан
   - Письмо должно быть отправлено
   - Проверьте почту получателя

## 🎯 Ключевые моменты

- **Gmail scope уже настроен** в приложении ✅
- **Нужно только включить Gmail API** в Google Cloud Console ⚙️
- **После включения API** всё будет работать автоматически 🚀

## 📞 Если нужна помощь

1. Документация: `docs/GMAIL_API_SETUP.md`
2. Диагностика: `python check_gmail_scope.py`
3. Проверка: `python setup_gmail_api.py`
