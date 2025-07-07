# Настройка GitHub репозитория

## Шаги для настройки удаленного репозитория:

1. Войдите в GitHub под аккаунтом Ashushkow (https://github.com/Ashushkow)
2. Создайте новый репозиторий с именем `google-workspace-admin-tools`
3. НЕ инициализируйте с README, .gitignore или лицензией (у нас уже есть эти файлы)

## Команды для подключения удаленного репозитория:

```powershell
# Переход в папку проекта
cd "c:\Users\sputnik8\Documents\Project"

# Добавление Git в PATH (если нужно)
$env:PATH += ";C:\Program Files\Git\bin"

# Добавление удаленного репозитория
git remote add origin https://github.com/Ashushkow/google-workspace-admin-tools.git

# Отправка кода в удаленный репозиторий
git push -u origin master
```

## Автоматические коммиты и пуши

После настройки удаленного репозитория вы сможете использовать:

```powershell
# Добавить все изменения
git add .

# Сделать коммит
git commit -m "Описание изменений"

# Отправить на GitHub
git push
```
