#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест нового компонента управления участниками групп.
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import tkinter as tk
from tkinter import messagebox

def test_group_members_ui():
    """Тест пользовательского интерфейса управления участниками групп"""
    try:
        from src.ui.group_members_management import GroupMembersManagementWindow
        
        # Создаем root окно
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        # Создаем тестовое окно управления участниками
        test_window = GroupMembersManagementWindow(
            master=root,
            group_id="test@company.com",
            group_name="Тестовая группа",
            google_service=None,  # Заглушка
            freeipa_service=None  # Заглушка
        )
        
        # Показываем информацию
        messagebox.showinfo(
            "Тест UI",
            "Окно управления участниками групп создано успешно!\\n"
            "Проверьте интерфейс и закройте окно для завершения теста."
        )
        
        # Запуск основного цикла
        root.mainloop()
        
        print("✅ Тест пользовательского интерфейса прошел успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте UI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_group_management_integration():
    """Тест интеграции с основным окном управления группами"""
    try:
        from src.ui.group_management import GroupManagementWindow
        
        # Создаем root окно
        root = tk.Tk()
        root.withdraw()
        
        # Создаем окно управления группами с поддержкой FreeIPA
        test_window = GroupManagementWindow(
            master=root,
            service=None,  # Заглушка
            freeipa_service=None  # Заглушка
        )
        
        messagebox.showinfo(
            "Тест интеграции",
            "Окно управления группами с поддержкой FreeIPA создано!\\n"
            "Проверьте наличие кнопки '👥 Участники' и закройте окно."
        )
        
        root.mainloop()
        
        print("✅ Тест интеграции прошел успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте интеграции: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция тестирования"""
    print("🧪 Запуск тестов нового функционала управления участниками групп")
    print("=" * 70)
    
    # Тест 1: UI компонента
    print("\\n1️⃣ Тестирование пользовательского интерфейса...")
    ui_test_result = test_group_members_ui()
    
    # Тест 2: Интеграция
    print("\\n2️⃣ Тестирование интеграции с управлением группами...")
    integration_test_result = test_group_management_integration()
    
    # Результаты
    print("\\n" + "=" * 70)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"   UI компонент: {'✅ ПРОЙДЕН' if ui_test_result else '❌ ПРОВАЛЕН'}")
    print(f"   Интеграция: {'✅ ПРОЙДЕН' if integration_test_result else '❌ ПРОВАЛЕН'}")
    
    if ui_test_result and integration_test_result:
        print("\\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("\\nВозможности нового функционала:")
        print("• 👥 Управление участниками групп через отдельное окно")
        print("• 🔗 Интеграция с FreeIPA для добавления пользователей")
        print("• 📊 Отображение участников Google Workspace и FreeIPA")
        print("• 🔍 Поиск пользователей FreeIPA")
        print("• ➕ Добавление пользователей в группы FreeIPA")
        print("• ➖ Удаление пользователей из групп FreeIPA")
        print("• 🔄 Синхронизация между системами")
    else:
        print("\\n⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        print("Проверьте ошибки выше для диагностики.")

if __name__ == "__main__":
    main()
