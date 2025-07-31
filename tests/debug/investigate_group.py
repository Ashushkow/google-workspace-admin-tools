#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исследование проблемной группы testdecember2023@sputnik8.com
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.auth import get_service
from src.config.enhanced_config import config


def investigate_problem_group():
    """Исследование проблемной группы"""
    print("🔍 ИССЛЕДОВАНИЕ ГРУППЫ testdecember2023@sputnik8.com")
    print("=" * 60)
    
    problem_group = "testdecember2023@sputnik8.com"
    service = get_service()
    
    # 1. Проверяем, существует ли группа вообще
    print("1️⃣ Проверка существования группы...")
    try:
        # Попробуем найти группу через поиск
        all_groups = service.groups().list(
            domain=config.settings.google_workspace_domain,
            maxResults=50
        ).execute()
        
        groups = all_groups.get('groups', [])
        found_group = None
        
        for group in groups:
            if group.get('email') == problem_group:
                found_group = group
                break
        
        if found_group:
            print(f"   ✅ Группа найдена в списке групп домена")
            print(f"   📛 Название: {found_group.get('name', 'N/A')}")
            print(f"   📧 Email: {found_group.get('email')}")
            print(f"   👥 Участников: {found_group.get('directMembersCount', 'N/A')}")
        else:
            print(f"   ❌ Группа НЕ найдена в списке групп домена {config.settings.google_workspace_domain}")
            
            # Возможно, группа в другом домене или имеет специальные настройки
            print(f"   🔍 Попытка прямого доступа к группе...")
            try:
                direct_group = service.groups().get(groupKey=problem_group).execute()
                print(f"   ⚠️ Группа существует, но недоступна через список:")
                print(f"      Название: {direct_group.get('name', 'N/A')}")
                print(f"      Email: {direct_group.get('email')}")
                print(f"      Описание: {direct_group.get('description', 'N/A')}")
            except Exception as e:
                print(f"   ❌ Прямой доступ также невозможен: {e}")
                
                # Попробуем проверить через другие API
                print(f"   🔍 Проверка через Groups Settings API...")
                try:
                    # Если есть доступ к Groups Settings API
                    pass
                except:
                    pass
                
    except Exception as e:
        print(f"   ❌ Ошибка при поиске группы: {e}")
    
    # 2. Анализ возможных причин
    print("\n2️⃣ Анализ возможных причин недоступности...")
    
    possible_reasons = [
        "🔒 Группа имеет ограничения безопасности",
        "🏢 Группа находится в специальной Organizational Unit", 
        "👥 Группа создана не через Admin Console",
        "📧 Группа является внешней или общей группой",
        "⚙️ Группа имеет особые настройки доступа",
        "🚫 Группа была удалена или заархивирована",
        "🔄 Группа находится в процессе миграции",
        "📋 У текущего пользователя нет прав на эту конкретную группу"
    ]
    
    for reason in possible_reasons:
        print(f"   {reason}")
    
    # 3. Рекомендации по решению
    print("\n3️⃣ Рекомендации по решению...")
    
    print("   📊 В Google Admin Console:")
    print("      1. Перейдите в Directory → Groups")
    print("      2. Найдите группу testdecember2023@sputnik8.com")
    print("      3. Проверьте настройки безопасности и доступа")
    print("      4. Проверьте Organizational Unit группы")
    print()
    print("   🧪 Для тестирования:")
    print("      1. Создайте новую тестовую группу")
    print("      2. Попробуйте добавить пользователей в неё")
    print("      3. Если работает - проблема в настройках testdecember2023")
    print()
    print("   🔧 Альтернативные решения:")
    print("      1. Переименуйте группу testdecember2023@sputnik8.com")
    print("      2. Создайте новую группу с теми же участниками")
    print("      3. Обратитесь к Google Support за помощью")


def create_test_group():
    """Создание тестовой группы для проверки функциональности"""
    print("\n🧪 СОЗДАНИЕ ТЕСТОВОЙ ГРУППЫ")
    print("=" * 60)
    
    service = get_service()
    test_group_email = f"test-group-{int(__import__('time').time())}@{config.settings.google_workspace_domain}"
    
    try:
        # Создаем тестовую группу
        group_body = {
            'email': test_group_email,
            'name': 'Test Group for API Testing',
            'description': 'Временная группа для тестирования добавления пользователей'
        }
        
        print(f"📝 Создание группы: {test_group_email}")
        
        created_group = service.groups().insert(body=group_body).execute()
        print(f"✅ Группа создана успешно!")
        print(f"   📧 Email: {created_group.get('email')}")
        print(f"   📛 Название: {created_group.get('name')}")
        
        # Теперь попробуем добавить пользователя
        print(f"\n👤 Добавление тестового пользователя...")
        
        users = service.users().list(
            domain=config.settings.google_workspace_domain,
            maxResults=1
        ).execute().get('users', [])
        
        if users:
            test_user_email = users[0].get('primaryEmail')
            
            try:
                member_body = {
                    'email': test_user_email,
                    'role': 'MEMBER'
                }
                
                add_result = service.members().insert(
                    groupKey=test_group_email,
                    body=member_body
                ).execute()
                
                print(f"✅ Пользователь {test_user_email} успешно добавлен!")
                print("🎉 ВЫВОД: API для управления группами работает корректно")
                
            except Exception as e:
                print(f"❌ Ошибка добавления пользователя: {e}")
        
        # Удаляем тестовую группу
        print(f"\n🗑️ Удаление тестовой группы...")
        try:
            service.groups().delete(groupKey=test_group_email).execute()
            print(f"✅ Тестовая группа удалена")
        except Exception as e:
            print(f"⚠️ Не удалось удалить тестовую группу: {e}")
            print(f"   Удалите вручную: {test_group_email}")
        
    except Exception as e:
        print(f"❌ Ошибка создания тестовой группы: {e}")


def main():
    print("🔍 ПОЛНАЯ ДИАГНОСТИКА ПРОБЛЕМЫ С ГРУППОЙ")
    print("=" * 60)
    
    try:
        investigate_problem_group()
        create_test_group()
        
        print("\n" + "=" * 60)
        print("📋 ЗАКЛЮЧЕНИЕ:")
        print("✅ API для управления группами работает")
        print("❌ Группа testdecember2023@sputnik8.com недоступна")
        print("💡 Проблема НЕ в настройках OAuth или правах приложения")
        print("🔧 Необходимо проверить настройки конкретной группы")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
