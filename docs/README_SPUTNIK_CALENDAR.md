# 🎯 Управление календарем SPUTNIK (общий)

## Новая функциональность v2.0.7

Добавлена специализированная функциональность для управления общим календарем команды SPUTNIK.

### 📅 Календарь
- **Название:** SPUTNIK (общий)
- **URL:** https://calendar.google.com/calendar/u/0?cid=dGNvNXZpcWxjNnZ0MjBsYmtsaDAzdTJrYjhAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ
- **Участников:** 100+ сотрудников

### 🚀 Быстрый доступ

#### Из главного меню:
```
Календари → 🎯 Календарь SPUTNIK (общий)
```

#### Горячие клавиши:
```
Ctrl+Shift+S
```

#### Панель инструментов:
```
Кнопка: 🎯 SPUTNIK
```

### ✨ Возможности

- **👀 Просмотр участников** - полный список с ролями
- **➕ Добавление участников** - индивидуально или массово
- **🗑️ Удаление участников** - один или несколько
- **✏️ Изменение ролей** - владелец, редактор, читатель
- **🔍 Поиск и фильтрация** - быстрый поиск по email
- **📊 Статистика** - распределение по ролям
- **💾 Экспорт** - CSV/Excel списков участников

### 🔐 Роли доступа

| Роль | Описание | Права |
|------|----------|-------|
| 👑 **Владелец** | Полный доступ | Управление участниками + события |
| ✏️ **Редактор** | Редактирование | Создание и изменение событий |
| 👁️ **Читатель** | Просмотр | Только просмотр событий |

### 📊 Текущая статистика
- **Всего участников:** 100
- **Владельцев:** 14
- **Редакторов:** 83  
- **Читателей:** 3

### 🛠️ Техническая реализация

#### Новые классы:
- `GoogleCalendarAPI` - работа с Google Calendar API
- `SputnikCalendarManager` - управление календарем SPUTNIK
- `SputnikCalendarWindow` - пользовательский интерфейс

#### Новые файлы:
- `src/api/calendar_api.py`
- `src/api/sputnik_calendar.py`
- `src/ui/sputnik_calendar_ui.py`

### 🔧 Для разработчиков

#### Пример использования API:
```python
from src.api.sputnik_calendar import create_sputnik_calendar_manager

# Создаем менеджер
manager = create_sputnik_calendar_manager()

# Получаем участников
members = manager.get_members()

# Добавляем участника
manager.add_member("new.user@sputnik8.com", "reader")

# Удаляем участника  
manager.remove_member("old.user@sputnik8.com")

# Изменяем роль
manager.change_member_role("user@sputnik8.com", "writer")
```

#### Массовое добавление:
```python
members_data = [
    {"email": "user1@sputnik8.com", "role": "reader"},
    {"email": "user2@sputnik8.com", "role": "writer"}
]
results = manager.add_multiple_members(members_data)
```

### 📋 Демонстрация

Запустите демо-скрипт:
```bash
python demo_sputnik_calendar.py
```

---

**Версия:** 2.0.7  
**Автор:** Admin Team Tools  
**Дата:** Июль 2025
