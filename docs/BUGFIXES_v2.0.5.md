# Исправления ошибок v2.0.5

## Проблема: Ошибка инициализации UI компонентов

### Описание проблемы
При запуске приложения возникала ошибка:
```
AttributeError: 'MainWindow' object has no attribute 'status_indicator'
```

### Причина
Метод `check_service_status` вызывался до создания UI компонентов (`status_indicator` и `status_label`), которые создаются в методе `setup_ui`.

### Исправление

#### 1. Перенос инициализации в `_delayed_init`
Вызовы `check_service_status()` и `load_statistics()` перенесены в метод `_delayed_init()`, который выполняется после создания UI:

```python
def _delayed_init(self):
    """Отложенная инициализация после создания UI"""
    self._ui_initialized = True
    
    # Теперь, когда UI создан, можем проверить статус сервиса
    self.check_service_status()
    
    # Загружаем статистику
    self.load_statistics()
```

#### 2. Добавление проверок инициализации UI
Добавлены проверки `_ui_initialized` в критические методы:

**check_service_status:**
```python
def check_service_status(self):
    """Проверка статуса подключения к Google API"""
    # Проверяем, что UI инициализирован
    if not self._ui_initialized or not hasattr(self, 'status_indicator') or not self.status_indicator:
        return
    # ... остальной код
```

**load_statistics:**
```python
def load_statistics(self):
    """Загрузка статистики пользователей и групп"""
    if not self._ui_initialized or not self.service or not self.statistics_panel:
        return
    # ... остальной код
```

**log_activity:**
```python
def log_activity(self, message: str, level: str = 'INFO'):
    """Добавляет запись в журнал активности"""
    if self._ui_initialized and self.activity_log:
        self.activity_log.add_entry(message, level)
```

### Результат
- ✅ Приложение запускается без ошибок
- ✅ UI компоненты создаются в правильном порядке
- ✅ Статус сервиса проверяется после инициализации UI
- ✅ Статистика загружается корректно
- ✅ Журнал активности работает правильно

### Файлы изменены
- `src/ui/main_window.py` - исправлена инициализация UI

### Тестирование
Приложение успешно запускается и работает без ошибок инициализации.
