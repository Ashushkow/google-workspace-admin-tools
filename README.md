<div align="center">

# 🚀 Admin Team Tools

### Профессиональное приложение для управления Google Workspace

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.7-brightgreen.svg)](https://github.com/Ashushkow/admin-team-tools/releases)
[![Tests](https://img.shields.io/badge/tests-6%2F6%20passing-success.svg)](#testing)

**Современное решение для администрирования пользователей, групп и календарей Google Workspace**

[🚀 Быстрый старт](#-быстрый-старт) • 
[📖 Документация](#-документация) • 
[✨ Возможности](#-возможности) • 
[🛠️ API](#️-api-и-интеграции) • 
[🤝 Участие](#-участие-в-разработке)

![Demo](https://via.placeholder.com/800x400/1a1a1a/ffffff?text=Admin+Team+Tools+Demo)

*Интуитивный интерфейс для управления Google Workspace*

</div>

---

## 🎯 Что это?

**Admin Team Tools** — это мощное desktop-приложение с графическим интерфейсом для управления Google Workspace. Приложение предоставляет удобные инструменты для администраторов, позволяя эффективно управлять пользователями, группами и календарями организации.

### 🔑 Ключевые особенности:

- 🔐 **Безопасная OAuth 2.0 авторизация** — интерактивная аутентификация через браузер
- 🎨 **Современный GUI интерфейс** — удобное управление через графический интерфейс
- ⚡ **Высокая производительность** — асинхронная архитектура и кэширование
- 🛡️ **Надежность** — полное логирование действий и обработка ошибок
- 🔄 **Автоматизация** — массовые операции и пакетная обработка
- 📁 **Организованная структура** — автоматическое размещение файлов в правильных директориях

---

## ✨ Возможности

<table>
<tr>
<td width="50%">

### 👥 **Управление пользователями**
- ✅ Создание новых пользователей
- ✅ Редактирование профилей и настроек
- ✅ Управление паролями и доступом
- ✅ Массовые операции
- ✅ Экспорт данных в Excel/CSV

### 🔒 **Управление группами**
- ✅ Создание и настройка групп
- ✅ Управление участниками
- ✅ Настройка прав доступа
- ✅ Синхронизация с Google Directory

</td>
<td width="50%">

### 📅 **Управление календарями**
- ✅ Создание общих календарей
- ✅ Настройка доступа для групп
- ✅ Управление событиями
- ✅ Синхронизация расписаний
- 🎯 **Специальный календарь SPUTNIK (общий)**

### 🎯 **Календарь SPUTNIK** *(NEW v2.0.7)*
- ✅ Прямое управление участниками
- ✅ Массовое добавление/удаление
- ✅ Изменение ролей доступа
- ✅ Статистика и аналитика

### 📊 **Аналитика и отчеты**
- ✅ Статистика использования
- ✅ Аудит действий пользователей
- ✅ Экспорт отчетов
- ✅ Мониторинг активности

</td>
</tr>
</table>

---

## 🚀 Быстрый старт

### 📋 Требования

- **Python 3.8+** (рекомендуется 3.11+)
- **Google Workspace** аккаунт с правами администратора
- **Google Cloud Project** с включенным Admin SDK API

### ⚡ Установка и настройка

#### 1️⃣ Клонирование репозитория
```bash
git clone https://github.com/Ashushkow/admin-team-tools.git
cd admin-team-tools
```

#### 2️⃣ Настройка окружения
```bash
# Создание виртуального окружения
python -m venv .venv

# Активация (Windows)
.venv\Scripts\activate

# Активация (Linux/Mac)
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

#### 3️⃣ Настройка Google API

1. **Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)**
2. **Включите Admin SDK API:**
   - Перейдите в "APIs & Services" → "Library"
   - Найдите "Admin SDK API" и включите его
3. **Создайте OAuth 2.0 credentials:**
   - Перейдите в "APIs & Services" → "Credentials"
   - Нажмите "Create Credentials" → "OAuth 2.0 Client ID"
   - Выберите "Desktop Application"
   - Скачайте JSON файл и переименуйте в `credentials.json`
4. **Поместите файл в корневую папку проекта**

#### 4️⃣ Конфигурация приложения
```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env файл под ваши нужды
# Основные настройки:
# GOOGLE_WORKSPACE_DOMAIN=yourdomain.com
# GOOGLE_WORKSPACE_ADMIN=admin@yourdomain.com
```

#### 5️⃣ Первый запуск
```bash
# Тестирование подключения
python tests/manual/test_oauth.py

# Запуск приложения
python main.py
```

> � **При первом запуске** откроется браузер для авторизации в Google Workspace

---

## 🛠️ API и интеграции

### 🔐 Поддерживаемые методы авторизации

| Метод | Описание | Рекомендуется для |
|-------|----------|-------------------|
| **OAuth 2.0** 🥇 | Интерактивная авторизация через браузер | Desktop приложения, разработка |
| **Service Account** 🥈 | Серверная авторизация без пользователя | Автоматизация, CI/CD |

### 📡 Google Workspace APIs

- **Admin Directory API** — управление пользователями и группами
- **Calendar API** — управление календарями и событиями
- **Reports API** — получение отчетов об активности
- **Groups Settings API** — расширенные настройки групп

---

## 🏗️ Архитектура

### 📁 Структура проекта
```
admin-team-tools/
├── 📱 main.py                    # Точка входа
├── 📦 requirements.txt           # Зависимости
├── ⚙️ pyproject.toml            # Конфигурация проекта
├── 🐳 Dockerfile               # Контейнеризация
│
├── 💻 src/                      # Исходный код
│   ├── 🎯 core/                 # Основная логика
│   ├── 🔧 services/             # Бизнес-логика
│   ├── 💾 repositories/         # Доступ к данным
│   ├── 🌐 api/                  # API клиенты
│   ├── 🎨 ui/                   # Пользовательский интерфейс
│   └── 🛠️ utils/               # Утилиты
│
├── 🧪 tests/                    # Тестирование
│   ├── 🔄 manual/               # Ручные тесты
│   └── 🤖 (автоматические)      # Юнит/интеграционные тесты
│
├── 📚 docs/                     # Документация
├── 🔧 scripts/                  # Утилитарные скрипты
├── 📦 archive/                  # Архивные файлы
└── 🏗️ build/                   # Артефакты сборки
```

### 🎯 Принципы архитектуры

- **Clean Architecture** — четкое разделение слоев
- **Dependency Injection** — инверсия управления зависимостями
- **Repository Pattern** — абстракция доступа к данным
- **Async/Await** — асинхронная обработка запросов

### 📁 Автоматическая организация файлов

Приложение автоматически размещает создаваемые файлы в правильных директориях:

```
📦 Project/
├── 📁 logs/                     # Файлы логирования
│   ├── admin_tools.log          # Основные логи
│   ├── errors.log               # Логи ошибок
│   └── security_audit.json      # Аудит безопасности
├── 📁 data/                     # Данные приложения
│   ├── 📁 exports/              # Экспортированные файлы
│   │   ├── users_export.csv     # Экспорт пользователей
│   │   └── calendar_members.xlsx # Экспорт участников календаря
│   ├── 📁 reports/              # Отчеты и аналитика
│   └── 📁 security/             # Файлы безопасности
├── 📁 config/                   # Конфигурационные файлы
│   ├── 📁 themes/               # Настройки тем
│   ├── app_config.json          # Основная конфигурация
│   └── theme_config.json        # Настройки внешнего вида
├── 📁 temp/                     # Временные файлы
├── 📁 cache/                    # Кэш файлы
└── 📁 tests/                    # Тестовые файлы и данные
    ├── 📁 data/                 # Тестовые данные
    └── 📁 logs/                 # Тестовые логи
```

**Преимущества:**
- 🎯 **Автоматическое размещение** — файлы сами попадают в нужные места
- 🧹 **Чистая структура** — корневая директория не засоряется
- 🔧 **Легкое обслуживание** — простой поиск и управление файлами
- 🗂️ **Логическая группировка** — связанные файлы в одной папке
---

## 🧪 Тестирование

### ⚡ Быстрое тестирование
```bash
# Запуск всех автоматических тестов
pytest tests/ -v

# Тестирование с покрытием кода
pytest tests/ --cov=src --cov-report=html

# Проверка OAuth подключения
python tests/manual/test_oauth.py
```

### � Результаты тестов
- ✅ **6/6 автоматических тестов** проходят успешно
- ✅ **19 ручных тестов** для отладки и проверки
- ✅ **Покрытие кода**: базовые компоненты протестированы
- ✅ **Интеграционные тесты** с Google API

---

## 🐳 Контейнеризация

### Docker развертывание
```bash
# Сборка образа
docker build -t admin-team-tools .

# Запуск контейнера
docker run -it --rm \
  -v $(pwd)/credentials.json:/app/credentials.json \
  -v $(pwd)/config:/app/config \
  admin-team-tools
```

### Docker Compose
```bash
# Запуск через docker-compose
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

---

## 📚 Документация

### 🗂️ Доступная документация

| Документ | Описание |
|----------|----------|
| [📋 API Setup](docs/API_SETUP.md) | Настройка Google Cloud Console |
| [🔐 OAuth2 Setup](docs/OAUTH2_PRIORITY_SETUP.md) | Быстрая настройка OAuth 2.0 |
| [👥 User Guide](docs/USER_GUIDE.md) | Руководство пользователя |
| [🔧 Troubleshooting](docs/OAUTH2_TROUBLESHOOTING.md) | Решение проблем |
| [🛡️ Security](docs/SECURITY.md) | Вопросы безопасности |
| [� Changelog](docs/CHANGELOG.md) | История изменений |

### 📖 Дополнительные ресурсы
- [Google Workspace Admin SDK](https://developers.google.com/admin-sdk)
- [OAuth 2.0 для Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Python Google API Client](https://github.com/googleapis/google-api-python-client)

---

## 🔧 Разработка

### 🛠️ Настройка среды разработки
```bash
# Установка dev зависимостей
pip install -e ".[dev]"

# Настройка pre-commit hooks
pre-commit install

# Запуск линтеров
black src tests
flake8 src tests
mypy src
```

### 🏗️ Сборка проекта
```bash
# Сборка пакета
python -m build

# Создание исполняемого файла
python scripts/build_release.py

# Сборка через Nuitka (оптимизированная)
python scripts/build_nuitka.py
```

### 📋 Полезные команды
```bash
# Проверка настройки окружения
python scripts/check_setup.py

# Очистка кэша и временных файлов
python scripts/clean_build.py

# Обновление зависимостей
pip-compile requirements.in
```

---

## 🤝 Участие в разработке

Мы приветствуем участие в развитии проекта! 🎉

### 📝 Как внести свой вклад

1. **🍴 Fork** репозиторий
2. **🌿 Создайте** ветку для функции (`git checkout -b feature/amazing-feature`)
3. **💻 Внесите** изменения с соблюдением стандартов кода
4. **✅ Добавьте** тесты для новой функциональности
5. **📝 Обновите** документацию при необходимости
6. **� Создайте** Pull Request

### 📋 Правила разработки

- ✅ Следуйте **PEP 8** стандартам Python
- 🧪 Добавляйте **тесты** для новой функциональности
- 📝 Обновляйте **документацию** при изменениях
- 🔍 Используйте **типизацию** (type hints)
- 📊 Поддерживайте **покрытие тестами**

### 🐛 Сообщение об ошибках

Нашли баг? [Создайте issue](https://github.com/Ashushkow/admin-team-tools/issues/new) с описанием:
- Шаги для воспроизведения
- Ожидаемое поведение
- Фактическое поведение
- Информация о системе (ОС, Python версия)

---

## � Статистика проекта

<div align="center">

| Метрика | Значение |
|---------|----------|
| 📝 Строк кода | ~5000+ |
| 🧪 Тестов | 25+ |
| 📚 Документов | 12+ |
| 🔧 Скриптов | 8+ |
| 📦 Зависимостей | 15+ |
| 🏷️ Версия | 2.0.7 |

</div>

---

## � Лицензия

Этот проект распространяется под лицензией **MIT License**.

```
MIT License

Copyright (c) 2025 Admin Team Tools

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

Полный текст лицензии: [LICENSE](LICENSE)

---

## 🔗 Ссылки и контакты

<div align="center">

### 🌐 Проект в интернете

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/Ashushkow/admin-team-tools)
[![Issues](https://img.shields.io/badge/Issues-Report%20Bug-red?style=for-the-badge&logo=github)](https://github.com/Ashushkow/admin-team-tools/issues)
[![Releases](https://img.shields.io/badge/Releases-Download-green?style=for-the-badge&logo=github)](https://github.com/Ashushkow/admin-team-tools/releases)

### 📞 Поддержка

Есть вопросы? Обращайтесь:
- 📧 Email: [admin@example.com](mailto:admin@example.com)
- 💬 GitHub Issues: [Задать вопрос](https://github.com/Ashushkow/admin-team-tools/issues)
- 📚 Wiki: [Документация проекта](https://github.com/Ashushkow/admin-team-tools/wiki)

</div>

---

<div align="center">

### 🎉 Спасибо за использование Admin Team Tools!

**Создано с ❤️ для администраторов Google Workspace**

⭐ Если проект оказался полезным, поставьте звездочку на GitHub!

</div>
