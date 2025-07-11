#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест окна управления группами
"""

import sys
import os

# Добавляем корневую папку в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import tkinter as tk
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth import get_service

def test_group_window():
    """Тестирует окно управления группами"""
    print("🔧 Тестируем окно управления группами...")
    
    try:
        # Получаем сервис
        service = get_service()
        print("✅ Подключение к Google API успешно!")
        
        # Импортируем окно групп после получения сервиса
        from src.ui.group_management import GroupManagementWindow
        
        # Создаем главное окно
        root = tk.Tk()
        root.title("Тест окна групп")
        root.geometry("300x200")
        
        # Создаем кнопку для открытия окна групп
        def open_groups():
            group_window = GroupManagementWindow(root, service)
        
        button = tk.Button(root, text="Открыть управление группами", command=open_groups)
        button.pack(pady=50)
        
        print("🖼️ Нажмите кнопку в окне для тестирования групп...")
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Тест окна управления группами")
    print("=" * 60)
    
    success = test_group_window()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Тест завершен.")
    else:
        print("❌ Тест не пройден.")
    print("=" * 60)
