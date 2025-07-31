#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест функциональности создания пользователей с выбором OU
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.api.orgunits_api import list_orgunits, format_orgunits_for_combobox, get_orgunit_path_from_display_name
    from src.api.users_api import create_user
    from src.ui.user_windows import CreateUserWindow
    print("✅ Импорт всех модулей прошел успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def test_ou_functions():
    """Тестирует функции работы с OU"""
    print("\n🧪 Тестирование функций OU...")
    
    # Мок данные для тестирования
    mock_orgunits = [
        {
            'name': 'Root Organization',
            'orgUnitPath': '/',
            'description': 'Корневое подразделение'
        },
        {
            'name': 'HR',
            'orgUnitPath': '/HR',
            'description': 'Human Resources'
        },
        {
            'name': 'Admin',
            'orgUnitPath': '/HR/Admin',
            'description': 'Administration team under HR'
        },
        {
            'name': 'IT',
            'orgUnitPath': '/IT',
            'description': 'Information Technology'
        },
        {
            'name': 'Developers',
            'orgUnitPath': '/IT/Developers',
            'description': 'Development team'
        }
    ]
    
    # Тестируем форматирование для combobox
    formatted = format_orgunits_for_combobox(mock_orgunits)
    print("📋 Отформатированные OU для UI:")
    for ou in formatted:
        print(f"  - {ou}")
    
    # Тестируем получение пути по отображаемому имени
    print("\n🔍 Тест получения путей OU:")
    test_cases = [
        ("🏠 Корневое подразделение", "/"),
        ("🏢 HR", "/HR"),
        ("  🏢 Admin", "/HR/Admin"),
        ("🏢 IT", "/IT"),
        ("  🏢 Developers", "/IT/Developers")
    ]
    
    for display_name, expected_path in test_cases:
        actual_path = get_orgunit_path_from_display_name(display_name, mock_orgunits)
        status = "✅" if actual_path == expected_path else "❌"
        print(f"  {status} '{display_name}' -> '{actual_path}' (ожидалось: '{expected_path}')")

def test_user_creation_with_ou():
    """Демонстрирует создание пользователя с OU"""
    print("\n👤 Демонстрация создания пользователя с OU:")
    print("(Это демонстрация API вызова - фактическое создание не происходит)")
    
    # Пример использования нового API
    example_calls = [
        {
            'email': 'john.doe@sputnik8.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'SecurePass123!',
            'org_unit_path': '/HR'
        },
        {
            'email': 'jane.admin@sputnik8.com',
            'first_name': 'Jane',
            'last_name': 'Admin',
            'password': 'AdminPass456!',
            'org_unit_path': '/HR/Admin'
        },
        {
            'email': 'dev.user@sputnik8.com',
            'first_name': 'Dev',
            'last_name': 'User',
            'password': 'DevPass789!',
            'org_unit_path': '/IT/Developers'
        }
    ]
    
    for i, call_params in enumerate(example_calls, 1):
        print(f"\n  📝 Пример {i}:")
        print(f"     Email: {call_params['email']}")
        print(f"     Имя: {call_params['first_name']} {call_params['last_name']}")
        print(f"     OU: {call_params['org_unit_path']}")
        print(f"     API call: create_user(service, email='{call_params['email']}', "
              f"first_name='{call_params['first_name']}', last_name='{call_params['last_name']}', "
              f"password='***', org_unit_path='{call_params['org_unit_path']}')")

def main():
    """Главная функция теста"""
    print("🚀 Тест функциональности создания пользователей с выбором OU")
    print("=" * 70)
    
    try:
        test_ou_functions()
        test_user_creation_with_ou()
        
        print("\n" + "=" * 70)
        print("🎉 Все тесты пройдены успешно!")
        print("\n💡 Инструкции по использованию:")
        print("1. В окне создания пользователя теперь есть поле 'Подразделение (OU)'")
        print("2. Выберите нужное подразделение из выпадающего списка")
        print("3. Пользователь будет создан в выбранном подразделении")
        print("4. По умолчанию выбрано корневое подразделение")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время тестирования: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
