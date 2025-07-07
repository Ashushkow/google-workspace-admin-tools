# 🔐 Настройка конфиденциальных файлов

## Обязательная настройка перед запуском

### 1. Создание credentials.json

1. **Скопируйте template файл:**
   ```powershell
   copy credentials.json.template credentials.json
   ```

2. **Получите Google API credentials:**
   - Зайдите в [Google Cloud Console](https://console.cloud.google.com/)
   - Создайте новый проект или выберите существующий
   - Включите **Admin SDK Directory API**
   - Перейдите в **APIs & Services > Credentials**
   - Создайте **OAuth 2.0 Client ID** для Desktop Application
   - Скачайте JSON файл с credentials

3. **Замените содержимое credentials.json** скачанными данными

### 2. Создание settings.json

1. **Скопируйте template файл:**
   ```powershell
   copy settings.json.template settings.json
   ```

2. **Настройте параметры:**
   - `domain` - ваш Google Workspace домен
   - `admin_email` - email администратора
   - Остальные параметры по необходимости

### 3. Структура файлов

После настройки у вас должны быть:
- ✅ `credentials.json` - Google API credentials (НЕ в Git)
- ✅ `settings.json` - настройки приложения (НЕ в Git)
- ✅ `credentials.json.template` - template для credentials (в Git)
- ✅ `settings.json.template` - template для settings (в Git)

## ⚠️ Безопасность

**ВАЖНО:** Файлы `credentials.json` и `settings.json` содержат конфиденциальную информацию и НЕ должны попадать в Git репозиторий.

Эти файлы автоматически исключены в `.gitignore`:
```
credentials.json
settings.json
token.pickle
admin_log.json
```

## 🔧 Проверка настройки

После создания файлов запустите приложение:
```powershell
python main.py
```

При первом запуске:
1. Откроется браузер для авторизации Google
2. Войдите под аккаунтом администратора Google Workspace
3. Разрешите приложению доступ к Admin SDK
4. Токен сохранится в `token.pickle`

## ❌ Troubleshooting

### Ошибка: "credentials.json не найден"
```powershell
copy credentials.json.template credentials.json
# Затем отредактируйте credentials.json с вашими данными
```

### Ошибка: "settings.json не найден"
```powershell
copy settings.json.template settings.json
# Затем отредактируйте settings.json с вашими параметрами
```

### Ошибка авторизации
- Проверьте правильность client_id и client_secret в credentials.json
- Убедитесь, что Admin SDK API включен в Google Cloud Console
- Проверьте права доступа администратора Google Workspace
