# Git Workflow для Google Workspace Admin Tools

## Текущая конфигурация Git

Репозиторий уже настроен с правильными параметрами пользователя:
- **Имя пользователя**: Ashushkow
- **Email**: svna95@hotmail.com
- **Первоначальный коммит**: Уже создан

## Быстрый старт

### 1. Настройка удаленного репозитория на GitHub

1. Зайдите на https://github.com/Ashushkow
2. Создайте новый репозиторий с именем `google-workspace-admin-tools`
3. НЕ инициализируйте с README, .gitignore или лицензией

### 2. Подключение к удаленному репозиторию

```powershell
# Переход в папку проекта
cd "c:\Users\sputnik8\Documents\Project"

# Добавление Git в PATH
$env:PATH += ";C:\Program Files\Git\bin"

# Добавление удаленного репозитория
git remote add origin https://github.com/Ashushkow/google-workspace-admin-tools.git

# Первоначальная отправка кода
git push -u origin master
```

## Ежедневный workflow

### Вариант 1: Автоматический скрипт (рекомендуется)

```powershell
# Для PowerShell
.\auto_commit.ps1 "Описание изменений"

# Для Command Prompt
auto_commit.bat "Описание изменений"
```

### Вариант 2: Ручные команды

```powershell
# Добавление Git в PATH (если нужно)
$env:PATH += ";C:\Program Files\Git\bin"

# Переход в папку проекта
cd "c:\Users\sputnik8\Documents\Project"

# Проверка статуса
git status

# Добавление всех изменений
git add .

# Создание коммита
git commit -m "Описание изменений"

# Отправка на GitHub
git push
```

## Полезные команды

```powershell
# Проверка истории коммитов
git log --oneline

# Проверка различий
git diff

# Проверка удаленных репозиториев
git remote -v

# Проверка текущих настроек пользователя
git config user.name
git config user.email

# Проверка статуса
git status

# Откат последнего коммита (если нужно)
git reset --soft HEAD~1
```

## Структура проекта

Все файлы в репозитории:
- `main.py` - Основная точка входа
- `config.py` - Конфигурация приложения
- `auth.py` - Аутентификация Google API
- `users_api.py` - API для работы с пользователями
- `groups_api.py` - API для работы с группами
- `data_cache.py` - Кэширование данных
- `ui_components.py` - UI компоненты
- `main_window.py` - Главное окно приложения
- `user_windows.py` - Окна для работы с пользователями
- `employee_list_window.py` - Окно списка сотрудников
- `additional_windows.py` - Дополнительные окна
- `group_management.py` - Управление группами
- `logger.py` - Система логирования
- `requirements.txt` - Зависимости Python
- `.gitignore` - Исключения Git
- Документация: `README.md`, `README_modular.md`, `DECOMPOSITION_SUMMARY.md`, `PROJECT_STRUCTURE.md`

## Автоматизация

Для полной автоматизации можно настроить:

1. **Git hooks** - автоматические действия при коммитах
2. **GitHub Actions** - CI/CD пайплайны
3. **Scheduled tasks** - регулярные автоматические коммиты

## Безопасность

⚠️ **Важно**: Файлы `credentials.json` и `settings.json` содержат конфиденциальную информацию. Убедитесь, что:
- Репозиторий приватный
- Файлы с секретами добавлены в `.gitignore` (если содержат секреты)
- Используете переменные окружения для production

## Troubleshooting

### Проблема: Git не найден
```powershell
# Добавить Git в PATH
$env:PATH += ";C:\Program Files\Git\bin"
```

### Проблема: Ошибка аутентификации GitHub
```powershell
# Настроить Personal Access Token
git config --global credential.helper manager-core
```

### Проблема: Конфликты при merge
```powershell
# Посмотреть конфликты
git status

# Разрешить конфликты в файлах, затем
git add .
git commit -m "Resolve merge conflicts"
```
