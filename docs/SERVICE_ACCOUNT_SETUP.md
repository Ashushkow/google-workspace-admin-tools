# 🔧 Настройка Service Account для Admin Team Tools

## 🎯 Ваша конфигурация
- **Domain**: `sputnik8.com`
- **Admin Email**: `andrei.shushkov@sputnik8.com`
- **Service Account**: `admin-team-tools-service@admin-project-464720.iam.gserviceaccount.com`
- **Client ID**: `117649742513308469203`

## ⚠️ ВАЖНО: Текущая проблема

Приложение показывает ошибку `unauthorized_client`, потому что нужно настроить **Domain-wide delegation**.

## 🚀 Пошаговое решение

### Шаг 1: Откройте Google Workspace Admin Console

1. Перейдите по ссылке: https://admin.google.com
2. Войдите под учетной записью: `andrei.shushkov@sputnik8.com`

### Шаг 2: Найдите Domain-wide delegation

1. В боковом меню выберите **Security** (Безопасность)
2. Нажмите на **API Controls** (Управление API)
3. Выберите **Domain-wide delegation** (Делегирование на уровне домена)

### Шаг 3: Добавьте новое делегирование

1. Нажмите **Add new** (Добавить новый) или **Manage Domain Wide Delegation**
2. **Заполните форму:**

**Client ID:** (скопируйте точно)
```
117649742513308469203
```

**OAuth scopes:** (скопируйте всю строку)
```
https://www.googleapis.com/auth/admin.directory.user,https://www.googleapis.com/auth/admin.directory.group,https://www.googleapis.com/auth/admin.directory.orgunit,https://www.googleapis.com/auth/calendar
```

3. Нажмите **Authorize** (Авторизовать)

### Шаг 4: Проверьте результат

После настройки (обычно 5-10 минут) запустите:
```bash
python main.py
```

## 📋 Что должно быть настроено:

- ✅ Service Account создан
- ✅ credentials.json файл скачан  
- ⚠️ Domain-wide delegation включен
- ⚠️ OAuth scopes авторизованы в Admin Console
- ⚠️ DOMAIN_ADMIN_EMAIL настроен

## 🆘 Возможные проблемы:

### Ошибка "insufficient permissions"
- Проверьте, что Domain-wide delegation включен
- Убедитесь, что все scopes добавлены в Admin Console
- Проверьте, что DOMAIN_ADMIN_EMAIL указан правильно

### Ошибка "invalid_grant"
- Убедитесь, что Service Account имеет права Admin API
- Проверьте, что используется правильный Client ID

### Ошибка "access_denied"
- Убедитесь, что ваш аккаунт имеет Super Admin права
- Проверьте настройки безопасности в Admin Console

---

**После выполнения всех шагов приложение должно работать с Service Account!** 🎉
