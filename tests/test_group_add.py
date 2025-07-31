#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование добавления пользователя в доступную группу.
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.auth import get_service
from src.config.enhanced_config import config


def test_add_user_to_available_group():
    """Тестирование добавления пользователя в доступную группу"""
    print("🧪 ТЕСТ ДОБАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯ В ГРУППУ")
    print("=" * 60)
    
    try:
        service = get_service()
        
        # Получаем список групп
        print("📋 Получение списка доступных групп...")
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
        
        if not groups:
            print("❌ Доступных групп не найдено")
            return False
        
        # Выбираем первую доступную группу для тестирования
        test_group = groups[0]
        test_group_email = test_group.get('email')
        test_group_name = test_group.get('name')
        
        print(f"\n🎯 Тестовая группа: {test_group_name} ({test_group_email})")
        
        # Получаем список пользователей для тестирования
        print("👥 Получение списка пользователей...")
        users_result = service.users().list(
            domain=config.settings.google_workspace_domain,
            maxResults=5
        ).execute()
        users = users_result.get('users', [])
        
        if not users:
            print("❌ Пользователи не найдены")
            return False
        
        print(f"✅ Найдено {len(users)} пользователей:")
        for i, user in enumerate(users, 1):
            user_email = user.get('primaryEmail')
            user_name = user.get('name', {}).get('fullName', 'N/A')
            print(f"  {i}. {user_name} ({user_email})")
        
        # Выбираем пользователя для тестирования (не администратора)
        test_user = None
        admin_email = config.settings.google_workspace_admin
        
        for user in users:
            if user.get('primaryEmail') != admin_email:
                test_user = user
                break
        
        if not test_user:
            test_user = users[0]  # Используем первого, если других нет
        
        test_user_email = test_user.get('primaryEmail')
        test_user_name = test_user.get('name', {}).get('fullName', 'N/A')
        
        print(f"\n👤 Тестовый пользователь: {test_user_name} ({test_user_email})")
        
        # Проверяем, не является ли пользователь уже участником группы
        print(f"\n🔍 Проверка текущих участников группы {test_group_email}...")
        try:
            members_result = service.members().list(groupKey=test_group_email).execute()
            current_members = members_result.get('members', [])
            current_emails = [m.get('email') for m in current_members]
            
            print(f"📊 Текущие участники ({len(current_members)}):")
            for member in current_members:
                print(f"  - {member.get('email')} ({member.get('role', 'N/A')})")
            
            if test_user_email in current_emails:
                print(f"⚠️ Пользователь {test_user_email} уже состоит в группе")
                print("💡 Это нормально для тестирования - API должен вернуть соответствующее сообщение")
            
        except Exception as e:
            print(f"❌ Ошибка получения участников: {e}")
            return False
        
        # Тестируем добавление пользователя
        print(f"\n🚀 ТЕСТ: Добавление {test_user_email} в группу {test_group_email}")
        print("=" * 60)
        
        try:
            body = {
                'email': test_user_email,
                'role': 'MEMBER'
            }
            
            result = service.members().insert(
                groupKey=test_group_email,
                body=body
            ).execute()
            
            print(f"✅ УСПЕХ: Пользователь успешно добавлен!")
            print(f"📋 Результат: {result}")
            
            # Проверяем, что пользователь действительно добавлен
            print(f"\n🔍 Проверка: пользователь добавлен в группу...")
            members_after = service.members().list(groupKey=test_group_email).execute()
            updated_emails = [m.get('email') for m in members_after.get('members', [])]
            
            if test_user_email in updated_emails:
                print(f"✅ Подтверждение: {test_user_email} найден в списке участников")
            else:
                print(f"⚠️ Странно: {test_user_email} не найден в обновленном списке")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "Member already exists" in error_msg:
                print(f"ℹ️ Пользователь уже состоит в группе (это нормально)")
                return True
            elif "403" in error_msg and "Not Authorized" in error_msg:
                print(f"❌ Ошибка 403: {e}")
                print("💡 Такая же ошибка, как с testdecember2023@sputnik8.com")
                return False
            else:
                print(f"❌ Другая ошибка: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False


def main():
    print("🔧 ТЕСТИРОВАНИЕ РАБОТЫ С ГРУППАМИ")
    print("Цель: проверить, работает ли добавление пользователей в другие группы")
    print("=" * 60)
    
    success = test_add_user_to_available_group()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ РЕЗУЛЬТАТ: Добавление пользователей в группы РАБОТАЕТ")
        print("💡 Проблема специфична для группы testdecember2023@sputnik8.com")
        print("🔧 Рекомендации:")
        print("  1. Проверьте настройки группы testdecember2023@sputnik8.com в Admin Console")
        print("  2. Возможно, группа имеет особые ограничения безопасности")
        print("  3. Попробуйте создать новую тестовую группу")
    else:
        print("❌ РЕЗУЛЬТАТ: Проблема с добавлением пользователей в группы")
        print("🔧 Требуется дополнительная диагностика прав доступа")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
