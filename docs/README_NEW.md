# Google Workspace Admin Tools v2.0

🎉 **Новая оптимизированная версия** - Модульное приложение для управления пользователями Google Workspace через Admin SDK Directory API.

## 🆕 Что нового в версии 2.0

- ✅ **Оптимизированная архитектура** - Убрана избыточная сложность
- ✅ **Асинхронная загрузка данных** - Интерфейс не зависает при API запросах  
- ✅ **Улучшенная обработка ошибок** - Понятные сообщения пользователю
- ✅ **Компактный интерфейс** - Размер окна уменьшен до 750x500
- ✅ **Простые утилиты** - Один файл `simple_utils.py` вместо 5 сложных модулей
- ✅ **Меньше зависимостей** - Убраны cryptography и psutil
- ✅ **Принцип KISS** - Keep It Simple, Stupid

## 🚀 Быстрый старт

### Первоначальная настройка GitHub

1. **Создайте репозиторий на GitHub**:
   - Зайдите на https://github.com/Ashushkow
   - Создайте новый репозиторий `google-workspace-admin-tools`
   - НЕ инициализируйте с README, .gitignore или лицензией

2. **Подключите удаленный репозиторий**:
   ```powershell
   cd "c:\Users\sputnik8\Documents\Project"
   $env:PATH += ";C:\Program Files\Git\bin"
   git remote add origin https://github.com/Ashushkow/google-workspace-admin-tools.git
   git push -u origin master
   ```

### Автоматические коммиты

После настройки GitHub используйте один из способов:

**PowerShell:**
```powershell
.\auto_commit.ps1 "Описание изменений"
```

**Command Prompt:**
```cmd
auto_commit.bat "Описание изменений"
```

## 📋 Описание

Это Tkinter-приложение предоставляет графический интерфейс для управления пользователями и группами в Google Workspace. Приложение полностью декомпозировано на отдельные модули для лучшей поддерживаемости и расширяемости.

## ✨ Возможности

- 👥 Просмотр и управление пользователями Google Workspace
- ➕ Создание, редактирование и удаление пользователей
- 👨‍👩‍👧‍👦 Управление группами и членством в группах
- 📊 Экспорт данных в CSV
- 🚀 Кэширование для улучшения производительности
- ⚡ Асинхронная загрузка данных
- 🔍 Расширенная фильтрация и сортировка
- 🎨 Современный пользовательский интерфейс
- 📝 Система логирования

## 🛠️ Установка

1. **Установите Python 3.7 или выше**
2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте аутентификацию Google API:**
   - Создайте проект в Google Cloud Console
   - Включите Admin SDK Directory API
   - Создайте Service Account или OAuth 2.0 credentials
   - Сохраните файл credentials в папке проекта

## 🏃‍♂️ Запуск

```bash
python main.py
```

## 📁 Структура проекта

### Основные модули:
- `main.py` - Точка входа в приложение
- `config.py` - Конфигурация и настройки
- `auth.py` - Аутентификация Google API
- `users_api.py` / `groups_api.py` - API для работы с данными
- `data_cache.py` - Система кэширования
- `ui_components.py` - Переиспользуемые UI компоненты
- `main_window.py` - Главное окно приложения
- `user_windows.py` - Окна управления пользователями
- `employee_list_window.py` - Список сотрудников
- `additional_windows.py` - Дополнительные окна
- `group_management.py` - Управление группами
- `logger.py` - Система логирования

### Автоматизация Git:
- `auto_commit.ps1` - PowerShell скрипт для автокоммитов
- `auto_commit.bat` - Batch скрипт для автокоммитов
- `GIT_WORKFLOW.md` - Подробное руководство по Git workflow
- `setup_github.md` - Инструкции по настройке GitHub

## 📚 Документация

- 📖 [Git Workflow](GIT_WORKFLOW.md) - Руководство по работе с Git
- 🏗️ [Структура проекта](PROJECT_STRUCTURE.md) - Детальная архитектура
- 🔄 [Сводка декомпозиции](DECOMPOSITION_SUMMARY.md) - Процесс модернизации
- 📝 [Модульная документация](README_modular.md) - Техническая документация

## 👨‍💻 Git Configuration

Репозиторий настроен для пользователя **Ashushkow**:
- **GitHub**: https://github.com/Ashushkow
- **Email**: svna95@hotmail.com
- **Автоматические скрипты**: ✅ Настроены

## 🔧 Troubleshooting

### Git не найден:
```powershell
$env:PATH += ";C:\Program Files\Git\bin"
```

### Проблемы с аутентификацией GitHub:
```powershell
git config --global credential.helper manager-core
```

## 📄 Лицензия

MIT License

---

**Разработано для автоматизации управления Google Workspace**  
🚀 *Используйте `auto_commit.ps1` или `auto_commit.bat` для автоматических коммитов!*
