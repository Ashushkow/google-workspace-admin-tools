# 🤝 Руководство по участию в разработке

Спасибо за интерес к участию в развитии Admin Team Tools! Мы ценим любой вклад в проект.

## 📋 Кодекс поведения

Участвуя в этом проекте, вы соглашаетесь соблюдать наш [Кодекс поведения](CODE_OF_CONDUCT.md).

## 🚀 Как начать

### 1. Настройка окружения

```bash
# Клонирование вашего fork
git clone https://github.com/yourusername/admin-team-tools.git
cd admin-team-tools

# Добавление upstream репозитория
git remote add upstream https://github.com/original/admin-team-tools.git

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Создание ветки

```bash
# Обновление master
git checkout master
git pull upstream master

# Создание новой ветки
git checkout -b feature/your-feature-name
```

## 🏗️ Типы вкладов

### 🐛 Исправление багов
- Поищите существующие issues перед созданием нового
- Опишите шаги для воспроизведения
- Включите информацию о системе (OS, Python версия)

### ✨ Новые функции
- Обсудите большие изменения в issues перед началом работы
- Следуйте архитектурным принципам проекта
- Добавляйте тесты для новой функциональности

### 📚 Документация
- Исправления опечаток всегда приветствуются
- Добавляйте примеры использования
- Обновляйте документацию при изменении API

## 🔧 Стандарты разработки

### Python код

```python
# ✅ Хорошо
def get_user_by_email(service: Any, email: str) -> Optional[Dict[str, Any]]:
    """
    Получение пользователя по email адресу.
    
    Args:
        service: Аутентифицированный Google Admin SDK сервис
        email: Email адрес пользователя
        
    Returns:
        Словарь с данными пользователя или None если не найден
        
    Raises:
        HttpError: При ошибке API запроса
    """
    try:
        user = service.users().get(userKey=email).execute()
        return user
    except HttpError as e:
        if e.resp.status == 404:
            return None
        raise e

# ❌ Плохо
def get_user(service, email):
    user = service.users().get(userKey=email).execute()
    return user
```

### Соглашения

- **PEP 8** для стиля кода
- **Type hints** для всех функций
- **Docstrings** в формате Google Style
- **f-strings** для форматирования строк
- **Константы** в UPPER_CASE

### Структура коммитов

```bash
# Формат: тип(область): описание

feat(calendar): добавлена поддержка групповых календарей
fix(auth): исправлена ошибка обновления токена
docs(readme): обновлены инструкции по установке
style(ui): улучшен отступ в компонентах
refactor(api): оптимизирован код загрузки пользователей
test(user): добавлены тесты для создания пользователя
```

### Типы коммитов

- `feat`: новая функциональность
- `fix`: исправление бага
- `docs`: изменения в документации
- `style`: форматирование кода (без изменения логики)
- `refactor`: рефакторинг кода
- `test`: добавление/изменение тестов
- `chore`: обновление зависимостей, настройки

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
python -m pytest

# С покрытием
python -m pytest --cov=src

# Конкретный файл
python -m pytest tests/test_user_management.py

# С детальным выводом
python -m pytest -v
```

### Написание тестов

```python
import pytest
from unittest.mock import Mock, patch
from src.api.user_management import create_user

class TestUserManagement:
    """Тесты для управления пользователями."""
    
    @patch('src.api.user_management.get_service')
    def test_create_user_success(self, mock_service):
        """Тест успешного создания пользователя."""
        # Arrange
        mock_service.users().insert().execute.return_value = {
            'primaryEmail': 'test@example.com',
            'name': {'givenName': 'Test', 'familyName': 'User'}
        }
        
        user_data = {
            'primaryEmail': 'test@example.com',
            'name': {'givenName': 'Test', 'familyName': 'User'}
        }
        
        # Act
        result = create_user(mock_service, user_data)
        
        # Assert
        assert result['primaryEmail'] == 'test@example.com'
        mock_service.users().insert.assert_called_once()
```

## 🎨 UI/UX Рекомендации

### Дизайн компонентов

- Используйте существующие UI компоненты
- Следуйте цветовой схеме тем
- Обеспечьте доступность (accessibility)
- Тестируйте на разных разрешениях

### Локализация

```python
# Используйте константы для текста
class UIStrings:
    CREATE_USER_TITLE = "Создание пользователя"
    CREATE_USER_SUCCESS = "Пользователь успешно создан"
    
# Вместо хардкода
button = tk.Button(text=UIStrings.CREATE_USER_TITLE)
```

## 📝 Процесс review

### Создание Pull Request

1. **Убедитесь** что все тесты проходят
2. **Обновите** документацию при необходимости
3. **Заполните** шаблон PR полностью
4. **Свяжите** с соответствующими issues

### Шаблон PR

```markdown
## 📋 Описание

Краткое описание изменений.

## 🔧 Тип изменений

- [ ] 🐛 Исправление бага
- [ ] ✨ Новая функциональность
- [ ] 💥 Breaking change
- [ ] 📚 Документация

## ✅ Чек-лист

- [ ] Код следует стилю проекта
- [ ] Добавлены тесты
- [ ] Все тесты проходят
- [ ] Документация обновлена
- [ ] Нет конфликтов с master

## 🧪 Тестирование

Опишите как тестировались изменения.

## 📸 Скриншоты

Если применимо, добавьте скриншоты.
```

### Критерии approval

- ✅ **Код качественный** и читаемый
- ✅ **Тесты покрывают** новую функциональность
- ✅ **Документация актуальная**
- ✅ **Нет breaking changes** без обсуждения
- ✅ **Performance** не ухудшился

## 🏷️ Релизы

### Версионирование

Проект использует [Semantic Versioning](https://semver.org/):

- **MAJOR** версия: breaking changes
- **MINOR** версия: новая функциональность (обратно совместимая)
- **PATCH** версия: исправления багов

### Процесс релиза

1. Создание release branch
2. Обновление CHANGELOG.md
3. Обновление версии в коде
4. Создание GitHub Release
5. Merge в master

## 🙋‍♀️ Нужна помощь?

- 💬 **GitHub Discussions** для общих вопросов
- 🐛 **GitHub Issues** для багов и предложений
- 📧 **Email**: dev@admin-tools.dev для приватных вопросов

## 🎉 Признание

Все участники проекта будут указаны в:
- README.md в разделе Contributors
- CHANGELOG.md для соответствующих релизов
- GitHub Contributors

Спасибо за ваш вклад! 🚀
