#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование разрешений для управления группами.
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.auth import get_service
from src.config.enhanced_config import config


def test_group_permissions():
    """Тестирование разрешений для управления группами"""
    try:
        print("🔐 Тестирование разрешений для управления группами...")
        print(f"📋 Используемые scopes: {config.google.scopes}")
        print()
        
        # Получаем сервис
        service = get_service()
        print("✅ Google API сервис инициализирован успешно")
        
        # Проверяем, можем ли мы получить список групп
        print("📊 Проверка доступа к группам...")
        try:
            groups_result = service.groups().list(domain=config.settings.google_workspace_domain).execute()
            groups = groups_result.get('groups', [])
            print(f"✅ Получено {len(groups)} групп")
            
            if groups:
                # Берем первую группу для тестирования
                test_group = groups[0]
                group_email = test_group.get('email')
                print(f"🎯 Тестовая группа: {group_email}")
                
                # Проверяем доступ к участникам группы
                print("👥 Проверка доступа к участникам группы...")
                try:
                    members_result = service.members().list(groupKey=group_email).execute()
                    members = members_result.get('members', [])
                    print(f"✅ Получено {len(members)} участников в группе")
                    
                    print("\n🎉 Все права доступа работают корректно!")
                    print("💡 Теперь вы можете добавлять и удалять пользователей из групп")
                    
                except Exception as e:
                    print(f"❌ Ошибка доступа к участникам группы: {e}")
                    return False
            else:
                print("⚠️ Группы не найдены в домене")
                
        except Exception as e:
            print(f"❌ Ошибка доступа к группам: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ТЕСТ РАЗРЕШЕНИЙ ДЛЯ УПРАВЛЕНИЯ ГРУППАМИ")
    print("=" * 60)
    
    success = test_group_permissions()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ТЕСТ ПРОЙДЕН: Разрешения настроены корректно")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН: Требуется повторная авторизация")
        print("\n📋 Рекомендации:")
        print("1. Запустите приложение заново: python main.py")
        print("2. Пройдите авторизацию с новыми scopes в браузере")
        print("3. Разрешите доступ к управлению группами")
    print("=" * 60)
