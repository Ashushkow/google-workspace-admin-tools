#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления загрузки групп в UI
"""

import sys
import os

# Добавляем корневую папку в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth import get_service
from src.api.groups_api import list_groups

def test_ui_groups_fix():
    """Тестирует исправленную загрузку групп через groups_api"""
    print("🔧 Тестируем исправленную загрузку групп через groups_api...")
    
    try:
        # Получаем сервис (как в реальном приложении)
        print("🔗 Подключаемся к Google API...")
        service = get_service()
        print("✅ Подключение успешно!")
        
        # Тестируем функцию list_groups из groups_api
        print("\n👥 Тестируем list_groups из groups_api...")
        groups = list_groups(service)
        
        print(f"✅ Функция list_groups вернула: {len(groups)} групп")
        
        if groups:
            print("\n📋 Примеры групп:")
            for i, group in enumerate(groups[:5]):
                email = group.get('email', 'N/A')
                name = group.get('name', 'N/A')
                members_count = group.get('directMembersCount', 'N/A')
                print(f"  {i+1}. {email} ({name}) - участников: {members_count}")
            
            if len(groups) > 5:
                print(f"  ... и еще {len(groups) - 5} групп")
            
            return True
        else:
            print("❌ Группы не загружены!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Тест исправления загрузки групп в UI")
    print("=" * 60)
    
    success = test_ui_groups_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Исправление работает! Группы должны отображаться в UI.")
    else:
        print("❌ Исправление не сработало.")
    print("=" * 60)
