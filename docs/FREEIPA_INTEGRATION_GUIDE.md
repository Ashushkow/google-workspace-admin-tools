# Интеграция с FreeIPA

Данное руководство описывает интеграцию Admin Team Tools с FreeIPA для управления пользователями и группами.

## Обзор

FreeIPA - это система управления идентификацией и безопасностью с открытым исходным кодом. Интеграция позволяет:

- ✅ Синхронизировать пользователей из Google Workspace в FreeIPA
- ✅ Создавать и управлять группами в FreeIPA
- ✅ Назначать пользователей в группы
- ✅ Сравнивать данные между системами
- ✅ Массовые операции синхронизации

## Установка зависимостей

```bash
pip install python-freeipa requests-kerberos
```

## Настройка

### 1. Создание конфигурации

Создайте файл конфигурации FreeIPA:

```bash
python -m src.services.freeipa_client create-config
```

Или используйте CLI:

```bash
python main.py freeipa create-config
```

### 2. Настройка параметров

Отредактируйте файл `config/freeipa_config.json`:

```json
{
  "server_url": "https://ipa.yourdomain.com",
  "domain": "yourdomain.com",
  "username": "admin",
  "password": "your_password_here",
  "use_kerberos": false,
  "verify_ssl": true,
  "ca_cert_path": null,
  "timeout": 30
}
```

#### Параметры конфигурации:

- `server_url` - URL FreeIPA сервера
- `domain` - Домен FreeIPA
- `username` - Имя пользователя для подключения
- `password` - Пароль пользователя
- `use_kerberos` - Использовать Kerberos аутентификацию
- `verify_ssl` - Проверять SSL сертификаты
- `ca_cert_path` - Путь к CA сертификату (опционально)
- `timeout` - Таймаут подключения в секундах

### 3. Тестирование подключения

```bash
python main.py freeipa test-connection
```

## Использование

### CLI команды

#### Статистика FreeIPA

```bash
python main.py freeipa stats
```

#### Синхронизация пользователей

Синхронизация одного пользователя:

```bash
python main.py freeipa sync-user user@example.com --groups developers admins
```

Массовая синхронизация всех пользователей:

```bash
python main.py freeipa sync-all-users --domain example.com --groups employees
```

#### Управление группами

Создание группы:

```bash
python main.py freeipa create-group developers --description "Команда разработчиков"
```

Синхронизация групп из Google Workspace:

```bash
python main.py freeipa sync-groups --domain example.com
```

#### Управление членством

Добавление пользователя в группу:

```bash
python main.py freeipa add-user-to-group user@example.com developers
```

#### Сравнение данных

```bash
python main.py freeipa compare-users --domain example.com
```

### Программный интерфейс

```python
from src.integrations import FreeIPAIntegration, setup_freeipa_integration
from src.services.user_service import UserService
from src.services.group_service import GroupService
from src.core.di_container import container

# Получение сервисов
user_service = container.resolve(UserService)
group_service = container.resolve(GroupService)

# Настройка интеграции
integration = await setup_freeipa_integration(
    user_service, 
    group_service,
    config_path="config/freeipa_config.json"
)

if integration:
    # Синхронизация пользователя
    await integration.sync_user_to_freeipa(
        "user@example.com", 
        groups=["developers", "employees"]
    )
    
    # Создание группы
    await integration.create_freeipa_group(
        "new-team", 
        "Новая команда"
    )
    
    # Получение статистики
    stats = await integration.get_freeipa_stats()
    print(f"Пользователей: {stats['users_count']}")
    print(f"Групп: {stats['groups_count']}")
    
    await integration.disconnect()
```

### Context Manager

```python
async with FreeIPAIntegration(user_service, group_service) as integration:
    if integration.load_config():
        # Выполнение операций
        await integration.sync_user_to_freeipa("user@example.com")
        # Автоматическое отключение при выходе
```

## Примеры использования

### Полная синхронизация организации

```bash
# 1. Проверка подключения
python main.py freeipa test-connection

# 2. Просмотр статистики
python main.py freeipa stats

# 3. Сравнение пользователей
python main.py freeipa compare-users --domain example.com

# 4. Синхронизация групп
python main.py freeipa sync-groups --domain example.com --confirm

# 5. Синхронизация пользователей с группами по умолчанию
python main.py freeipa sync-all-users \
    --domain example.com \
    --groups employees domain-users \
    --confirm
```

### Добавление нового сотрудника

```bash
# Синхронизация пользователя с назначением в группы
python main.py freeipa sync-user newuser@example.com \
    --groups employees developers project-team-alpha
```

### Создание новой команды

```bash
# Создание группы
python main.py freeipa create-group project-alpha \
    --description "Команда проекта Alpha"

# Добавление участников
python main.py freeipa add-user-to-group user1@example.com project-alpha
python main.py freeipa add-user-to-group user2@example.com project-alpha
```

## Безопасность

### Рекомендации

1. **Используйте выделенного пользователя** для API подключений
2. **Ограничьте права** пользователя только необходимыми операциями
3. **Используйте Kerberos** для аутентификации в продакшене
4. **Храните credentials** в защищенном месте
5. **Регулярно ротируйте** пароли

### Настройка Kerberos

Для использования Kerberos аутентификации:

```json
{
  "server_url": "https://ipa.yourdomain.com",
  "domain": "yourdomain.com",
  "use_kerberos": true,
  "verify_ssl": true
}
```

Убедитесь, что система настроена для Kerberos и получен действующий тикет:

```bash
kinit admin@YOURDOMAIN.COM
```

## Мониторинг и логирование

Все операции логируются с использованием стандартного модуля logging Python:

```python
import logging

# Настройка уровня логирования
logging.getLogger('src.services.freeipa_client').setLevel(logging.DEBUG)
logging.getLogger('src.integrations.freeipa_integration').setLevel(logging.INFO)
```

### Примеры логов

```
INFO - Успешное подключение к FreeIPA
INFO - Пользователь user@example.com синхронизирован в FreeIPA
INFO - Группа developers создана в FreeIPA
ERROR - Ошибка создания пользователя: уже существует
```

## Устранение неполадок

### Частые проблемы

#### 1. Ошибка подключения

```
ERROR - Ошибка подключения к FreeIPA: connection refused
```

**Решение:**
- Проверьте URL сервера в конфигурации
- Убедитесь, что FreeIPA сервер доступен
- Проверьте сетевые настройки и файрволл

#### 2. Ошибка аутентификации

```
ERROR - Authentication failed
```

**Решение:**
- Проверьте имя пользователя и пароль
- Убедитесь, что пользователь имеет права на операции
- Для Kerberos - проверьте наличие действующего тикета

#### 3. SSL ошибки

```
ERROR - SSL certificate verification failed
```

**Решение:**
- Установите `verify_ssl: false` для тестирования
- Добавьте путь к CA сертификату в `ca_cert_path`
- Убедитесь, что сертификат сервера действителен

#### 4. Пользователь уже существует

```
ERROR - Duplicate entry
```

**Решение:**
- Используйте операции обновления вместо создания
- Проверьте существующих пользователей перед синхронизацией

### Диагностика

Для диагностики проблем используйте:

```bash
# Тестирование подключения
python main.py freeipa test-connection

# Подробная диагностика
python main.py freeipa stats --verbose

# Сравнение пользователей
python main.py freeipa compare-users
```

## Ограничения

1. **Производительность**: Большие объемы данных требуют времени для синхронизации
2. **Зависимости**: Требует установки дополнительных Python библиотек
3. **Сеть**: Операции выполняются по сети, возможны таймауты
4. **Права**: Требует административных прав в FreeIPA для некоторых операций

## Развитие

Планируемые улучшения:

- [ ] Двусторонняя синхронизация (FreeIPA → Google Workspace)
- [ ] Инкрементальная синхронизация
- [ ] Web UI для управления интеграцией
- [ ] Планировщик автоматической синхронизации
- [ ] Расширенная настройка атрибутов пользователей
- [ ] Поддержка LDAP групп
- [ ] Интеграция с системами мониторинга

## Поддержка

Для получения помощи:

1. Проверьте раздел "Устранение неполадок"
2. Включите подробное логирование (`--verbose`)
3. Проверьте логи в `logs/admin_tools.log`
4. Создайте issue с описанием проблемы и логами
