# 📁 Система управления путями файлов

## Обзор

Модуль `file_paths.py` обеспечивает организованное размещение всех создаваемых файлов в соответствующих директориях согласно новой структуре проекта.

## 🎯 Цель

Предотвратить создание файлов в корневой директории проекта и автоматически направлять их в правильные папки:

- **`logs/`** - файлы логирования
- **`data/exports/`** - экспортированные файлы
- **`config/`** - файлы конфигурации
- **`temp/`** - временные файлы
- **`cache/`** - кэш файлы
- **`tests/data/`** - тестовые данные

## 🔧 Использование

### Основные функции

```python
from utils.file_paths import get_export_path, get_log_path, get_config_path

# Получить правильный путь для экспорта
export_file = get_export_path("users_export.csv")

# Получить правильный путь для логов
log_file = get_log_path("application.log")

# Получить правильный путь для конфигурации
config_file = get_config_path("settings.json")
```

### Автоматическое определение

```python
from utils.file_paths import get_organized_path

# Автоматическое определение папки по типу файла
organized_path = get_organized_path("user_export.csv")  # → data/exports/
organized_path = get_organized_path("app.log")          # → logs/
organized_path = get_organized_path("theme_config.json") # → config/
```

## 📂 Структура директорий

```
📦 Project/
├── 📁 logs/                 # Файлы логирования
│   ├── admin_tools.log
│   ├── errors.log
│   └── security_audit.json
├── 📁 data/                 # Данные приложения
│   ├── 📁 exports/          # Экспортированные файлы
│   ├── 📁 reports/          # Отчеты
│   └── 📁 security/         # Файлы безопасности
├── 📁 config/               # Конфигурационные файлы
│   ├── 📁 themes/           # Настройки тем
│   ├── settings.json
│   └── app_config.json
├── 📁 temp/                 # Временные файлы
├── 📁 cache/                # Кэш файлы
└── 📁 tests/                # Тестовые файлы
    ├── 📁 data/             # Тестовые данные
    └── 📁 logs/             # Тестовые логи
```

## 🛠️ Интегрированные компоненты

### 1. Система логирования (`enhanced_logger.py`)
- Автоматически сохраняет логи в `logs/`
- Поддерживает ротацию файлов

### 2. Экспорт данных (`main_window.py`, `sputnik_calendar_ui.py`)
- Предлагает сохранение в `data/exports/`
- Автоматическое именование с timestamp

### 3. Конфигурация тем (`theme_manager.py`)
- Сохраняет настройки в `config/themes/`

### 4. Безопасность (`security_manager.py`)
- Ключи и аудит в `data/security/`

## 🔒 Совместимость

Система сохраняет совместимость с существующими файлами:
- `credentials.json` остается в корне
- `token.pickle` остается в корне
- Старые файлы постепенно мигрируются

## 🧹 Очистка

```python
from utils.file_paths import file_path_manager

# Очистка временных файлов старше 24 часов
file_path_manager.clean_temp_files(max_age_hours=24)

# Получить статистику директорий
info = file_path_manager.get_directory_info()
print(info)
```

## ✅ Преимущества

1. **Организованность** - четкая структура проекта
2. **Автоматизация** - файлы сами попадают в нужные места
3. **Совместимость** - работает с существующим кодом
4. **Масштабируемость** - легко добавить новые типы файлов
5. **Очистка** - автоматическое управление временными файлами

## 🔄 Миграция

При первом запуске система автоматически:
1. Создает необходимые директории
2. Направляет новые файлы в правильные места
3. Сохраняет совместимость со старыми путями

## 📋 Примеры использования

### Экспорт пользователей
```python
# Старый способ
filename = filedialog.asksaveasfilename(defaultextension='.csv')

# Новый способ
suggested_path = get_export_path(f"users_{datetime.now().strftime('%Y%m%d')}.csv")
filename = filedialog.asksaveasfilename(initialfile=str(suggested_path))
```

### Логирование
```python
# Автоматически в logs/
log_file = get_log_path('admin_tools.log')
handler = logging.FileHandler(log_file)
```

### Конфигурация
```python
# Автоматически в config/
config_file = get_config_path('app_settings.json')
with open(config_file, 'w') as f:
    json.dump(settings, f)
```
