#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест UI функциональности создания пользователей с выбором OU
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_ui_ou_functionality():
    """Тестирует UI функциональность выбора OU"""
    print("🖥️ Тест UI функциональности выбора организационных подразделений")
    print("=" * 80)
    
    try:
        # Импортируем необходимые модули
        from src.api.orgunits_api import list_orgunits, format_orgunits_for_combobox, get_orgunit_path_from_display_name
        from src.auth import get_service
        
        print("✅ Модули импортированы успешно")
        
        # Симулируем получение сервиса (как в UI)
        print("🔑 Получение Google API сервиса...")
        service = get_service()
        print("✅ Сервис получен")
        
        # Симулируем загрузку OU (как в CreateUserWindow.__init__)
        print("\n📋 Загрузка OU для UI...")
        orgunits = list_orgunits(service)
        orgunit_display_names = format_orgunits_for_combobox(orgunits)
        
        print(f"📊 Загружено {len(orgunits)} OU")
        print(f"🎨 Отформатировано {len(orgunit_display_names)} названий для UI")
        
        # Показываем список как в Combobox
        print("\n📋 Список OU как в выпадающем списке:")
        print("-" * 80)
        for i, display_name in enumerate(orgunit_display_names, 1):
            print(f"{i:2d}. {display_name}")
        
        # Тестируем конвертацию обратно в пути
        print(f"\n🔄 Тест конвертации отображаемых имен обратно в пути:")
        print("-" * 80)
        
        test_cases = [
            "🏠 Корневое подразделение",
            "🏢 HR", 
            "  🏢 Admin",
            "🏢 Marketing",
            "  🏢 CPC",
            "🏢 Product development",
            "  🏢 Development"
        ]
        
        for display_name in test_cases:
            if display_name in orgunit_display_names:
                path = get_orgunit_path_from_display_name(display_name, orgunits)
                status = "✅"
                print(f"  {status} '{display_name}' → '{path}'")
            else:
                print(f"  ⚠️ '{display_name}' не найдено в списке")
        
        # Особо проверяем HR/Admin
        print(f"\n🎯 Особая проверка подразделения HR/Admin:")
        print("-" * 80)
        
        hr_admin_found = False
        for display_name in orgunit_display_names:
            if "Admin" in display_name and "HR" in [ou.get('orgUnitPath', '') for ou in orgunits if ou.get('name') == 'Admin']:
                path = get_orgunit_path_from_display_name(display_name, orgunits)
                print(f"✅ Найдено: '{display_name}' → '{path}'")
                hr_admin_found = True
                
                # Проверяем, что это действительно подразделение под HR
                for ou in orgunits:
                    if ou.get('orgUnitPath') == path:
                        parent_path = '/'.join(path.split('/')[:-1]) or '/'
                        print(f"   📁 Родительское подразделение: {parent_path}")
                        break
        
        if not hr_admin_found:
            print("❌ Подразделение HR/Admin не найдено в отформатированном списке")
        
        # Показываем все дочерние подразделения
        print(f"\n🌳 Все дочерние подразделения (уровень 2+):")
        print("-" * 80)
        
        child_count = 0
        for ou in orgunits:
            path = ou.get('orgUnitPath', '/')
            if path.count('/') > 1:  # Дочерние подразделения
                name = ou.get('name', 'Unknown')
                parent = '/'.join(path.split('/')[:-1])
                print(f"  🏢 {name} ({path}) ← родитель: {parent}")
                child_count += 1
        
        print(f"\n📊 Итого дочерних подразделений: {child_count}")
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Главная функция"""
    test_ui_ou_functionality()
    
    print("\n" + "=" * 80)
    print("💡 Если вы видите только главные подразделения:")
    print("1. Убедитесь, что приложение перезапущено после изменений")
    print("2. Проверьте, что в Google Admin Console действительно есть дочерние OU")
    print("3. Дочерние OU отображаются с отступами (пробелами)")

if __name__ == "__main__":
    main()
