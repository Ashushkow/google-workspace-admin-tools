#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенная диагностика Google API для проблемы 403.
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.auth import get_service
from src.config.enhanced_config import config


def test_api_access():
    """Тестирование доступа к различным API endpoints"""
    print("🧪 ТЕСТИРОВАНИЕ ДОСТУПА К GOOGLE API")
    print("=" * 60)
    
    try:
        # Получаем сервис
        service = get_service()
        print("✅ Google API сервис инициализирован")
        
        # Тест 1: Проверка доступа к пользователям
        print("\n1️⃣ Тест доступа к пользователям...")
        try:
            users_result = service.users().list(
                domain=config.settings.google_workspace_domain,
                maxResults=1
            ).execute()
            users = users_result.get('users', [])
            print(f"   ✅ Доступ к пользователям: OK ({len(users)} пользователей)")
        except Exception as e:
            print(f"   ❌ Ошибка доступа к пользователям: {e}")
            return False
        
        # Тест 2: Проверка доступа к группам
        print("\n2️⃣ Тест доступа к группам...")
        try:
            groups_result = service.groups().list(
                domain=config.settings.google_workspace_domain,
                maxResults=5
            ).execute()
            groups = groups_result.get('groups', [])
            print(f"   ✅ Доступ к группам: OK ({len(groups)} групп)")
            
            if groups:
                # Тест 3: Проверка доступа к участникам конкретной группы
                test_group = groups[0]
                group_email = test_group.get('email')
                print(f"\n3️⃣ Тест доступа к участникам группы {group_email}...")
                
                try:
                    members_result = service.members().list(groupKey=group_email).execute()
                    members = members_result.get('members', [])
                    print(f"   ✅ Доступ к участникам: OK ({len(members)} участников)")
                    
                    # Тест 4: Проверка специально проблемной группы
                    problem_group = "testdecember2023@sputnik8.com"
                    print(f"\n4️⃣ Тест доступа к проблемной группе {problem_group}...")
                    
                    try:
                        problem_members = service.members().list(groupKey=problem_group).execute()
                        members_count = len(problem_members.get('members', []))
                        print(f"   ✅ Доступ к {problem_group}: OK ({members_count} участников)")
                        
                        # Тест 5: Проверка возможности добавления (но не добавляем)
                        print(f"\n5️⃣ Тест прав на изменение группы {problem_group}...")
                        
                        # Попытаемся получить детали группы
                        try:
                            group_details = service.groups().get(groupKey=problem_group).execute()
                            print(f"   ✅ Детали группы получены")
                            print(f"   📋 Название: {group_details.get('name', 'N/A')}")
                            print(f"   📧 Email: {group_details.get('email', 'N/A')}")
                            print(f"   👥 Участников: {group_details.get('directMembersCount', 'N/A')}")
                            
                            # Проверяем настройки группы
                            settings = group_details.get('settings', {})
                            who_can_join = settings.get('whoCanJoin', 'N/A')
                            who_can_invite = settings.get('whoCanInvite', 'N/A')
                            
                            print(f"   ⚙️ Кто может присоединяться: {who_can_join}")
                            print(f"   ⚙️ Кто может приглашать: {who_can_invite}")
                            
                        except Exception as e:
                            print(f"   ❌ Ошибка получения деталей группы: {e}")
                            
                    except Exception as e:
                        print(f"   ❌ Ошибка доступа к {problem_group}: {e}")
                        
                        # Проверяем, существует ли группа вообще
                        print(f"\n🔍 Проверка существования группы {problem_group}...")
                        try:
                            group_info = service.groups().get(groupKey=problem_group).execute()
                            print(f"   ✅ Группа существует: {group_info.get('name')}")
                        except Exception as ge:
                            print(f"   ❌ Группа не найдена или недоступна: {ge}")
                            return False
                        
                except Exception as e:
                    print(f"   ❌ Ошибка доступа к участникам: {e}")
                    
            else:
                print("   ⚠️ Группы не найдены")
                
        except Exception as e:
            print(f"   ❌ Ошибка доступа к группам: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False


def check_user_permissions():
    """Проверка прав текущего пользователя"""
    print("\n👤 ПРОВЕРКА ПРАВ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)
    
    try:
        service = get_service()
        
        # Получаем информацию о текущем пользователе
        print("📋 Попытка получить информацию о текущем авторизованном пользователе...")
        
        # Используем Admin API для получения информации о пользователе
        admin_email = config.settings.google_workspace_admin
        print(f"🔍 Проверка пользователя: {admin_email}")
        
        try:
            user_info = service.users().get(userKey=admin_email).execute()
            print(f"   ✅ Пользователь найден: {user_info.get('primaryEmail')}")
            print(f"   📛 Имя: {user_info.get('name', {}).get('fullName', 'N/A')}")
            print(f"   🏢 Роль: {user_info.get('isAdmin', False) and 'Администратор' or 'Пользователь'}")
            print(f"   🔓 Приостановлен: {'Да' if user_info.get('suspended', False) else 'Нет'}")
            
            if not user_info.get('isAdmin', False):
                print("   ⚠️ ПРЕДУПРЕЖДЕНИЕ: Пользователь не является администратором!")
                print("   💡 Для управления группами нужны права администратора")
                
        except Exception as e:
            print(f"   ❌ Ошибка получения информации о пользователе: {e}")
            
    except Exception as e:
        print(f"❌ Ошибка проверки прав: {e}")


def main():
    print("🔍 РАСШИРЕННАЯ ДИАГНОСТИКА ОШИБКИ 403")
    print("=" * 60)
    print(f"🌐 Домен: {config.settings.google_workspace_domain}")
    print(f"👤 Администратор: {config.settings.google_workspace_admin}")
    print()
    
    # Тестируем доступ к API
    api_ok = test_api_access()
    
    # Проверяем права пользователя
    check_user_permissions()
    
    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ НА ОСНОВЕ ДИАГНОСТИКИ:")
    print("=" * 60)
    
    if api_ok:
        print("✅ Основной доступ к API работает")
        print("🎯 Возможные причины ошибки 403 при добавлении в группу:")
        print("   1. Группа имеет ограниченные настройки безопасности")
        print("   2. Пользователь не имеет прав на изменение конкретной группы")
        print("   3. Группа находится в организационной единице с ограничениями")
        print("   4. Временные проблемы с Google API")
        print()
        print("🔧 Попробуйте:")
        print("   1. Добавить пользователя в другую группу для проверки")
        print("   2. Проверить настройки группы testdecember2023@sputnik8.com в Admin Console")
        print("   3. Попробовать добавить через веб-интерфейс Google Admin Console")
    else:
        print("❌ Обнаружены проблемы с доступом к API")
        print("🔧 Необходимо:")
        print("   1. Проверить права пользователя в Google Workspace")
        print("   2. Убедиться что Admin SDK API включен")
        print("   3. Проверить настройки OAuth consent screen")


if __name__ == "__main__":
    main()
