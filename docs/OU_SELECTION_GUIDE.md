# 🏢 Выбор организационного подразделения (OU) при создании пользователя

## 📝 Обзор

Теперь при создании нового пользователя в Google Workspace можно выбрать организационное подразделение (Organizational Unit), в которое будет помещен пользователь.

## ✨ Новая функциональность

### 🎯 Что добавлено

1. **API для работы с OU** (`src/api/orgunits_api.py`)
   - `list_orgunits()` - получение списка всех OU в домене
   - `get_orgunit()` - получение информации о конкретном OU
   - `create_orgunit()` - создание нового OU
   - Утилиты для форматирования OU для UI

2. **Обновленное создание пользователей**
   - `create_user()` теперь поддерживает параметр `org_unit_path`
   - `create_user_with_welcome_email()` поддерживает OU
   - `create_user_with_auto_welcome()` поддерживает OU

3. **Обновленный пользовательский интерфейс**
   - В окне создания пользователя добавлено поле выбора OU
   - Автоматическая загрузка списка доступных OU
   - Корневое подразделение выбрано по умолчанию

## 🚀 Как использовать

### В пользовательском интерфейсе

1. Откройте окно создания пользователя
2. Заполните обязательные поля (имя, фамилия, пароль)
3. **Выберите подразделение** из выпадающего списка "Подразделение (OU):"
4. Нажмите "Создать"

### Программно

```python
from src.api.users_api import create_user

# Создание пользователя с указанием OU
result = create_user(
    service=google_service,
    email="user@example.com",
    first_name="John",
    last_name="Doe", 
    password="secure_password",
    org_unit_path="/IT/Developers"  # 🆕 Новый параметр
)
```

```python
from src.api.user_creation_service import create_user_with_welcome_email

# Создание пользователя с приветственным письмом и OU
result = create_user_with_welcome_email(
    service=google_service,
    gmail_credentials=gmail_creds,
    email="user@example.com",
    first_name="John",
    last_name="Doe",
    password="secure_password",
    admin_email="admin@example.com",
    org_unit_path="/HR/New_Employees"  # 🆕 Новый параметр
)
```

## 🏗️ Структура организационных подразделений

### Форматы путей OU

- **Корневое подразделение**: `/`
- **Подразделение первого уровня**: `/IT`
- **Вложенное подразделение**: `/IT/Developers`
- **Глубоко вложенное**: `/IT/Developers/Frontend`

### Отображение в UI

- 🏠 **Корневое подразделение** (по умолчанию)
- 🏢 **IT Department**
- 🏢 **HR Department**
  - 🏢 **New Employees** (с отступом для иерархии)

## ⚙️ Технические детали

### Новые файлы

- `src/api/orgunits_api.py` - API для работы с OU
- `test_ou_functionality.py` - тестовый скрипт

### Обновленные файлы

- `src/api/users_api.py` - добавлен параметр `org_unit_path`
- `src/api/user_creation_service.py` - поддержка OU в функциях создания
- `src/ui/user_windows.py` - добавлено поле выбора OU

### Необходимые права API

Убедитесь, что у вашего Service Account есть права на:
```
https://www.googleapis.com/auth/admin.directory.orgunit
```

## 🛡️ Безопасность и разрешения

### Требования к правам

1. **Admin SDK API** должен быть включен в Google Cloud Console
2. **Service Account** должен иметь права на чтение OU
3. **Domain-wide delegation** должно включать scope для `admin.directory.orgunit`

### Обработка ошибок

- Если OU недоступны - автоматически используется корневое подразделение
- При ошибках загрузки OU показывается только корневое подразделение
- Неправильные пути OU автоматически заменяются на корневое

## 🧪 Тестирование

Запустите тест для проверки функциональности:

```bash
python test_ou_functionality.py
```

Ожидаемый результат:
```
✅ Импорт orgunits_api прошел успешно
✅ Импорт обновленной users_api прошел успешно  
✅ Импорт обновленных функций user_creation_service прошел успешно
🎉 Все тесты пройдены успешно!
```

## 📊 Примеры использования

### Пример 1: Создание пользователя в IT отделе

```python
result = create_user(
    service=service,
    email="developer@company.com",
    first_name="Alex",
    last_name="Developer",
    password="Dev123!@#",
    org_unit_path="/IT/Developers"
)
```

### Пример 2: Создание пользователя с приветственным письмом в HR

```python
result = create_user_with_welcome_email(
    service=service,
    gmail_credentials=gmail_creds,
    email="hr.manager@company.com", 
    first_name="Jane",
    last_name="HR",
    password="HR123!@#",
    admin_email="admin@company.com",
    org_unit_path="/HR",
    send_welcome_email=True
)
```

## 🎯 Будущие улучшения

- [ ] Возможность создания новых OU прямо из интерфейса
- [ ] Массовое перемещение пользователей между OU
- [ ] Визуализация иерархии OU в виде дерева
- [ ] Фильтрация пользователей по OU в списке сотрудников

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
- Убедитесь в правильности пути (`/IT/Developers`, а не `IT/Developers`)

---

*Обновлено: $(Get-Date -Format "yyyy-MM-dd HH:mm")*
