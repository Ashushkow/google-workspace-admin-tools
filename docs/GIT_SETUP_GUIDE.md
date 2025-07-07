# Git Setup Guide для Google Workspace Admin Tools v2.0.3

## 1. Установка Git

### Загрузка и установка:
1. Перейдите на https://git-scm.com/download/win
2. Скачайте Git для Windows (64-bit Git for Windows Setup)
3. Запустите установщик с правами администратора
4. В процессе установки рекомендуется:
   - Выбрать "Use Git from the Windows Command Prompt"
   - Выбрать "Checkout Windows-style, commit Unix-style line endings"
   - Выбрать "Use Windows' default console window"

### Проверка установки:
Откройте PowerShell и выполните:
```powershell
git --version
```

## 2. Первоначальная настройка Git

```powershell
# Настройка имени пользователя и email
git config --global user.name "Ваше Имя"
git config --global user.email "your.email@example.com"

# Настройка редактора по умолчанию (необязательно)
git config --global core.editor "notepad"

# Проверка настроек
git config --list
```

## 3. Создание репозитория на GitHub

1. Зайдите на https://github.com
2. Нажмите "New repository"
3. Название: `google-workspace-admin-tools`
4. Описание: `Google Workspace Admin SDK Directory API Management Tool v2.0.3`
5. Выберите Public или Private
6. НЕ инициализируйте с README (у нас уже есть файлы)
7. Нажмите "Create repository"

## 4. Инициализация локального репозитория

Выполните команды в папке проекта:

```powershell
# Перейти в папку проекта
cd "C:\Users\sputnik8\Documents\Project"

# Инициализировать git репозиторий
git init

# Добавить удаленный репозиторий (замените на свой URL)
git remote add origin https://github.com/YOUR_USERNAME/google-workspace-admin-tools.git

# Проверить настройку remote
git remote -v
```

## 5. Подготовка файлов к коммиту

```powershell
# Создать .gitignore (если еще не создан)
# Содержимое .gitignore уже подготовлено в проекте

# Добавить все файлы
git add .

# Проверить статус
git status

# Создать первый коммит
git commit -m "Initial commit: Google Workspace Admin Tools v2.0.3

- Refactored monolithic main.py into modular structure
- Organized code into src/api, src/ui, src/utils directories
- Fixed all imports to use relative imports
- Added comprehensive documentation and tests
- Prepared release v2.0.3 with full functionality

Features:
- Google Workspace Admin SDK integration
- User management (list, create, update, delete)
- Group management with member operations
- Modern Tkinter GUI with theming
- Comprehensive error handling and logging
- Security audit and monitoring
- Async operations support
- Configuration management
- Data caching system

Tech stack: Python 3.12, Google Admin SDK, Tkinter, Custom Auth"
```

## 6. Создание и отправка тегов

```powershell
# Создать тег для версии
git tag -a v2.0.3 -m "Release v2.0.3: Modular Architecture with Full Google Admin SDK Integration

Major refactoring:
- Split monolithic main.py (952 lines) into 48-line entry point
- Created modular structure: src/api, src/ui, src/utils
- Fixed all relative imports
- Added comprehensive documentation
- Full test coverage
- Security enhancements

New features:
- Enhanced group management
- Improved error handling
- Modern UI components
- Advanced caching system
- Monitoring and audit logging

Breaking changes: None (backward compatible)
Migration: Automatic import resolution"

# Отправить код в репозиторий
git push -u origin main

# Отправить теги
git push origin --tags
```

## 7. Создание Release на GitHub

1. Перейдите в ваш репозиторий на GitHub
2. Нажмите "Releases" → "Create a new release"
3. Выберите тег `v2.0.3`
4. Заголовок: `v2.0.3 - Modular Architecture Release`
5. Описание: Скопируйте из `docs/releases/RELEASE_NOTES_v2.0.3.md`
6. Прикрепите файлы (если нужно):
   - `requirements.txt`
   - `setup_github.md`
   - `READY_TO_USE.md`
7. Нажмите "Publish release"

## 8. Альтернативный способ: Автоматический релиз

Если Git установлен, можете использовать подготовленные скрипты:

```powershell
# PowerShell скрипт (рекомендуется)
.\scripts\release_v2.0.3.ps1

# Или Python скрипт
python scripts\release_v2.0.3.py

# Или batch файл
.\scripts\release_v2.0.3.bat
```

## 9. Дальнейшее развитие

После успешной публикации:

1. Склонируйте репозиторий в другое место для тестирования:
```powershell
git clone https://github.com/YOUR_USERNAME/google-workspace-admin-tools.git test_clone
cd test_clone
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# Настройте credentials.json
python main.py
```

2. Создайте ветки для дальнейшей разработки:
```powershell
git checkout -b feature/new-feature
git checkout -b hotfix/bug-fix
```

3. Настройте CI/CD (GitHub Actions) для автоматического тестирования

## Устранение проблем

### Проблемы с аутентификацией:
```powershell
# Использование Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/google-workspace-admin-tools.git
```

### Проблемы с large files:
```powershell
# Если файлы слишком большие, используйте Git LFS
git lfs track "*.json"
git lfs track "*.pickle"
```

### Проблемы с line endings:
```powershell
git config core.autocrlf true
```

## Контакты и поддержка

Документация проекта: `docs/`
Изменения версии: `docs/CHANGELOG.md`
Структура проекта: `docs/FOLDER_STRUCTURE_v2.0.2.md`
Статус релиза: `docs/RELEASE_v2.0.3_READY_FOR_GIT.md`
