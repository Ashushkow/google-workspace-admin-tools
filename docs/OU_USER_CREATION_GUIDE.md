# 🏢 Создание пользователей с выбором организационного подразделения (OU)

## 📝 Обзор

В Admin Team Tools добавлена возможность создавать пользователей Google Workspace в конкретных организационных подразделениях (Organizational Units). Теперь вы можете размещать новых пользователей не только в корневом подразделении, но и в любом подразделении вашей организационной структуры, например `/HR/Admin`, `/IT/Developers` и т.д.

## ✨ Новые возможности

### 🎯 Выбор OU при создании пользователя
- **Выпадающий список** всех доступных подразделений
- **Автоматическая загрузка** OU из Google Workspace
- **Иерархическое отображение** с отступами для визуализации структуры
- **Корневое подразделение** выбрано по умолчанию

### 🏗️ Примеры организационной структуры
```
🏠 Корневое подразделение (/)
🏢 HR (/HR)
  🏢 Admin (/HR/Admin)
  🏢 Recruitment (/HR/Recruitment)
🏢 IT (/IT)
  🏢 Developers (/IT/Developers)
  🏢 Support (/IT/Support)
🏢 Finance (/Finance)
🏢 Marketing (/Marketing)
```

## 🚀 Как использовать

### В пользовательском интерфейсе

1. **Запустите приложение** Admin Team Tools
2. **Нажмите** кнопку "➕ Создать пользователя"
3. **Заполните обязательные поля:**
   - First Name (Имя)
   - Last Name (Фамилия)
   - Password (Пароль)
4. **🆕 Выберите подразделение** из выпадающего списка "Подразделение (OU):"
5. **При необходимости заполните** дополнительные поля
6. **Нажмите** "➕ Создать"

### Программно через API

```python
from src.api.users_api import create_user

# Создание пользователя в подразделении HR/Admin
result = create_user(
    service=google_service,
    email='admin.user@example.com',
    first_name='John',
    last_name='Admin',
    password='SecurePassword123!',
    org_unit_path='/HR/Admin'  # 🆕 Указываем OU
)
```

## 📊 Примеры использования

### Пример 1: HR Менеджер
```python
create_user(
    service=service,
    email='hr.manager@sputnik8.com',
    first_name='Anna',
    last_name='HRManager',
    password='HRPass123!',
    org_unit_path='/HR'
)
```

### Пример 2: Администратор в подразделении Admin
```python
create_user(
    service=service,
    email='admin.user@sputnik8.com',
    first_name='Alex',
    last_name='Administrator',
    password='AdminPass456!',
    org_unit_path='/HR/Admin'
)
```

### Пример 3: Разработчик в IT отделе
```python
create_user(
    service=service,
    email='dev.user@sputnik8.com',
    first_name='John',
    last_name='Developer',
    password='DevPass789!',
    org_unit_path='/IT/Developers'
)
```

## 🛡️ Требования и настройка

### Права API
Убедитесь, что у вашего Service Account есть следующие права:
```
https://www.googleapis.com/auth/admin.directory.user
https://www.googleapis.com/auth/admin.directory.orgunit
```

### Проверка настроек
1. **Google Cloud Console:** Admin SDK API включен
2. **Google Admin Console:** Domain-wide delegation настроено
3. **Service Account:** Имеет права на чтение и управление OU

## 🎯 Преимущества

- **🏢 Лучшая организация** пользователей по отделам
- **⚙️ Упрощение управления** правами и политиками
- **📋 Применение настроек** к группам пользователей
- **🌳 Структурированная иерархия** организации
- **🔒 Более точный контроль** доступа к ресурсам

## 🆘 Устранение неполадок

### Проблема: OU не загружаются
**Решение:**
1. Проверьте права Service Account
2. Убедитесь в наличии scope `admin.directory.orgunit`
3. Проверьте Domain-wide delegation

### Проблема: Пользователь создается в корневом OU
**Причины:**
- Неправильный путь к OU
- Недостаточно прав для указанного OU
- OU не существует

**Решение:**
- Проверьте существование OU в Google Admin Console
- Убедитесь в правильности пути (`/HR/Admin`, а не `HR/Admin`)

## 🧪 Тестирование

Запустите тестовые скрипты для проверки функциональности:

```powershell
# Тест функций OU
python test_ou_user_creation.py

# Демонстрация использования
python demo_ou_user_creation.py
```

---

**Обновлено:** 31 июля 2025  
**Версия:** 2.0.8  
**Автор:** Admin Team Tools
