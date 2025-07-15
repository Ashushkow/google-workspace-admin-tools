#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрационный скрипт для календаря SPUTNIK (общий).
Показывает, как использовать новую функциональность.
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.api.sputnik_calendar import create_sputnik_calendar_manager
from src.api.calendar_api import GoogleCalendarAPI


def demo_sputnik_calendar():
    """Демонстрация работы с календарем SPUTNIK"""
    print("=" * 70)
    print("🎯 ДЕМОНСТРАЦИЯ КАЛЕНДАРЯ SPUTNIK (ОБЩИЙ)")
    print("=" * 70)
    print()
    
    # Проверяем наличие credentials
    credentials_path = Path("credentials.json")
    if not credentials_path.exists():
        print("❌ Файл credentials.json не найден")
        print("📋 Для настройки см.: docs/OAUTH2_PRIORITY_SETUP.md")
        print()
        print("🔗 URL календаря SPUTNIK:")
        print("https://calendar.google.com/calendar/u/0?cid=dGNvNXZpcWxjNnZ0MjBsYmtsaDAzdTJrYjhAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ")
        print()
        print("📋 ID календаря:")
        print("tco5viqlc6vt20lbklh03u2kb8@group.calendar.google.com")
        return
    
    print("🔑 Инициализация календаря SPUTNIK...")
    
    try:
        # Создаем менеджер календаря SPUTNIK
        manager = create_sputnik_calendar_manager()
        
        if not manager:
            print("❌ Не удалось инициализировать менеджер календаря SPUTNIK")
            print("   Возможные причины:")
            print("   - Нет доступа к календарю")
            print("   - Проблемы с аутентификацией")
            print("   - Календарь не существует")
            return
        
        print("✅ Менеджер календаря SPUTNIK инициализирован")
        print()
        
        # Получаем информацию о календаре
        calendar_info = manager.get_calendar_info()
        if calendar_info:
            print("📅 ИНФОРМАЦИЯ О КАЛЕНДАРЕ:")
            print(f"   Название: {calendar_info.name}")
            print(f"   Владелец: {calendar_info.owner}")
            print(f"   Описание: {calendar_info.description}")
            print()
        
        # Получаем участников
        print("👥 ЗАГРУЗКА УЧАСТНИКОВ...")
        members = manager.get_members()
        
        if members:
            print(f"✅ Найдено участников: {len(members)}")
            print()
            print("📋 СПИСОК УЧАСТНИКОВ:")
            print("-" * 70)
            
            for i, member in enumerate(members, 1):
                role_desc = manager.get_role_description(member.role)
                print(f"{i:2}. {member.email}")
                print(f"    Роль: {role_desc}")
                print()
            
            # Статистика
            stats = manager.get_member_statistics()
            print("📊 СТАТИСТИКА:")
            print(f"   Всего участников: {stats['total']}")
            print(f"   Владельцев: {stats['owners']}")
            print(f"   Редакторов: {stats['writers']}")
            print(f"   Читателей: {stats['readers']}")
            print(f"   Других ролей: {stats['other']}")
            
        else:
            print("⚠️ Участники не найдены или нет доступа к календарю")
        
        print()
        print("🔧 ДОСТУПНЫЕ ОПЕРАЦИИ:")
        print("   • Добавить участника: manager.add_member(email, role)")
        print("   • Удалить участника: manager.remove_member(email)")
        print("   • Изменить роль: manager.change_member_role(email, new_role)")
        print("   • Массовое добавление: manager.add_multiple_members(members_data)")
        print()
        print("📱 GUI ДОСТУП:")
        print("   • Меню: Календари → 🎯 Календарь SPUTNIK (общий)")
        print("   • Горячие клавиши: Ctrl+Shift+S")
        print("   • Кнопка в тулбаре: 🎯 SPUTNIK")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print()
        print("🔧 ВОЗМОЖНЫЕ РЕШЕНИЯ:")
        print("   1. Проверьте файл credentials.json")
        print("   2. Убедитесь в доступе к календарю SPUTNIK")
        print("   3. Проверьте интернет-соединение")
    
    print()
    print("=" * 70)


def demo_calendar_url_extraction():
    """Демонстрация извлечения ID календаря из URL"""
    print("🔗 ДЕМОНСТРАЦИЯ ИЗВЛЕЧЕНИЯ ID ИЗ URL")
    print("=" * 70)
    
    # URL календаря SPUTNIK
    calendar_url = "https://calendar.google.com/calendar/u/0?cid=dGNvNXZpcWxjNnZ0MjBsYmtsaDAzdTJrYjhAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ"
    
    print(f"URL: {calendar_url}")
    print()
    
    # Извлекаем ID
    calendar_id = GoogleCalendarAPI.extract_calendar_id_from_url(calendar_url)
    
    if calendar_id:
        print(f"✅ Извлеченный ID: {calendar_id}")
    else:
        print("❌ Не удалось извлечь ID из URL")
    
    print()


if __name__ == "__main__":
    # Демонстрация извлечения ID из URL
    demo_calendar_url_extraction()
    
    # Основная демонстрация
    demo_sputnik_calendar()
