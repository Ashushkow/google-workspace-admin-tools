# Manual Tests Directory

Эта папка содержит ручные тестовые скрипты для отладки и проверки функциональности.

## Категории тестов:

### OAuth и аутентификация:
- `test_oauth.py` - Базовый тест OAuth авторизации
- `test_oauth2_debug.py` - Отладочные тесты OAuth2
- `test_oauth2_direct.py` - Прямые тесты OAuth2
- `test_oauth_fix.py` - Тесты исправлений OAuth
- `test_oauth_users.py` - Тесты пользователей через OAuth
- `test_real_oauth2.py` - Тесты с реальным OAuth2
- `test_domains_oauth.py` - Тесты доменов OAuth

### Пользователи и группы:
- `test_all_users.py` - Тест всех пользователей
- `test_employee_list.py` - Тест списка сотрудников
- `test_final_groups.py` - Финальные тесты групп
- `test_groups_loading.py` - Тесты загрузки групп
- `test_statistics_groups.py` - Тесты статистики групп

### UI и интерфейс:
- `test_group_window.py` - Тест окна групп
- `test_ui_groups_fix.py` - Тесты исправлений UI групп
- `test_ui_groups_fix2.py` - Дополнительные тесты UI групп

### API и интеграция:
- `test_new_api.py` - Тесты нового API
- `test_new_config.py` - Тесты новой конфигурации
- `test_final_solution.py` - Тесты финального решения
- `test_repository.py` - Тесты репозитория

## Использование:

Запускайте тесты из корневой папки проекта:

```bash
python tests/manual/test_oauth.py
python tests/manual/test_all_users.py
```

## Примечание:

Эти тесты предназначены для ручного запуска и отладки.
Для автоматического тестирования используйте основные тесты в папке `tests/`.
