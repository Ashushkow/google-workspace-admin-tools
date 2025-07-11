# 🛡️ Система обработки ошибок Admin Team Tools

## Обзор

Новая система обработки ошибок включает:

- **Кастомные исключения** для специфических ошибок
- **Централизованный обработчик** с умной категоризацией
- **Улучшенное логирование** с ротацией файлов и цветным выводом
- **Валидатор окружения** для проверки конфигурации
- **Graceful shutdown** с обработкой сигналов

## Структура

```
src/utils/
├── exceptions.py          # Кастомные исключения
├── enhanced_logger.py     # Система логирования
├── error_handler.py       # Централизованный обработчик
└── environment_validator.py  # Валидатор окружения
```

## Использование

### Кастомные исключения

```python
from src.utils.exceptions import *

# Ошибки конфигурации
raise ConfigurationError(
    "Неправильная конфигурация API",
    error_code="CONF_001",
    details={"file": "config.json", "line": 15}
)

# Ошибки Google API
raise GoogleAPIError(
    "Превышен лимит запросов",
    error_code="API_QUOTA_EXCEEDED"
)

# Ошибки Service Account
raise ServiceAccountError(
    "Не настроен DOMAIN_ADMIN_EMAIL",
    error_code="SA_DOMAIN_MISSING"
)
```

### Обработчик ошибок

```python
from src.utils.error_handler import ErrorHandler
from src.utils.enhanced_logger import setup_logging

logger = setup_logging()
error_handler = ErrorHandler(logger)

try:
    # Ваш код
    pass
except Exception as e:
    # Автоматическая обработка с правильным UI
    error_handler.handle_exception(e, "контекст операции")
```

### Логирование

```python
from src.utils.enhanced_logger import setup_logging

# Настройка с автоматической ротацией
logger = setup_logging(log_level="INFO", log_dir="logs")

logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
logger.critical("Критическая ошибка")
```

### Валидация окружения

```python
from src.utils.environment_validator import EnvironmentValidator

validator = EnvironmentValidator(logger)
success, errors, warnings = validator.validate_all()

if not success:
    print("Критические ошибки:")
    for error in errors:
        print(f"  • {error}")

if warnings:
    print("Предупреждения:")
    for warning in warnings:
        print(f"  • {warning}")
```

## Преимущества новой системы

### 1. **Специфичная обработка ошибок**
- Каждый тип ошибки обрабатывается индивидуально
- Пользователь получает понятные инструкции по исправлению
- Автоматическое определение типа проблемы

### 2. **Профессиональное логирование**
- Ротация файлов (10MB основной лог, 5MB для ошибок)
- Цветной вывод в консоль
- Структурированные сообщения с контекстом
- Автоматическое сохранение трассировки

### 3. **Валидация перед запуском**
- Проверка версии Python
- Валидация структуры проекта
- Проверка зависимостей
- Валидация credentials
- Проверка прав доступа

### 4. **Graceful shutdown**
- Обработка Ctrl+C и SIGTERM
- Корректное закрытие ресурсов
- Сохранение состояния при завершении

### 5. **Детальная диагностика**
- Коды ошибок для быстрой идентификации
- Контекстная информация
- Рекомендации по исправлению
- Ссылки на документацию

## Примеры сообщений об ошибках

### До (старая система):
```
Ошибка авторизации
Не удалось подключиться к Google API: 403 Forbidden
```

### После (новая система):
```
🚨 Ошибка Domain-wide delegation

Проблема с правами Service Account:
403 Forbidden: Request had insufficient authentication scopes

Необходимо:
1. Включить Domain-wide delegation в Google Cloud Console
2. Добавить необходимые OAuth scopes в Admin Console  
3. Убедиться, что DOMAIN_ADMIN_EMAIL корректен

📚 Подробная инструкция: docs/SERVICE_ACCOUNT_SETUP.md
🔧 Код ошибки: DD_001
```

## Структура логов

```
logs/
├── admin_tools.log     # Все события (ротация 10MB, 5 копий)
├── errors.log          # Только ошибки (ротация 5MB, 3 копии)
└── admin_tools.log.1   # Архивные копии
```

## Коды ошибок

| Код | Категория | Описание |
|-----|-----------|----------|
| CRED_001 | Credentials | Проблемы с credentials.json |
| SA_001 | Service Account | Ошибки Service Account |
| DD_001 | Domain Delegation | Проблемы с Domain-wide delegation |
| API_001 | Google API | Общие ошибки Google API |
| NET_001 | Network | Сетевые проблемы |
| CONF_001 | Configuration | Ошибки конфигурации |
| UI_001 | User Interface | Проблемы с интерфейсом |

## Интеграция в существующий код

Для интеграции в существующие модули:

```python
# В начале файла
from src.utils.exceptions import GoogleAPIError, NetworkError
from src.utils.enhanced_logger import setup_logging

logger = setup_logging()

# Вместо общих исключений
try:
    response = api_call()
except requests.exceptions.ConnectionError as e:
    raise NetworkError(f"Нет соединения с API: {e}", error_code="NET_CONNECTION")
except requests.exceptions.Timeout as e:
    raise NetworkError(f"Таймаут при вызове API: {e}", error_code="NET_TIMEOUT")
```

## Мониторинг и отладка

### Анализ логов:
```bash
# Последние ошибки
tail -n 50 logs/errors.log

# Поиск по коду ошибки
grep "DD_001" logs/admin_tools.log

# Статистика ошибок
grep -c "ERROR" logs/admin_tools.log
```

### Уровни логирования:
- **DEBUG**: Детальная отладочная информация
- **INFO**: Общие события приложения  
- **WARNING**: Предупреждения (не критичные)
- **ERROR**: Ошибки (требуют внимания)
- **CRITICAL**: Критические ошибки (приложение может остановиться)

## Performance

Новая система добавляет минимальные накладные расходы:
- ~50ms на инициализацию логирования
- ~1-2ms на обработку одной ошибки
- ~100KB дополнительного кода в exe файле

Для production рекомендуется использовать `main_optimized.py` с упрощенной обработкой ошибок.
