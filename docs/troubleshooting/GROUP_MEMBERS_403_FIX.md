# 🔧 ИСПРАВЛЕНИЕ ОШИБКИ 403 - Добавление пользователей в группы

## 🎯 Проблема
При добавлении пользователя в группу появлялась ошибка:
```
HttpError 403 when requesting https://admin.googleapis.com/admin/directory/v1/groups/testdecember2023%40sputnik8.com/members?alt=json returned "Not Authorized to access this resource/api"
```

## ✅ Решение
Проблема заключалась в отсутствии необходимого OAuth 2.0 scope для управления участниками групп.

### Что было исправлено:
1. **Добавлен недостающий scope**: `https://www.googleapis.com/auth/admin.directory.group.member`
2. **Обновлена конфигурация** в файле `src/config/enhanced_config.py`
3. **Удален старый токен** авторизации для принудительной повторной авторизации

### Обновленный список scopes:
```
✅ https://www.googleapis.com/auth/admin.directory.user
✅ https://www.googleapis.com/auth/admin.directory.group
✅ https://www.googleapis.com/auth/admin.directory.group.member  ← ДОБАВЛЕН
✅ https://www.googleapis.com/auth/admin.directory.orgunit
✅ https://www.googleapis.com/auth/admin.directory.domain.readonly
✅ https://www.googleapis.com/auth/calendar
✅ https://www.googleapis.com/auth/drive
```

## 🚀 Что нужно сделать сейчас

### 1. Запустите приложение для повторной авторизации:
```bash
python main.py
```

### 2. При первом запуске:
- 🌐 Откроется браузер с запросом на авторизацию
- 🔐 Войдите под аккаунтом администратора Google Workspace
- ✅ **ВАЖНО**: Разрешите доступ ко всем запрашиваемым разрешениям
- 🎯 Особенно важно разрешить доступ к "Управление группами и их участниками"

### 3. После успешной авторизации:
- ✅ Новый токен будет сохранен в `token.pickle`
- ✅ Приложение запустится с полными правами
- ✅ Добавление пользователей в группы будет работать корректно

## 🧪 Проверка исправления

После повторной авторизации попробуйте снова добавить пользователя в группу:
1. Откройте управление группами
2. Выберите группу 
3. Попробуйте добавить пользователя
4. Ошибка 403 больше не должна появляться

## 📋 Что делать, если проблема осталась:

### Проверка 1: OAuth Consent Screen
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services → OAuth consent screen
3. Убедитесь, что добавлены все необходимые scopes

### Проверка 2: Права пользователя
1. Убедитесь, что используете аккаунт администратора Google Workspace
2. У пользователя должны быть права Super Admin или Group Admin

### Проверка 3: API включены
1. В Google Cloud Console: APIs & Services → Enabled APIs
2. Убедитесь, что включен **Admin SDK API**

## 🎉 Результат
После исправления:
- ✅ Пользователи смогут быть добавлены в группы без ошибок
- ✅ Приложение будет отображать корректные сообщения об успехе
- ✅ Все операции с группами будут работать стабильно

---
**Дата исправления:** 18 июля 2025  
**Статус:** ✅ ИСПРАВЛЕНО - требуется повторная авторизация
