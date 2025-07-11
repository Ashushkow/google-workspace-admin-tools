# 🔧 Настройка Service Account для Admin Team Tools

## ⚠️ ВАЖНО: Дополнительная настройка для Service Account

У вас есть Service Account credentials, но для работы с Google Workspace Admin API нужна дополнительная настройка **Domain-wide delegation**.

## 🚀 Пошаговая настройка Domain-wide delegation

### Шаг 1: Включить Domain-wide delegation

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Выберите ваш проект **admin-project-464720**
3. **IAM и администрирование** → **Аккаунты служб**
4. Найдите аккаунт: `admin-team-tools-service@admin-project-464720.iam.gserviceaccount.com`
5. Нажмите на email аккаунта для редактирования
6. Перейдите на вкладку **"Подробности"**
7. В разделе **"Domain-wide delegation"** нажмите **"Включить делегирование в рамках домена"**
8. Нажмите **"Сохранить"**

### Шаг 2: Настроить Admin Console

1. Перейдите в [Google Admin Console](https://admin.google.com/)
2. **Безопасность** → **Управление доступом и данными** → **Элементы управления API**
3. Нажмите **"Управление делегированием в рамках домена"**
4. Нажмите **"Добавить новое"**
5. В поле **"Идентификатор клиента"** введите: `105177552235888602990`
6. В поле **"Области OAuth"** введите:
   ```
   https://www.googleapis.com/auth/admin.directory.user,
   https://www.googleapis.com/auth/admin.directory.group,
   https://www.googleapis.com/auth/admin.directory.orgunit,
   https://www.googleapis.com/auth/calendar
   ```
7. Нажмите **"Авторизовать"**

### Шаг 3: Настроить DOMAIN_ADMIN_EMAIL

1. Откройте файл `src/config.py`
2. Найдите строку:
   ```python
   DOMAIN_ADMIN_EMAIL = 'admin@yourdomain.com'
   ```
3. Замените `admin@yourdomain.com` на email администратора вашего Google Workspace домена
4. Сохраните файл

**Пример:**
```python
DOMAIN_ADMIN_EMAIL = 'admin@mycompany.com'  # Ваш админский email
```

## 🔍 Проверка настройки

После выполнения всех шагов, запустите проверку:

```bash
python check_setup.py
```

Затем попробуйте запустить приложение:

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
