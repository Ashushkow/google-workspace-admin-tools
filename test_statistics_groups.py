#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест отображения групп в статистике UI
"""

import sys
import os
import tkinter as tk
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth import get_service
from src.ui.components.statistics_panel import StatisticsPanel

def test_statistics_groups():
    """Тестирует отображение групп в панели статистики"""
    print("🔧 Тестируем отображение групп в StatisticsPanel...")
    
    try:
        # Получаем сервис
        service = get_service()
        print("✅ Подключение к Google API успешно!")
        
        # Создаем простое окно для тестирования
        root = tk.Tk()
        root.title("Тест StatisticsPanel")
        root.geometry("300x200")
        
        # Создаем StatisticsPanel
        print("📊 Создаем StatisticsPanel...")
        stats_panel = StatisticsPanel(root, service)
        
        # Загружаем статистику
        print("📈 Загружаем статистику...")
        result = stats_panel.load_statistics()
        
        if result:
            users_count, groups_count = result
            print(f"✅ Статистика загружена:")
            print(f"  👥 Пользователей: {users_count}")
            print(f"  👫 Групп: {groups_count}")
            
            if groups_count > 0:
                print("🎉 Группы отображаются правильно!")
                success = True
            else:
                print("❌ Группы не отображаются (количество = 0)")
                success = False
        else:
            print("❌ Не удалось загрузить статистику")
            success = False
        
        # Показываем окно на 3 секунды для визуальной проверки
        root.after(3000, root.destroy)
        print("🖼️ Показываем окно на 3 секунды...")
        root.mainloop()
        
        return success
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Тест отображения групп в UI StatisticsPanel")
    print("=" * 60)
    
    success = test_statistics_groups()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Тест пройден! Группы отображаются в StatisticsPanel.")
    else:
        print("❌ Тест не пройден. Проблема с отображением групп.")
    print("=" * 60)
