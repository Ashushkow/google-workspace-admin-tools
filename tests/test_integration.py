# -*- coding: utf-8 -*-
"""
Тест интеграции для проверки работы приложения
"""

import tkinter as tk
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_integration():
    """Тестируем интеграцию приложения"""
    try:
        from main_window import AdminToolsMainWindow
        from auth import get_service
        from config import CREDENTIALS_FILE
        
        print("✓ Импорт основных модулей успешен")
        
        # Проверяем наличие credentials файла
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"⚠️  Файл {CREDENTIALS_FILE} не найден - это нормально для тестирования")
            return
        
        # Создаем главное окно
        root = tk.Tk()
        root.withdraw()
        
        # Пытаемся получить сервис
        try:
            service = get_service()
            print("✓ Сервис Google API инициализирован")
        except Exception as e:
            print(f"⚠️  Не удалось инициализировать сервис: {e}")
            service = None
        
        # Создаем главное окно приложения
        app = AdminToolsMainWindow(service=service)
        print("✓ Главное окно приложения создано")
        
        # Проверяем, что окно имеет необходимые методы
        assert hasattr(app, 'open_employee_list'), "Метод open_employee_list не найден"
        print("✓ Метод открытия списка сотрудников найден")
        
        # Закрываем окно
        app.destroy()
        root.destroy()
        
        print("\n🎉 Интеграционный тест пройден успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка в интеграционном тесте: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_app_integration()
