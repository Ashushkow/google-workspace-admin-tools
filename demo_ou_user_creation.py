#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация создания пользователей в различных OU
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def demo_ou_user_creation():
    """Демонстрирует создание пользователей в различных OU"""
    print("🏢 Демонстрация создания пользователей в различных организационных подразделениях")
    print("=" * 80)
    
    examples = [
        {
            'scenario': 'Создание HR менеджера в подразделении HR',
            'user': {
                'email': 'hr.manager@sputnik8.com',
                'first_name': 'Anna',
                'last_name': 'HRManager',
                'org_unit_path': '/HR'
            }
        },
        {
            'scenario': 'Создание администратора в подразделении HR/Admin',
            'user': {
                'email': 'admin.user@sputnik8.com',
                'first_name': 'Alex',
                'last_name': 'Administrator',
                'org_unit_path': '/HR/Admin'
            }
        },
        {
            'scenario': 'Создание разработчика в подразделении IT/Developers',
            'user': {
                'email': 'dev.user@sputnik8.com',
                'first_name': 'John',
                'last_name': 'Developer',
                'org_unit_path': '/IT/Developers'
            }
        },
        {
            'scenario': 'Создание пользователя в корневом подразделении (по умолчанию)',
            'user': {
                'email': 'general.user@sputnik8.com',
                'first_name': 'Maria',
                'last_name': 'Generalova',
                'org_unit_path': '/'
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📝 Пример {i}: {example['scenario']}")
        print("-" * 60)
        
        user = example['user']
        print(f"👤 Имя: {user['first_name']} {user['last_name']}")
        print(f"📧 Email: {user['email']}")
        print(f"🏢 Подразделение: {user['org_unit_path']}")
        
        print(f"\n💻 Код для создания:")
        print(f"```python")
        print(f"from src.api.users_api import create_user")
        print(f"")
        print(f"result = create_user(")
        print(f"    service=google_service,")
        print(f"    email='{user['email']}',")
        print(f"    first_name='{user['first_name']}',")
        print(f"    last_name='{user['last_name']}',")
        print(f"    password='SecurePassword123!',")
        print(f"    org_unit_path='{user['org_unit_path']}'")
        print(f")")
        print(f"```")
    
    print("\n" + "=" * 80)
    print("🎯 Преимущества использования OU:")
    print("• Лучшая организация пользователей по отделам")
    print("• Упрощение управления правами и политиками")
    print("• Возможность применения настроек к группам пользователей")
    print("• Более структурированная иерархия организации")
    
    print("\n🛡️ Требования для работы с OU:")
    print("• Включен Admin SDK API в Google Cloud Console")
    print("• Service Account имеет права на чтение OU")
    print("• Добавлен scope: https://www.googleapis.com/auth/admin.directory.orgunit")

def demo_ui_usage():
    """Демонстрирует использование через UI"""
    print("\n" + "=" * 80)
    print("🖥️ Использование через пользовательский интерфейс")
    print("=" * 80)
    
    steps = [
        "1. Запустите приложение Admin Team Tools",
        "2. Нажмите кнопку '➕ Создать пользователя'",
        "3. Заполните обязательные поля:",
        "   • First Name (Имя)",
        "   • Last Name (Фамилия)", 
        "   • Password (Пароль)",
        "4. 🆕 Выберите подразделение из списка 'Подразделение (OU):'",
        "   • По умолчанию выбрано корневое подразделение",
        "   • Список загружается автоматически из Google Workspace",
        "5. При необходимости заполните дополнительные поля:",
        "   • Secondary Email",
        "   • Phone Number",
        "6. Нажмите кнопку '➕ Создать'",
        "7. Пользователь будет создан в выбранном подразделении"
    ]
    
    for step in steps:
        print(step)
    
    print(f"\n💡 Примеры подразделений в списке:")
    print(f"• 🏠 Корневое подразделение")
    print(f"• 🏢 HR")
    print(f"•   🏢 Admin")
    print(f"• 🏢 IT")
    print(f"•   🏢 Developers")

def main():
    """Главная функция"""
    demo_ou_user_creation()
    demo_ui_usage()
    
    print("\n" + "=" * 80)
    print("✅ Функциональность создания пользователей с выбором OU готова к использованию!")

if __name__ == "__main__":
    main()
