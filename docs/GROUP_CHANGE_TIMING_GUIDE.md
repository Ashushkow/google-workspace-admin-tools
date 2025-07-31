# Руководство по времени отражения изменений в группах Google Workspace

## ⏱️ Время отражения изменений

### **Немедленно (0-30 секунд)**
- **Добавление/удаление участников групп** - изменения видны сразу в Admin Console
- **Изменение ролей участников** (owner, manager, member)
- **Базовые изменения настроек группы**

### **До 2-10 минут**
- **Gmail и другие Google сервисы** - требуют время для синхронизации
- **Разрешения на файлы/папки Google Drive**
- **Календари и встречи**

### **До 24 часов**
- **Внешние интеграции и SSO системы**
- **Кэшированные данные в сторонних приложениях**

## 🔧 Использование верификации

### Базовое использование
```python
from src.services.group_service import GroupService

# Удаление с автоматической верификацией (рекомендуется)
success = await group_service.remove_member(
    group_email="group@company.com",
    member_email="user@company.com",
    verify=True  # По умолчанию True
)

# Добавление с верификацией
success = await group_service.add_member(
    group_email="group@company.com", 
    member_email="user@company.com",
    verify=True
)
```

### Быстрые операции без верификации
```python
# Для массовых операций, где скорость важнее надежности
success = await group_service.remove_member(
    group_email="group@company.com",
    member_email="user@company.com", 
    verify=False  # Отключаем верификацию
)
```

### Получение статистики производительности
```python
# Статистика времени выполнения операций
stats = group_service.get_operation_statistics()
print(f"Среднее время удаления: {stats.get('remove_member', {}).get('average', 0):.2f}с")

# Последние операции
recent = group_service.get_recent_operations(10)
for op in recent:
    print(f"{op['operation']}: {op['duration']}с - {'✅' if op['success'] else '❌'}")

# Статус группы
status = await group_service.get_group_propagation_status("group@company.com")
print(f"Участников в группе: {status.get('member_count', 0)}")
```

## 📊 Мониторинг операций

### Ручной мониторинг
```python
from src.utils.group_verification import GroupOperationMonitor

monitor = GroupOperationMonitor()

# Мониторинг пользовательской операции
with monitor.time_operation("custom_operation", "group@company.com"):
    # Ваш код здесь
    pass

# Получение статистики
stats = monitor.get_average_times()
```

### Интегрированный мониторинг
Все операции через `GroupService` автоматически мониторятся:
- Время выполнения API вызовов
- Время верификации изменений
- Статистика успешности операций

## 🔍 Настройка верификации

### Параметры верификации
```python
from src.utils.group_verification import GroupChangeVerifier
from src.api.google_api_client import GoogleAPIClient

api_client = GoogleAPIClient()
verifier = GroupChangeVerifier(api_client)

# Проверка удаления с настраиваемыми параметрами
success = verifier.verify_member_removal(
    group_email="group@company.com",
    user_email="user@company.com",
    max_retries=5,      # Количество попыток (по умолчанию 3)
    retry_delay=10      # Задержка между попытками в секундах (по умолчанию 5)
)
```

### Получение статуса распространения
```python
status = verifier.get_propagation_status("group@company.com")
print(f"Статус группы: {status}")
# Возвращает:
# {
#     'group_email': 'group@company.com',
#     'group_name': 'Название группы',
#     'member_count': 15,
#     'status': 'active',
#     'direct_members_count': 12
# }
```

## ⚡ Оптимизация производительности

### Для критически важных операций
- Используйте `verify=True` (по умолчанию)
- Мониторьте логи для отслеживания проблем
- Проверяйте статистику производительности

### Для массовых операций
- Используйте `verify=False` для ускорения
- Добавляйте задержки между запросами (rate limiting)
- Группируйте операции по батчам

### Обработка ошибок
```python
try:
    success = await group_service.remove_member(
        group_email="group@company.com",
        member_email="user@company.com"
    )
    if not success:
        print("Операция не выполнена или верификация не прошла")
except GroupNotFoundError:
    print("Группа не найдена")
except Exception as e:
    print(f"Неожиданная ошибка: {e}")
```

## 📈 Анализ производительности

### Очистка истории операций
```python
# Очистка истории для освобождения памяти
group_service.clear_operation_history()
```

### Экспорт статистики
```python
import json

# Получение и сохранение статистики
stats = group_service.get_operation_statistics()
with open('group_operations_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

# Получение детальной истории
recent = group_service.get_recent_operations(100)
with open('group_operations_history.json', 'w') as f:
    json.dump(recent, f, indent=2)
```

## 🚨 Рекомендации по troubleshooting

### Если операции выполняются медленно
1. Проверьте статистику: `group_service.get_operation_statistics()`
2. Убедитесь в стабильности интернет-соединения
3. Проверьте квоты Google API
4. Используйте `verify=False` для не критичных операций

### Если верификация не проходит
1. Увеличьте количество попыток: `max_retries=5`
2. Увеличьте задержку: `retry_delay=10`
3. Проверьте логи на наличие ошибок API
4. Убедитесь, что группа и пользователь существуют

### Логирование
Все операции автоматически логируются:
- ✅ Успешные операции
- ❌ Ошибки с детальной информацией  
- ⏱️ Время выполнения
- 🔍 Результаты верификации

---

**Итог:** Изменения в группах Google Workspace обычно отражаются **в течение 30 секунд** через Directory API, но полная синхронизация во всех сервисах может занять **до 10 минут**. Используйте встроенную верификацию для гарантии применения изменений.
