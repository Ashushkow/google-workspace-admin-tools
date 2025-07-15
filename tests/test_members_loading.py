#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест загрузки всех участников календаря SPUTNIK и проверки поиска.
"""

import sys
import os
from pathlib import Path
import time

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_members_loading():
    """Тест загрузки участников календаря"""
    try:
        from src.api.sputnik_calendar import create_sputnik_calendar_manager
        
        print("🧪 ТЕСТ ЗАГРУЗКИ УЧАСТНИКОВ КАЛЕНДАРЯ SPUTNIK")
        print("=" * 60)
        
        # Создаем календарный менеджер
        print("🔧 Создание календарного менеджера...")
        calendar_manager = create_sputnik_calendar_manager()
        if not calendar_manager:
            print("❌ Не удалось создать календарный менеджер")
            return False
        
        print("✅ Календарный менеджер создан")
        
        # Получаем информацию о календаре
        print("\n📋 Информация о календаре:")
        calendar_info = calendar_manager.get_calendar_info()
        print(f"  📅 Название: {calendar_info.name}")
        print(f"  🆔 ID: {calendar_info.id}")
        
        # Загружаем участников
        print("\n👥 Загрузка участников...")
        start_time = time.time()
        
        members = calendar_manager.get_members()
        
        load_time = time.time() - start_time
        
        print(f"✅ Загрузка завершена за {load_time:.2f} секунд")
        print(f"👥 Всего участников: {len(members)}")
        
        # Анализируем участников
        print("\n📊 АНАЛИЗ УЧАСТНИКОВ:")
        print("-" * 40)
        
        # Подсчет по ролям
        role_counts = {}
        domain_counts = {}
        
        for member in members:
            # Роли
            role = member.role
            role_counts[role] = role_counts.get(role, 0) + 1
            
            # Домены
            if '@' in member.email:
                domain = member.email.split('@')[1]
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        print("🔐 Распределение по ролям:")
        for role, count in sorted(role_counts.items()):
            role_emoji = {
                'owner': '👑',
                'writer': '✏️', 
                'reader': '👁️',
                'freeBusyReader': '⏰'
            }.get(role, '❓')
            print(f"  {role_emoji} {role}: {count}")
        
        print("\n🌐 Распределение по доменам:")
        for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  📧 {domain}: {count}")
        
        # Показываем первых 10 участников
        print(f"\n📋 ПЕРВЫЕ 10 УЧАСТНИКОВ:")
        print("-" * 50)
        for i, member in enumerate(members[:10]):
            role_name = {
                'owner': 'Владелец',
                'writer': 'Редактор', 
                'reader': 'Читатель',
                'freeBusyReader': 'Просмотр занятости'
            }.get(member.role, member.role)
            print(f"  {i+1:2}. {member.email:<35} | {role_name}")
        
        if len(members) > 10:
            print(f"     ... и еще {len(members) - 10} участников")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_functionality():
    """Тест функциональности поиска"""
    try:
        from src.api.sputnik_calendar import create_sputnik_calendar_manager
        
        print("\n\n🔍 ТЕСТ ФУНКЦИОНАЛЬНОСТИ ПОИСКА")
        print("=" * 60)
        
        calendar_manager = create_sputnik_calendar_manager()
        members = calendar_manager.get_members()
        
        print(f"📊 База для поиска: {len(members)} участников")
        
        # Тестовые поисковые запросы
        test_queries = [
            "sputnik8.com",
            "andrei",
            "valerii", 
            "alice",
            "example",
            "@gmail",
            "test"
        ]
        
        print("\n🧪 ТЕСТОВЫЕ ПОИСКОВЫЕ ЗАПРОСЫ:")
        print("-" * 40)
        
        for query in test_queries:
            matching_members = []
            query_lower = query.lower()
            
            for member in members:
                email_lower = member.email.lower()
                
                # Простой поиск
                if query_lower in email_lower:
                    matching_members.append(member)
                else:
                    # Поиск по частям email
                    email_parts = email_lower.split('@')
                    name_part = email_parts[0] if email_parts else ''
                    domain_part = email_parts[1] if len(email_parts) > 1 else ''
                    
                    if (query_lower in name_part or 
                        query_lower in domain_part or
                        any(query_lower in part for part in name_part.split('.'))):
                        matching_members.append(member)
            
            print(f"🔍 '{query}': найдено {len(matching_members)} участников")
            
            # Показываем первые 3 результата
            for i, member in enumerate(matching_members[:3]):
                print(f"    {i+1}. {member.email}")
            
            if len(matching_members) > 3:
                print(f"    ... и еще {len(matching_members) - 3}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ УЧАСТНИКОВ КАЛЕНДАРЯ SPUTNIK")
    print("=" * 70)
    
    success = True
    
    # Тест загрузки
    if not test_members_loading():
        success = False
    
    # Тест поиска
    if not test_search_functionality():
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("  1. Запустите main.py и откройте календарь SPUTNIK")
        print("  2. Проверьте отображение всех участников")
        print("  3. Протестируйте поиск различными запросами")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
