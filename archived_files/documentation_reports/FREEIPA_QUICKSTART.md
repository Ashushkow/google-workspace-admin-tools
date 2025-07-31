# 🚀 FreeIPA Quick Start Guide

## Быстрый старт с FreeIPA интеграцией

Это руководство поможет вам начать работу с FreeIPA интеграцией в Admin Team Tools всего за несколько минут.

---

## 📋 Предварительные требования

### Установка зависимостей

```powershell
pip install -r requirements.txt
```

---

## 🎯 Пошаговое руководство (GUI)

### Шаг 1: Запуск приложения
```powershell
python main.py
```

### Шаг 2: Открытие FreeIPA интеграции
1. В главном окне нажмите кнопку **"🔗 FreeIPA"** в панели инструментов
2. Или используйте меню: **FreeIPA → Управление интеграцией**
3. Или горячие клавиши: **Ctrl+F**

### Шаг 3: Настройка подключения
В открывшемся окне перейдите на вкладку **"Подключение"**:

1. **Сервер**: `https://ipa.example.com`
2. **Пользователь**: `admin` (или ваш пользователь)
3. **Пароль**: ваш пароль
4. **Домен**: `EXAMPLE.COM` (необязательно для Kerberos)
5. **Проверить SSL**: отключить если используется самоподписанный сертификат

Нажмите **"Подключиться"**

### Шаг 4: Управление группами
Перейдите на вкладку **"Управление группами"**:

1. **Создать группу**: введите название и описание новой группы
2. **Получить группы Google**: загружает список групп из Google Workspace
3. **Получить группы FreeIPA**: загружает список групп из FreeIPA
4. **Синхронизировать группы**: создает отсутствующие группы в FreeIPA

### Шаг 5: Сравнение групп
В той же вкладке **"Управление группами"**:

1. **Сравнить группы**: показывает различия между Google Workspace и FreeIPA
2. **Анализ результатов**: просмотр групп, которые есть только в одной системе
3. **Выборочная синхронизация**: создание отдельных групп по необходимости

⚠️ **Важно**: Синхронизация пользователей отключена. Этот модуль работает только с группами.

---

## 📊 Мониторинг

### Вкладка "Статистика"
Отображает:
- � Количество групп в Google Workspace и FreeIPA
-  Последняя синхронизация групп
- ❌ Ошибки подключения
- ⚠️ Информация о пользователях не отображается (функция отключена)

---

## 🛠️ Настройки

### Вкладка "Настройки"
- **Автосинхронизация**: включить периодическую синхронизацию
- **Интервал синхронизации**: настроить частоту (по умолчанию 1 час)
- **Логирование**: уровень детализации логов
- **Уведомления**: настройка оповещений об ошибках

---

## 📚 CLI Команды (альтернативный способ)

## Настройка FreeIPA

### 1. Создание конфигурации

```powershell
python main.py freeipa create-config
```

### 2. Редактирование конфигурации

Отредактируйте файл `config/freeipa_config.json`:

```json
{
  "server_url": "https://ipa.yourdomain.com",
  "domain": "yourdomain.com", 
  "username": "admin",
  "password": "your_password",
  "use_kerberos": false,
  "verify_ssl": true,
  "timeout": 30
}
```

### 3. Тестирование подключения

```powershell
python main.py freeipa test-connection
```

## Основные команды

### Статистика
```powershell
python main.py freeipa stats
```

### Синхронизация пользователей
```powershell
# Один пользователь
python main.py freeipa sync-user user@example.com --groups employees developers

# Все пользователи домена
python main.py freeipa sync-all-users --domain example.com --groups employees
```

### Управление группами
```powershell
# Создание группы
python main.py freeipa create-group developers --description "Команда разработки"

# Синхронизация групп из Google Workspace
python main.py freeipa sync-groups --domain example.com
```

### Добавление в группы
```powershell
python main.py freeipa add-user-to-group user@example.com developers
```

### Сравнение данных
```powershell
python main.py freeipa compare-users --domain example.com
```

## Тестирование интеграции

Запустите полное тестирование:

```powershell
python test_freeipa_integration.py
```

## Документация

Полная документация: [docs/FREEIPA_INTEGRATION_GUIDE.md](docs/FREEIPA_INTEGRATION_GUIDE.md)

## Поддержка

При возникновении проблем:

1. Проверьте логи в `logs/admin_tools.log`
2. Используйте флаг `--verbose` для подробного вывода
3. Убедитесь, что FreeIPA сервер доступен
4. Проверьте права пользователя в FreeIPA
