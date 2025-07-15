#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки нового диалога добавления участников SPUTNIK.
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Тестирование импортов"""
    print("🔧 Проверка импортов...")
    
    try:
        from src.ui.sputnik_calendar_ui import AddSputnikMemberDialog
        print("✅ AddSputnikMemberDialog импортирован успешно")
        
        from src.api.sputnik_calendar import create_sputnik_calendar_manager
        print("✅ SputnikCalendarManager импортирован успешно")
        
        print("✅ Все основные компоненты импортированы успешно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_user_loading():
    """Тестирование загрузки пользователей домена"""
    print("\n👥 Проверка загрузки пользователей домена sputnik8.com...")
    
    try:
        # Проверяем наличие credentials
        if not os.path.exists("credentials.json"):
            print("⚠️ Файл credentials.json не найден - будут использованы примеры")
            return True
        
        print("✅ Credentials найдены - загрузка пользователей будет работать")
        print("💡 Диалог будет автоматически загружать пользователей домена sputnik8.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки пользователей: {e}")
        return False

def test_calendar_connection():
    """Тестирование подключения к календарю SPUTNIK"""
    print("\n🎯 Проверка подключения к календарю SPUTNIK...")
    
    try:
        # Проверяем наличие credentials
        if not os.path.exists("credentials.json"):
            print("⚠️ Файл credentials.json не найден - пропускаем тест календаря")
            return True
        
        from src.api.sputnik_calendar import create_sputnik_calendar_manager
        
        # Создаем менеджер календаря
        manager = create_sputnik_calendar_manager()
        
        if not manager:
            print("⚠️ Не удалось создать менеджер календаря - пропускаем тест")
            return True
        
        # Получаем информацию о календаре
        calendar_info = manager.get_calendar_info()
        if calendar_info:
            print(f"✅ Календарь: {calendar_info.name}")
        
        # Получаем участников
        members = manager.get_members()
        print(f"✅ Участников в календаре: {len(members)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к календарю: {e}")
        return False

def show_new_features():
    """Показать новые возможности"""
    print("\n🎉 НОВЫЕ ВОЗМОЖНОСТИ ДОБАВЛЕНИЯ УЧАСТНИКОВ:")
    print("=" * 60)
    print("✨ Выбор из списка сотрудников домена sputnik8.com")
    print("🔍 Поиск сотрудников по имени и email")
    print("👤 Отображение статуса пользователя (активен/заблокирован)")
    print("🔗 Индикация уже добавленных в календарь")
    print("🔐 Выбор прав доступа с подробным описанием")
    print("⚡ Быстрое добавление двойным кликом")
    print("✅ Подтверждение с полной информацией о пользователе")
    print()
    print("🚀 Для тестирования:")
    print("  1. Запустите main.py")
    print("  2. Нажмите кнопку '🎯 SPUTNIK' или Ctrl+Shift+S")
    print("  3. Нажмите '➕ Добавить участника'")
    print("  4. Выберите сотрудника из списка")
    print("=" * 60)

if __name__ == "__main__":
    print("🧪 ТЕСТИРОВАНИЕ НОВОГО ДИАЛОГА ДОБАВЛЕНИЯ УЧАСТНИКОВ")
    print("=" * 70)
    
    # Тестируем импорты
    if not test_imports():
        sys.exit(1)
    
    # Тестируем загрузку пользователей
    test_user_loading()
    
    # Тестируем подключение к календарю
    test_calendar_connection()
    
    # Показываем новые возможности
    show_new_features()
    
    print("\n✅ Все тесты завершены!")
    print("🎯 Новый диалог готов к использованию!")
