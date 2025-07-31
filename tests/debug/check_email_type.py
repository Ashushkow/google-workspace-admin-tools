#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка: testdecember2023@sputnik8.com - пользователь или группа?
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.auth import get_service
from src.config.enhanced_config import config


def check_email_type():
    """Проверяем, является ли testdecember2023@sputnik8.com пользователем или группой"""
    print("🔍 ПРОВЕРКА ТИПА EMAIL: testdecember2023@sputnik8.com")
    print("=" * 60)
    
    email = "testdecember2023@sputnik8.com"
    service = get_service()
    
    # Проверяем как пользователя
    print("1️⃣ Проверка как пользователя...")
    try:
        user_info = service.users().get(userKey=email).execute()
        print(f"   ✅ ЭТО ПОЛЬЗОВАТЕЛЬ!")
        print(f"   📛 Имя: {user_info.get('name', {}).get('fullName', 'N/A')}")
        print(f"   📧 Email: {user_info.get('primaryEmail')}")
        print(f"   🏢 Администратор: {'Да' if user_info.get('isAdmin', False) else 'Нет'}")
        print(f"   🔓 Приостановлен: {'Да' if user_info.get('suspended', False) else 'Нет'}")
        is_user = True
    except Exception as e:
        print(f"   ❌ Не является пользователем: {e}")
        is_user = False
    
    # Проверяем как группу
    print("\n2️⃣ Проверка как группы...")
    try:
        group_info = service.groups().get(groupKey=email).execute()
        print(f"   ✅ ЭТО ГРУППА!")
        print(f"   📛 Название: {group_info.get('name', 'N/A')}")
        print(f"   📧 Email: {group_info.get('email')}")
        print(f"   👥 Участников: {group_info.get('directMembersCount', 'N/A')}")
        is_group = True
    except Exception as e:
        print(f"   ❌ Не является группой: {e}")
        is_group = False
    
    # Выводы
    print("\n" + "=" * 60)
    if is_user and not is_group:
        print("🎯 ВЫВОД: testdecember2023@sputnik8.com - ЭТО ПОЛЬЗОВАТЕЛЬ")
        print("❌ Попытка добавить пользователя в 'группу' с таким же email невозможна")
        print("💡 Нужно выбрать реальную группу для добавления пользователя")
    elif is_group and not is_user:
        print("🎯 ВЫВОД: testdecember2023@sputnik8.com - ЭТО ГРУППА")
    elif is_user and is_group:
        print("🎯 ВЫВОД: testdecember2023@sputnik8.com - И ПОЛЬЗОВАТЕЛЬ, И ГРУППА")
    else:
        print("🎯 ВЫВОД: testdecember2023@sputnik8.com - НИ ПОЛЬЗОВАТЕЛЬ, НИ ГРУППА")
    
    return is_user, is_group


def show_available_groups_and_users():
    """Показываем доступные группы и пользователей для правильного тестирования"""
    print("\n📋 ДОСТУПНЫЕ ГРУППЫ ДЛЯ ДОБАВЛЕНИЯ ПОЛЬЗОВАТЕЛЕЙ:")
    print("=" * 60)
    
    service = get_service()
    
    try:
        # Получаем группы
        groups_result = service.groups().list(
            domain=config.settings.google_workspace_domain,
            maxResults=10
        ).execute()
        groups = groups_result.get('groups', [])
        
        print(f"✅ Найдено {len(groups)} групп:")
        for i, group in enumerate(groups, 1):
            group_email = group.get('email')
            group_name = group.get('name')
            members_count = group.get('directMembersCount', 'N/A')
            print(f"  {i}. {group_name} ({group_email}) - {members_count} участников")
        
        # Получаем пользователей
        print(f"\n👥 ДОСТУПНЫЕ ПОЛЬЗОВАТЕЛИ ДЛЯ ДОБАВЛЕНИЯ:")
        print("-" * 40)
        
        users_result = service.users().list(
            domain=config.settings.google_workspace_domain,
            maxResults=10
        ).execute()
        users = users_result.get('users', [])
        
        print(f"✅ Найдено {len(users)} пользователей:")
        for i, user in enumerate(users, 1):
            user_email = user.get('primaryEmail')
            user_name = user.get('name', {}).get('fullName', 'N/A')
            print(f"  {i}. {user_name} ({user_email})")
        
        # Пример правильного использования
        if groups and users:
            example_group = groups[0].get('email')
            example_user = users[0].get('primaryEmail')
            
            print(f"\n💡 ПРИМЕР ПРАВИЛЬНОГО ДОБАВЛЕНИЯ:")
            print(f"Добавить пользователя: {example_user}")
            print(f"В группу: {example_group}")
            print(f"Команда API: service.members().insert(groupKey='{example_group}', body={{'email': '{example_user}', 'role': 'MEMBER'}})")
        
    except Exception as e:
        print(f"❌ Ошибка получения данных: {e}")


def main():
    print("🕵️ РАССЛЕДОВАНИЕ ПРОБЛЕМЫ С ДОБАВЛЕНИЕМ В ГРУППУ")
    print("=" * 60)
    
    # Проверяем тип email
    is_user, is_group = check_email_type()
    
    # Показываем правильные варианты
    if is_user and not is_group:
        show_available_groups_and_users()
        
        print("\n" + "=" * 60)
        print("🎯 РЕШЕНИЕ ПРОБЛЕМЫ:")
        print("❌ Ошибка была в том, что пытались добавить пользователя в 'группу'")
        print("   с email пользователя, а не реальной группы")
        print("✅ Используйте email настоящих групп из списка выше")
        print("📋 Обновите код приложения, чтобы выбирать группы, а не пользователей")
        print("=" * 60)


if __name__ == "__main__":
    main()
