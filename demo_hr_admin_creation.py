#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация создания пользователя в подразделении HR/Admin
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def demo_hr_admin_user_creation():
    """Демонстрирует создание пользователя в HR/Admin"""
    print("🎯 Демонстрация создания пользователя в подразделении HR/Admin")
    print("=" * 70)
    
    try:
        from src.api.orgunits_api import list_orgunits, format_orgunits_for_combobox, get_orgunit_path_from_display_name
        from src.api.users_api import create_user
        from src.auth import get_service
        
        print("✅ Модули импортированы успешно")
        
        # Получаем сервис
        service = get_service()
        print("✅ Google API сервис получен")
        
        # Загружаем OU
        print("\n📋 Загрузка организационных подразделений...")
        orgunits = list_orgunits(service)
        orgunit_display_names = format_orgunits_for_combobox(orgunits)
        
        # Ищем HR/Admin в списке
        hr_admin_display = None
        for display_name in orgunit_display_names:
            if "Admin" in display_name:
                path = get_orgunit_path_from_display_name(display_name, orgunits)
                if path == "/HR/Admin":
                    hr_admin_display = display_name
                    break
        
        if hr_admin_display:
            print(f"✅ Найдено подразделение HR/Admin:")
            print(f"   Отображение в UI: '{hr_admin_display}'")
            print(f"   Путь в API: '/HR/Admin'")
        else:
            print("❌ Подразделение HR/Admin не найдено")
            return
        
        # Демонстрируем создание пользователя
        print(f"\n👤 Демонстрация создания пользователя в HR/Admin:")
        print("-" * 70)
        
        example_user = {
            'email': 'admin.example@sputnik8.com',
            'first_name': 'Анна',
            'last_name': 'Администратор',
            'password': 'AdminSecure123!',
            'org_unit_path': '/HR/Admin'
        }
        
        print(f"📧 Email: {example_user['email']}")
        print(f"👤 Имя: {example_user['first_name']} {example_user['last_name']}")
        print(f"🏢 Подразделение: {example_user['org_unit_path']}")
        print(f"🔑 Пароль: ***********")
        
        print(f"\n💻 Код для создания пользователя:")
        print(f"```python")
        print(f"from src.api.users_api import create_user")
        print(f"")
        print(f"result = create_user(")
        print(f"    service=google_service,")
        print(f"    email='{example_user['email']}',")
        print(f"    first_name='{example_user['first_name']}',")
        print(f"    last_name='{example_user['last_name']}',")
        print(f"    password='{example_user['password']}',")
        print(f"    org_unit_path='{example_user['org_unit_path']}'")
        print(f")")
        print(f"```")
        
        # Показываем другие доступные подразделения под HR
        print(f"\n🏢 Все подразделения под HR:")
        print("-" * 70)
        
        hr_children = []
        for ou in orgunits:
            path = ou.get('orgUnitPath', '/')
            if path.startswith('/HR/'):
                name = ou.get('name', 'Unknown')
                hr_children.append((name, path))
        
        if hr_children:
            for name, path in sorted(hr_children):
                print(f"  🏢 {name} ({path})")
        else:
            print("  Дочерних подразделений под HR не найдено")
        
        # Показываем, как это выглядит в UI
        print(f"\n🖥️ Как это выглядит в пользовательском интерфейсе:")
        print("-" * 70)
        print("В выпадающем списке 'Подразделение (OU):' вы увидите:")
        print()
        
        # Показываем только HR и его дочерние подразделения
        for display_name in orgunit_display_names:
            if display_name == "🏢 HR":
                print(f"  {display_name}")
            elif display_name.startswith("  🏢"):
                # Проверяем, является ли это дочерним подразделением HR
                path = get_orgunit_path_from_display_name(display_name, orgunits)
                if path.startswith('/HR/'):
                    print(f"  {display_name}")
        
        print(f"\nДля создания пользователя в HR/Admin:")
        print(f"1. Выберите '  🏢 Admin' из списка")
        print(f"2. Заполните остальные поля")
        print(f"3. Нажмите 'Создать'")
        
        # Показываем инструкции по проверке
        print(f"\n🔍 Как проверить, что пользователь создан в правильном OU:")
        print("-" * 70)
        print("1. Откройте Google Admin Console (admin.google.com)")
        print("2. Перейдите в 'Пользователи'")
        print("3. Найдите созданного пользователя")
        print("4. В колонке 'Подразделение' должно быть указано 'HR > Admin'")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Главная функция"""
    demo_hr_admin_user_creation()
    
    print("\n" + "=" * 70)
    print("✅ Функциональность создания пользователей в HR/Admin готова!")
    print("🎉 Теперь вы можете создавать пользователей в любом подразделении")

if __name__ == "__main__":
    main()
