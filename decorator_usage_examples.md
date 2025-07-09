# 📋 Полная документация по UI декораторам

Этот файл содержит все примеры применения декораторов из `src/utils/ui_decorators.py`.

## 1. **handle_service_errors** - Обработка ошибок API операций

```python
from src.utils.ui_decorators import handle_service_errors

class AdminToolsMainWindow:
    @handle_service_errors("получение списка пользователей", require_service=True)
    def open_employee_list(self):
        """Открыть окно списка сотрудников"""
        # Автоматически проверяет self.service
        # Логирует успех/ошибки
        # Показывает messagebox при ошибках
        return EmployeeListWindow(self, self.service)
        
    @handle_service_errors("экспорт пользователей", require_service=True)
    def export_users(self):
        """Экспорт пользователей в CSV"""
        # Код метода...
```

## 2. **handle_ui_errors** - Обработка ошибок UI операций

```python
from src.utils.ui_decorators import handle_ui_errors

class AdminToolsMainWindow:
    @handle_ui_errors("открытие настроек", show_success=False)
    def open_settings_window(self):
        """Открыть окно настроек"""
        # Обрабатывает ошибки UI
        # Опционально показывает успех
        window = SettingsWindow(self)
        
    @handle_ui_errors("сохранение конфигурации", show_success=True)
    def save_config(self):
        """Сохранить конфигурацию"""
        # Код метода...
```

## 3. **log_operation** - Простое логирование

```python
from src.utils.ui_decorators import log_operation

class AdminToolsMainWindow:
    @log_operation("Открыто окно редактирования пользователя", "INFO")
    def open_edit_user(self):
        """Открыть окно редактирования пользователя"""
        # Код метода...
        
    @log_operation("Выполнена проверка статуса API", "DEBUG")
    def check_api_status(self):
        """Проверить статус подключения к API"""
        # Код метода...
```

## 4. **validate_input** - Валидация входных данных

```python
from src.utils.ui_decorators import validate_input

def is_valid_user_data(data):
    """Проверка корректности данных пользователя"""
    return data and isinstance(data, dict) and 'email' in data

class UserEditWindow:
    @validate_input(is_valid_user_data, "Некорректные данные пользователя")
    def save_user(self, user_data):
        """Сохранить данные пользователя"""
        # Код метода...
```

## 5. **validate_email** - Валидация email адресов

```python
from src.utils.ui_decorators import validate_email

class AdminToolsMainWindow:
    @validate_email
    def search_user_by_email(self, email):
        """Найти пользователя по email"""
        # Автоматически валидирует email в аргументах
        # Код метода...
        
    @validate_email
    def send_notification(self, email, message):
        """Отправить уведомление пользователю"""
        # Код метода...
```

## 6. **require_confirmation** - Запрос подтверждения

```python
from src.utils.ui_decorators import require_confirmation

class AdminToolsMainWindow:
    @require_confirmation("Вы действительно хотите удалить этого пользователя?")
    def delete_user(self, user_id):
        """Удалить пользователя"""
        # Показывает диалог подтверждения
        # Код метода...
        
    @require_confirmation("Это действие изменит права доступа. Продолжить?")
    def change_user_permissions(self, user_id, permissions):
        """Изменить права пользователя"""
        # Код метода...
```

## 7. **measure_performance** - Измерение времени выполнения

```python
from src.utils.ui_decorators import measure_performance

class AdminToolsMainWindow:
    @measure_performance
    def export_large_dataset(self):
        """Экспорт большого объема данных"""
        # Автоматически логирует время выполнения
        # Код метода...
        
    @measure_performance
    def sync_with_server(self):
        """Синхронизация с сервером"""
        # Код метода...
```

## 8. **retry_on_failure** - Повторные попытки

```python
from src.utils.ui_decorators import retry_on_failure

class AdminToolsMainWindow:
    @retry_on_failure(max_attempts=3, delay=2.0)
    def connect_to_api(self):
        """Подключение к API с повторными попытками"""
        # Код метода...
        
    @retry_on_failure(max_attempts=5, delay=1.0)
    def upload_file(self, file_path):
        """Загрузка файла с повторными попытками"""
        # Код метода...
```

## 9. **cache_result** - Кэширование результатов

```python
from src.utils.ui_decorators import cache_result

class AdminToolsMainWindow:
    @cache_result(maxsize=50)
    def get_user_groups(self, user_id):
        """Получить группы пользователя (с кэшированием)"""
        # Код метода...
        
    @cache_result(maxsize=100)
    def get_organization_structure(self):
        """Получить структуру организации (с кэшированием)"""
        # Код метода...

## 6. **retry_on_failure** - Повторные попытки

```python
@retry_on_failure(max_attempts=3, delay=2.0)
def unstable_api_call(self):
    # Повторяет до 3 раз с задержкой 2 сек
    return call_external_api()
```

## 7. **cache_result** - Кэширование результатов

```python
@cache_result(cache_duration=300)  # 5 минут
def get_user_list(self):
    # Кэширует результат на 5 минут
    return fetch_users_from_api()
```

## 8. **Комбинирование декораторов**

```python
@handle_service_errors("получение списка пользователей")
@measure_performance
@cache_result(cache_duration=180)
def get_filtered_users(self, filter_criteria):
    # 1. Проверяет подключение к API
    # 2. Измеряет производительность
    # 3. Кэширует результат на 3 минуты
    # 4. Обрабатывает ошибки
    return filter_users_api(self.service, filter_criteria)
```

## Комбинирование декораторов

Декораторы можно комбинировать для более сложной логики:

```python
from src.utils.ui_decorators import (
    handle_service_errors, 
    validate_email, 
    measure_performance, 
    require_confirmation
)

class AdminToolsMainWindow:
    @measure_performance
    @handle_service_errors("отправка уведомления", require_service=True)
    @validate_email
    @require_confirmation("Отправить уведомление выбранным пользователям?")
    def send_bulk_notification(self, email_list, message):
        """Отправить массовое уведомление с полной обработкой"""
        # Код метода...
        
    @cache_result(maxsize=20)
    @measure_performance
    @handle_service_errors("получение статистики", require_service=True)
    def get_user_statistics(self, department=None):
        """Получить статистику пользователей с кэшированием"""
        # Код метода...
```

## Применение к компонентам

Декораторы также можно использовать в компонентах UI:

```python
# src/ui/components/statistics_panel.py
from src.utils.ui_decorators import handle_ui_errors, measure_performance

class StatisticsPanel:
    @measure_performance
    @handle_ui_errors("обновление статистики")
    def update_statistics(self, users_data):
        """Обновить статистику пользователей"""
        # Код метода...

# src/ui/components/activity_log.py
from src.utils.ui_decorators import handle_ui_errors

class ActivityLog:
    @handle_ui_errors("очистка журнала")
    def clear_log(self):
        """Очистить журнал активности"""
        # Код метода...
```

## Текущее применение в проекте

В главном окне уже применены следующие декораторы:

```python
# src/ui/main_window.py

@handle_service_errors("открытие списка сотрудников")
def open_employee_list(self):
    # Код метода...

@handle_service_errors("открытие окна редактирования пользователя")  
def open_edit_user(self):
    # Код метода...

@handle_service_errors("экспорт пользователей")
@measure_performance
def export_users(self):
    # Код метода...

@handle_ui_errors("открытие окна настроек")
def open_settings_window(self):
    # Код метода...

@handle_ui_errors("открытие информации о приложении")
def show_about(self):
    # Код метода...
```

## Рекомендации по использованию

1. **handle_service_errors** - используйте для всех операций, требующих Google API
2. **handle_ui_errors** - для локальных UI операций
3. **validate_email** - для всех методов, работающих с email
4. **require_confirmation** - для критических операций (удаление, изменение прав)
5. **measure_performance** - для медленных операций (экспорт, загрузка)
6. **retry_on_failure** - для нестабильных сетевых операций
7. **cache_result** - для часто запрашиваемых данных
8. **log_operation** - для важных пользовательских действий

## Преимущества использования

- **Единообразие**: Все ошибки обрабатываются одинаково
- **Читаемость**: Основная логика не загромождена обработкой ошибок
- **Поддерживаемость**: Изменения в обработке ошибок вносятся в одном месте
- **Функциональность**: Дополнительные возможности (логирование, валидация) добавляются легко
- **Тестируемость**: Декораторы можно тестировать отдельно

## Будущие расширения

Возможные дополнительные декораторы:

1. **@async_operation** - для асинхронных операций
2. **@audit_log** - для аудита критических действий
3. **@rate_limit** - для ограничения частоты вызовов API
4. **@permission_required** - для проверки прав доступа
5. **@backup_before** - для создания резервных копий перед изменениями
