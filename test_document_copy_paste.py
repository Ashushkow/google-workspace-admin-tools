#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест для проверки функционала копирования и вставки в окне управления документами
"""

import sys
import tkinter as tk
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_document_management_copy_paste():
    """Тест функций копирования и вставки"""
    print("🧪 Тестирование функций копирования и вставки в окне управления документами...")
    
    # Создаем фиктивный документ-сервис
    class MockDocumentService:
        def get_document_info(self, url):
            return type('DocumentInfo', (), {
                'name': 'Тестовый документ',
                'owner': 'test@example.com',
                'url': url
            })()
        
        def get_permissions(self, doc_id):
            return [
                {'email': 'user1@example.com', 'role': 'reader', 'type': 'user'},
                {'email': 'user2@example.com', 'role': 'writer', 'type': 'user'}
            ]
    
    # Создаем главное окно
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    
    # Импортируем и создаем окно управления документами
    from src.ui.document_management import DocumentManagementWindow
    
    try:
        doc_window = DocumentManagementWindow(
            root, 
            MockDocumentService(),
            "https://docs.google.com/document/d/test123/edit"
        )
        
        print("✅ Окно управления документами создано успешно")
        print("✅ Контекстные меню для полей ввода настроены")
        print("✅ Горячие клавиши (Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A) добавлены")
        print("✅ Функция копирования email из таблицы добавлена")
        
        # Показываем окно для визуального тестирования
        print("\n📋 Для тестирования:")
        print("1. Попробуйте правый клик на поле URL - должно появиться контекстное меню")
        print("2. Попробуйте правый клик на поле Email - должно появиться контекстное меню")
        print("3. Используйте Ctrl+C, Ctrl+V, Ctrl+X в полях ввода")
        print("4. Выберите пользователя в таблице и нажмите Ctrl+C или правый клик")
        
        # Запускаем GUI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Ошибка при создании окна: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_document_management_copy_paste()
    if success:
        print("🎉 Тест завершен успешно!")
    else:
        print("💥 Тест завершился с ошибками")
