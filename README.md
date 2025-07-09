<div align="center">

# 🚀 Admin Team Tools

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/yourusername/admin-team-tools/ci.yml?branch=main&style=for-the-badge&logo=github&logoColor=white" alt="CI/CD Status">
  <img src="https://img.shields.io/codecov/c/github/yourusername/admin-team-tools?style=for-the-badge&logo=codecov&logoColor=white" alt="Coverage">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge" alt="License">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Google%20Workspace-Admin%20SDK-red.svg?style=for-the-badge&logo=google&logoColor=white" alt="Google Workspace">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/version-2.0.6-brightgreen.svg?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/github/issues/yourusername/admin-team-tools?style=for-the-badge&logo=github&logoColor=white" alt="Issues">
</p>

<h3>🎯 Мощное и интуитивное приложение для управления Google Workspace</h3>

<p><em>Упростите администрирование пользователей, групп и календарей с помощью современного интерфейса</em></p>

<p>
  <a href="#-быстрый-старт">🚀 Быстрый старт</a> •
  <a href="#-документация">📖 Документация</a> •
  <a href="#-возможности">✨ Возможности</a> •
  <a href="#-участие-в-разработке">🤝 Участие</a>
</p>

<img src="https://user-images.githubusercontent.com/placeholder/demo.gif" alt="Demo" width="600">

</div>

<br>

<div align="center">

## 🌟 Почему выбирают Admin Team Tools?

| 🚀 **Быстро** | 🛡️ **Безопасно** | 🎨 **Красиво** | 📈 **Масштабируемо** |
|:---:|:---:|:---:|:---:|
| Запуск за 2 минуты | OAuth2 + валидация | 3 встроенные темы | Поддержка больших организаций |
| Готовые шаблоны | Журнал всех действий | Адаптивный дизайн | Асинхронные операции |

</div>

---

## ✨ Возможности

### 👥 Управление пользователями
- **Создание пользователей** с полной валидацией данных
- **Редактирование** всех атрибутов пользователя
- **Удаление** с подтверждением безопасности
- **Поиск и фильтрация** по различным критериям
- **Массовый экспорт** в Excel/CSV формате

### 🔒 Управление группами
- **Просмотр всех групп** организации
- **Управление участниками** групп
- **Создание новых групп** с настройками
- **Синхронизация** с Google Directory

### 📅 Управление календарями
- **Просмотр календарей** всех пользователей
- **Добавление пользователей** в общие календари
- **Управление ролями доступа** (чтение, редактор, владелец)
- **Создание общих календарей** для команд

### 🎨 Современный интерфейс
- **3 встроенные темы**: светлая, тёмная, синяя
- **Горячие клавиши** для быстрой работы
- **Адаптивный дизайн** с модульными компонентами
- **Журнал активности** всех операций

---

## 🖼️ Скриншоты

<div align="center">

### Главное окно приложения
![Главное окно](docs/images/main_window.png)

### Управление пользователями
![Управление пользователями](docs/images/user_management.png)

### Тёмная тема
![Тёмная тема](docs/images/dark_theme.png)

</div>

---

## 🛠️ Технологии

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-FF6B6B?style=for-the-badge&logo=python&logoColor=white)
![Google API](https://img.shields.io/badge/Google%20API-4285F4?style=for-the-badge&logo=google&logoColor=white)
![OAuth2](https://img.shields.io/badge/OAuth2-4285F4?style=for-the-badge&logo=oauth&logoColor=white)

</div>

- **Backend**: Python 3.8+ с асинхронными операциями
- **UI Framework**: Tkinter с кастомными компонентами
- **API**: Google Workspace Admin SDK, Calendar API
- **Архитектура**: SOLID принципы, модульная структура
- **Безопасность**: OAuth2, валидация данных, обработка ошибок

---

## 🚀 Быстрый старт

### Предварительные требования

- **Python 3.8+** установлен в системе
- **Google Workspace Admin** аккаунт
- **Доступ к Google Cloud Console** для настройки API

### 1️⃣ Клонирование репозитория

```bash
git clone https://github.com/yourusername/admin-team-tools.git
cd admin-team-tools
```

### 2️⃣ Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv .venv

# Активация (Windows)
.venv\Scripts\activate

# Активация (macOS/Linux)
source .venv/bin/activate

# Установка пакетов
pip install -r requirements.txt
```

### 3️⃣ Настройка Google API

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите необходимые API:
   - Admin SDK API
   - Google Calendar API
4. Создайте Service Account или OAuth2 credentials
5. Скачайте файл `credentials.json` в корень проекта

### 4️⃣ Запуск приложения

```bash
python main.py
```

---

## ⌨️ Горячие клавиши

| Клавиша | Действие |
|---------|----------|
| `Ctrl+U` | 👥 Список пользователей |
| `Ctrl+G` | 🔒 Управление группами |
| `Ctrl+Shift+C` | 📅 Управление календарями |
| `Ctrl+E` | 📤 Экспорт данных |
| `Ctrl+1/2/3` | 🎨 Смена темы |
| `F1` | ❓ Справка |
| `Ctrl+R` | 🔄 Обновить данные |

---

## 📁 Структура проекта

```
admin-team-tools/
├── 📁 src/                    # Исходный код
│   ├── 📁 api/               # API для Google Workspace
│   ├── 📁 ui/                # Пользовательский интерфейс
│   │   ├── 📁 components/    # UI компоненты
│   │   ├── 📁 themes/        # Система тем
│   │   └── 📁 hotkeys/       # Горячие клавиши
│   ├── 📁 utils/             # Утилиты и декораторы
│   └── 📄 auth.py            # Аутентификация
├── 📁 docs/                  # Документация
├── 📁 tests/                 # Тесты
├── 📄 main.py               # Точка входа
├── 📄 requirements.txt      # Зависимости
└── 📄 README.md            # Этот файл
```

---

## 📖 Документация

- 📚 [**Руководство пользователя**](docs/USER_GUIDE.md) - Полное руководство по использованию
- 🔧 [**Руководство разработчика**](docs/DEVELOPER_GUIDE.md) - Для разработчиков
- 🔑 [**Настройка API**](docs/API_SETUP.md) - Настройка Google Workspace API
- 🎨 [**Система тем**](docs/THEMES.md) - Создание кастомных тем
- 📅 [**Управление календарями**](docs/CALENDAR_MANAGEMENT.md) - Работа с календарями

---

## 🔐 Безопасность

### Важные замечания

- 🚨 **Никогда не коммитьте** `credentials.json` в репозиторий
- 🔒 **Используйте переменные окружения** для чувствительных данных
- 🛡️ **Регулярно обновляйте** зависимости
- 📋 **Следуйте принципу минимальных привилегий** при настройке API

### Файлы для исключения

Файл `.gitignore` уже настроен для исключения:
- Файлов аутентификации (`credentials.json`, `token.pickle`)
- Логов и временных файлов
- Конфигурационных файлов с секретами

---

## 🧪 Тестирование

```bash
# Запуск всех тестов
python -m pytest tests/

# Запуск с покрытием
python -m pytest tests/ --cov=src/

# Запуск конкретного теста
python -m pytest tests/test_user_management.py
```

---

## 🤝 Участие в разработке

Мы приветствуем вклад в развитие проекта! 

### Как внести свой вклад

1. **Fork** репозиторий
2. Создайте **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** изменения (`git commit -m 'Add amazing feature'`)
4. **Push** в branch (`git push origin feature/amazing-feature`)
5. Создайте **Pull Request**

### Правила разработки

- ✅ Следуйте **PEP 8** стандартам Python
- 🧪 Добавляйте **тесты** для новой функциональности
- 📝 Обновляйте **документацию** при необходимости
- 🔍 Используйте **типизацию** (type hints)

---

## 📋 Roadmap

### v2.1.0 - Q1 2025
- [ ] 🌐 Веб-интерфейс
- [ ] 📊 Расширенная аналитика
- [ ] 🔔 Push-уведомления
- [ ] 🌍 Поддержка нескольких языков

### v2.2.0 - Q2 2025
- [ ] 🔌 Система плагинов
- [ ] 📱 Мобильное приложение
- [ ] 🤖 Автоматизация задач
- [ ] 📈 Дашборд метрик

---

## 📞 Поддержка

Есть вопросы или нужна помощь?

- 📧 **Email**: support@admin-tools.dev
- 💬 **Telegram**: @admin_tools_support
- 🐛 **Баги**: [GitHub Issues](https://github.com/yourusername/admin-team-tools/issues)
- 💡 **Предложения**: [GitHub Discussions](https://github.com/yourusername/admin-team-tools/discussions)

---

## 📄 Лицензия

Этот проект лицензирован под лицензией MIT - смотрите файл [LICENSE](LICENSE) для деталей.

---

<div align="center">

## 📊 Статистика проекта

<img src="https://img.shields.io/github/stars/yourusername/admin-team-tools?style=social" alt="GitHub stars">
<img src="https://img.shields.io/github/forks/yourusername/admin-team-tools?style=social" alt="GitHub forks">
<img src="https://img.shields.io/github/watchers/yourusername/admin-team-tools?style=social" alt="GitHub watchers">

<img src="https://img.shields.io/github/issues/yourusername/admin-team-tools" alt="GitHub issues">
<img src="https://img.shields.io/github/issues-pr/yourusername/admin-team-tools" alt="GitHub pull requests">
<img src="https://img.shields.io/github/last-commit/yourusername/admin-team-tools" alt="GitHub last commit">

<img src="https://img.shields.io/github/languages/top/yourusername/admin-team-tools" alt="GitHub top language">
<img src="https://img.shields.io/github/languages/count/yourusername/admin-team-tools" alt="GitHub language count">
<img src="https://img.shields.io/github/repo-size/yourusername/admin-team-tools" alt="GitHub repo size">

</div>

---

<div align="center">

### 🎉 **Сделано с ❤️ для администраторов Google Workspace**

<p>
  <a href="https://github.com/yourusername/admin-team-tools/stargazers">
    <img src="https://img.shields.io/badge/⭐-Поставьте%20звезду%20проекту-yellow?style=for-the-badge" alt="Star this repo">
  </a>
</p>

<p>
  <em>Если проект помог вам, поделитесь им с коллегами! 🚀</em>
</p>

<br>

<img src="https://forthebadge.com/images/badges/built-with-love.svg" alt="Built with love">
<img src="https://forthebadge.com/images/badges/made-with-python.svg" alt="Made with Python">
<img src="https://forthebadge.com/images/badges/powered-by-coffee.svg" alt="Powered by coffee">

</div>
