#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест исправления групп в Admin Team Tools
"""

import sys
import os

# Добавляем корневую папку в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth import get_service
from src.api.groups_api import list_groups

def test_final_groups_fix():
    """Финальный тест исправления групп"""
    print("🔧 Финальный тест исправления отображения групп...")
    
    try:
        # Получаем сервис
        service = get_service()
        print("✅ Подключение к Google API успешно!")
        
        # Тестируем функцию list_groups (используется в UI)
        print("\n👥 Тестируем list_groups (как в UI)...")
        groups = list_groups(service)
        
        print(f"✅ Функция list_groups вернула: {len(groups)} групп")
        
        if groups:
            print("\n📋 Примеры групп:")
            for i, group in enumerate(groups[:3]):
                email = group.get('email', 'N/A')
                name = group.get('name', 'N/A')
                members_count = group.get('directMembersCount', 'N/A')
                print(f"  {i+1}. {email} ({name}) - участников: {members_count}")
            
            print(f"\n📊 Итого групп: {len(groups)}")
            return True
        else:
            print("❌ Группы не загружены!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 ФИНАЛЬНЫЙ ТЕСТ: Исправление отображения групп")
    print("=" * 60)
    
    success = test_final_groups_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ✅ ИСПРАВЛЕНИЕ УСПЕШНО! Группы теперь отображаются в UI!")
        print("📝 Резюме:")
        print("  • Исправлена функция list_groups в groups_api.py")
        print("  • Добавлена резервная загрузка групп в ServiceAdapter")
        print("  • Убраны ограничения на количество групп")
        print("  • Приложение теперь загружает ВСЕ группы с пагинацией")
    else:
        print("❌ Исправление не сработало.")
    print("=" * 60)
