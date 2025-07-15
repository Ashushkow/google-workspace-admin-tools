# 🤝 Contributing to Admin Team Tools

Мы рады, что вы хотите внести свой вклад в развитие Admin Team Tools! Этот документ поможет вам начать.

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📝 Code of Conduct](#-code-of-conduct)
- [🐛 Bug Reports](#-bug-reports)
- [✨ Feature Requests](#-feature-requests)
- [💻 Development](#-development)
- [🧪 Testing](#-testing)
- [📚 Documentation](#-documentation)
- [🔄 Pull Requests](#-pull-requests)

## 🚀 Quick Start

1. **Fork** репозиторий на GitHub
2. **Clone** ваш fork локально:
   ```bash
   git clone https://github.com/YOUR_USERNAME/admin-team-tools.git
   cd admin-team-tools
   ```
3. **Настройте** среду разработки:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # или .venv\Scripts\activate на Windows
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```
4. **Создайте** ветку для вашей функции:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Code of Conduct

Участвуя в этом проекте, вы соглашаетесь соблюдать наш [Code of Conduct](CODE_OF_CONDUCT.md).

### Основные принципы:
- 🤝 Будьте уважительными и конструктивными
- 🌍 Приветствуйте разнообразие и инклюзивность
- 🎯 Фокусируйтесь на улучшении проекта
- 🔄 Помогайте другим участникам

## 🐛 Bug Reports

Нашли баг? Помогите нам его исправить!

### Перед созданием отчета:
1. 🔍 Проверьте [существующие issues](https://github.com/Ashushkow/admin-team-tools/issues)
2. 🔄 Убедитесь, что используете последнюю версию
3. 📋 Попробуйте воспроизвести баг в чистом окружении

### Информация для отчета:
```markdown
**Описание бага**
Краткое описание проблемы

**Шаги для воспроизведения**
1. Перейти в '...'
2. Нажать на '...'
3. Прокрутить до '...'
4. Увидеть ошибку

**Ожидаемое поведение**
Что должно было произойти

**Фактическое поведение** 
Что произошло на самом деле

**Окружение**
- ОС: [например, Windows 10]
- Python: [например, 3.11.0]
- Версия приложения: [например, 2.0.7]

**Дополнительная информация**
Логи, скриншоты, дополнительный контекст
```

## ✨ Feature Requests

Есть идея для новой функции? Мы будем рады её рассмотреть!

### Шаблон запроса:
```markdown
**Описание функции**
Краткое описание предлагаемой функции

**Проблема, которую решает**
Какую проблему решает эта функция?

**Предлагаемое решение**
Как вы видите реализацию?

**Альтернативы**
Рассматривали ли вы другие варианты?

**Дополнительная информация**
Любая дополнительная информация, диаграммы, примеры
```

## 💻 Development

### 🛠️ Настройка среды разработки

```bash
# Установка всех зависимостей для разработки
pip install -e ".[dev]"

# Настройка pre-commit hooks
pre-commit install

# Проверка настройки
python scripts/check_setup.py
```

### 📏 Стандарты кода

#### Python Code Style
```bash
# Форматирование кода
black src tests scripts

# Проверка стиля
flake8 src tests scripts

# Проверка типов
mypy src

# Сортировка импортов
isort src tests scripts
```

#### Правила:
- ✅ Следуйте **PEP 8**
- ✅ Используйте **type hints**
- ✅ Пишите **docstrings** для публичных функций
- ✅ Максимальная длина строки: **88 символов** (Black default)
- ✅ Используйте **английский язык** для кода и комментариев

### 🏗️ Архитектурные принципы

1. **Clean Architecture** - разделение по слоям
2. **SOLID принципы** - особенно SRP и DIP
3. **Repository Pattern** - абстракция доступа к данным
4. **Dependency Injection** - через DI контейнер
5. **Async/Await** - для всех I/O операций

### 📁 Структура коммитов

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### Типы коммитов:
- `feat`: новая функция
- `fix`: исправление бага
- `docs`: изменения в документации
- `style`: форматирование, отсутствие функциональных изменений
- `refactor`: рефакторинг кода
- `test`: добавление или изменение тестов
- `chore`: изменения в build процессе или auxiliary tools

#### Примеры:
```bash
feat(auth): add OAuth 2.0 refresh token handling
fix(ui): resolve window resizing issue on macOS
docs(readme): update installation instructions
test(api): add integration tests for user service
```

## 🧪 Testing

### Запуск тестов

```bash
# Все тесты
pytest tests/ -v

# С покрытием кода
pytest tests/ --cov=src --cov-report=html

# Только быстрые тесты
pytest tests/ -m "not slow"

# Конкретный модуль
pytest tests/test_auth.py -v
```

### Написание тестов

1. **Расположение**: тесты в папке `tests/`
2. **Именование**: файлы `test_*.py`, функции `test_*`
3. **Структура**:
   ```python
   def test_function_should_return_expected_result():
       # Arrange
       input_data = "test"
       expected = "expected_result"
       
       # Act
       result = function_under_test(input_data)
       
       # Assert
       assert result == expected
   ```

4. **Типы тестов**:
   - `tests/` - автоматические unit/integration тесты
   - `tests/manual/` - ручные тесты для отладки

### Покрытие кода

Стремимся к покрытию **> 80%** для новых модулей.

```bash
# Генерация отчета покрытия
pytest --cov=src --cov-report=html
open htmlcov/index.html  # просмотр отчета
```

## 📚 Documentation

### Документирование кода

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Краткое описание функции.
    
    Args:
        param1: Описание первого параметра
        param2: Описание второго параметра
        
    Returns:
        Описание возвращаемого значения
        
    Raises:
        ValueError: Когда param1 пустая строка
        
    Example:
        >>> example_function("test", 42)
        True
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    return len(param1) > param2
```

### Обновление документации

- 📝 Обновляйте README при изменении API
- 📚 Добавляйте новые документы в `docs/`
- 🔄 Обновляйте CHANGELOG.md для значимых изменений

## 🔄 Pull Requests

### Чек-лист перед созданием PR

- [ ] 🔄 Ветка обновлена с последней версией main/master
- [ ] ✅ Все тесты проходят
- [ ] 📏 Код соответствует стандартам стиля
- [ ] 📝 Добавлена/обновлена документация
- [ ] 🧪 Добавлены тесты для новой функциональности
- [ ] 📋 Заполнен шаблон PR

### Шаблон Pull Request

```markdown
## 📝 Описание изменений

Краткое описание того, что делает этот PR.

## 🔗 Связанные Issues

Fixes #123
Related to #456

## 🧪 Как тестировать

1. Шаги для тестирования изменений
2. Специальные случаи для проверки

## 📋 Чек-лист

- [ ] Код следует стилистическим требованиям проекта
- [ ] Проведен self-review кода
- [ ] Код прокомментирован в сложных местах
- [ ] Обновлена документация
- [ ] Изменения не ломают существующую функциональность
- [ ] Добавлены unit тесты для новой функциональности
- [ ] Все тесты проходят локально

## 📱 Скриншоты (если применимо)

Добавьте скриншоты изменений в UI

## ✨ Дополнительная информация

Любая дополнительная информация о PR
```

### Процесс Review

1. 👀 **Автоматические проверки** - CI/CD pipeline
2. 🔍 **Code Review** - минимум 1 approver
3. 🧪 **Тестирование** - manual testing если необходимо
4. 🚀 **Merge** - squash and merge для чистой истории

## 🎯 Приоритетные области для участия

### 🔥 High Priority
- 🐛 Исправление багов
- 🔐 Улучшения безопасности
- 📈 Оптимизация производительности
- 🧪 Увеличение покрытия тестами

### 🌟 Medium Priority
- ✨ Новые функции для пользователей
- 🎨 Улучшения UI/UX
- 📚 Улучшение документации
- 🔧 Инструменты разработки

### 💡 Ideas Welcome
- 🌍 Интернационализация (i18n)
- 📱 Веб-интерфейс
- 🔌 Система плагинов
- 🤖 Автоматизация workflows

## 📞 Получение помощи

Нужна помощь? Мы здесь!

- 💬 [GitHub Discussions](https://github.com/Ashushkow/admin-team-tools/discussions)
- 🐛 [GitHub Issues](https://github.com/Ashushkow/admin-team-tools/issues)
- 📧 Email: admin@example.com

---

## 🙏 Благодарности

Спасибо за ваш вклад в развитие Admin Team Tools! Каждый участник делает проект лучше.

### 🌟 Участники

Полный список участников доступен на [странице contributors](https://github.com/Ashushkow/admin-team-tools/graphs/contributors).

---

*Этот документ обновляется по мере развития проекта. Последнее обновление: июль 2025*
