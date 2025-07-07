# -*- coding: utf-8 -*-
"""
Простой тест окна сотрудников
"""

import tkinter as tk
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockService:
    """Мок сервиса для тестирования"""
    pass

def test_employee_window():
    """Тестируем создание окна сотрудников"""
    try:
        from employee_list_window import EmployeeListWindow
        from ui_components import ModernColors
        
        print("✓ Импорт модулей успешен")
        
        # Создаем главное окно для теста
        root = tk.Tk()
        root.withdraw()
        
        # Создаем мок сервиса
        mock_service = MockService()
        
        # Создаем окно сотрудников
        employee_window = EmployeeListWindow(root, mock_service)
        print("✓ Окно сотрудников создано успешно")
        
        # Проверяем, что переменные фильтров инициализированы
        assert hasattr(employee_window, 'search_var'), "search_var не найден"
        assert hasattr(employee_window, 'status_var'), "status_var не найден"
        assert hasattr(employee_window, 'orgunit_var'), "orgunit_var не найден"
        assert hasattr(employee_window, 'date_from_var'), "date_from_var не найден"
        assert hasattr(employee_window, 'date_to_var'), "date_to_var не найден"
        print("✓ Переменные фильтров инициализированы")
        
        # Проверяем, что методы фильтрации существуют
        assert hasattr(employee_window, 'apply_filters'), "apply_filters не найден"
        assert hasattr(employee_window, 'reset_filters'), "reset_filters не найден"
        print("✓ Методы фильтрации найдены")
        
        # Тестируем установку значений фильтров
        employee_window.search_var.set("test")
        employee_window.status_var.set("Active")
        employee_window.orgunit_var.set("IT")
        print("✓ Установка значений фильтров работает")
        
        # Закрываем окно
        employee_window.destroy()
        root.destroy()
        
        print("\n🎉 Все тесты пройдены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_employee_window()
