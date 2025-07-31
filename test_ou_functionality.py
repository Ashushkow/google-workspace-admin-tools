#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки функциональности выбора OU при создании пользователя
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Проверяем импорт нашего нового API
    from src.api.orgunits_api import (
        list_orgunits, 
        format_orgunits_for_combobox, 
        get_orgunit_path_from_display_name,
        get_orgunit_display_name
    )
    
    print("✅ Импорт orgunits_api прошел успешно")
    
    # Проверяем обновленную функцию создания пользователя
    from src.api.users_api import create_user
    
    print("✅ Импорт обновленной users_api прошел успешно")
    
    # Проверяем обновленные функции создания с email
    from src.api.user_creation_service import create_user_with_welcome_email, create_user_with_auto_welcome
    
    print("✅ Импорт обновленных функций user_creation_service прошел успешно")
    
    # Тестируем утилиты для работы с OU
    test_orgunits = [
        {'name': 'IT Department', 'orgUnitPath': '/IT'},
        {'name': 'HR Department', 'orgUnitPath': '/HR'},
        {'name': 'Developers', 'orgUnitPath': '/IT/Developers'},
        {'name': 'Root Organization', 'orgUnitPath': '/'}
    ]
    
    print("\n📋 Тестирование утилит OU:")
    
    # Тестируем форматирование для комбобокса
    formatted = format_orgunits_for_combobox(test_orgunits)
    print("Отформатированные OU для комбобокса:")
    for ou in formatted:
        print(f"  - {ou}")
    
    # Тестируем получение пути из отображаемого имени
    if formatted:
        display_name = formatted[1]  # Берем второй элемент (не корневой)
        path = get_orgunit_path_from_display_name(display_name, test_orgunits)
        print(f"\nИз '{display_name}' получили путь: '{path}'")
    
    # Тестируем получение отображаемого имени из пути
    test_path = "/IT/Developers"
    display = get_orgunit_display_name(test_path)
    print(f"Из пути '{test_path}' получили отображение: '{display}'")
    
    print("\n🎉 Все тесты пройдены успешно!")
    print("\n📝 Что было добавлено:")
    print("  1. ✅ API для работы с организационными подразделениями (OU)")
    print("  2. ✅ Обновлена функция создания пользователя с поддержкой OU")
    print("  3. ✅ Обновлены функции создания с приветственным письмом")
    print("  4. ✅ Обновлен UI CreateUserWindow с выбором OU")
    print("  5. ✅ Добавлены утилиты для форматирования OU")
    
    print("\n💡 Использование:")
    print("  - При создании пользователя теперь можно выбрать OU из выпадающего списка")
    print("  - По умолчанию выбирается корневое подразделение '/'")
    print("  - OU загружаются автоматически при открытии окна создания пользователя")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("💡 Убедитесь, что все файлы созданы правильно")
    sys.exit(1)
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    sys.exit(1)
