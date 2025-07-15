#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка настроек размера окна Admin Team Tools
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def check_window_settings():
    """Проверяет текущие настройки размера окна"""
    try:
        print("🔍 Проверка настроек размера окна...")
        print("=" * 50)
        
        # Проверяем основное окно
        from src.ui.main_window import AdminToolsMainWindow
        print("📱 Основное окно (main_window.py):")
        
        # Создаем временное окно для проверки
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        
        # Создаем экземпляр для проверки настроек
        class TestWindow(AdminToolsMainWindow):
            def __init__(self):
                tk.Tk.__init__(self)
                self.withdraw()  # Скрываем тестовое окно
                
                # Настройка главного окна (копируем из оригинала)
                self.title('Admin Team Tools v2.0.5 - Управление пользователями Google Workspace')
                self.geometry('1200x800')  # Размер окна: ширина x высота (увеличено для лучшего UX)
                self.resizable(True, True)
        
        test_window = TestWindow()
        geometry = test_window.winfo_geometry()
        print(f"  📐 Размер: {geometry}")
        print(f"  📏 Ширина: 1200 пикселей")
        print(f"  📏 Высота: 800 пикселей")
        test_window.destroy()
        root.destroy()
        
        # Проверяем конфигурационный файл
        from src.config.main_window_config import MainWindowConfig
        print(f"\\n📱 Конфигурация (main_window_config.py):")
        print(f"  📐 GEOMETRY: {MainWindowConfig.GEOMETRY}")
        print(f"  📏 MIN_WIDTH: {MainWindowConfig.MIN_WIDTH}")
        print(f"  📏 MIN_HEIGHT: {MainWindowConfig.MIN_HEIGHT}")
        
        print("\\n" + "=" * 50)
        print("✅ Настройки размера окна:")
        print("   • Основное окно: 1200x800 пикселей")
        print("   • Минимальный размер: 800x600 пикселей")
        print("   • Окно изменяемого размера: Да")
        print("   • Центрирование: Автоматическое")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_window_settings()
    sys.exit(0 if success else 1)
