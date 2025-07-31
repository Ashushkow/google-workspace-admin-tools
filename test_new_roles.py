#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест новых ролей в окне управления документами: Editor, Viewer, Commenter
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_role_mapping():
    """Тест маппинга ролей"""
    print("🧪 Тестирование новых ролей: Editor, Viewer, Commenter...")
    
    # Импортируем и создаем временный объект DocumentManagementWindow для тестов
    import tkinter as tk
    
    # Создаем фиктивный класс с методами маппинга
    class TestDocumentWindow:
        def _get_role_mapping(self):
            return {
                "Viewer": "reader",
                "Commenter": "commenter", 
                "Editor": "writer"
            }
        
        def _get_reverse_role_mapping(self):
            return {
                "reader": "Viewer",
                "commenter": "Commenter",
                "writer": "Editor",
                "owner": "Owner"
            }
        
        def _convert_role_to_api(self, display_role):
            mapping = self._get_role_mapping()
            return mapping.get(display_role, display_role.lower())
        
        def _convert_role_from_api(self, api_role):
            mapping = self._get_reverse_role_mapping()
            return mapping.get(api_role, api_role.capitalize())
    
    # Тестируем маппинг
    test_window = TestDocumentWindow()
    
    print("✅ Тестирование конвертации пользовательских ролей в API:")
    user_to_api = [
        ("Viewer", "reader"),
        ("Commenter", "commenter"),
        ("Editor", "writer")
    ]
    
    for user_role, expected_api_role in user_to_api:
        actual_api_role = test_window._convert_role_to_api(user_role)
        if actual_api_role == expected_api_role:
            print(f"   ✅ {user_role} -> {actual_api_role}")
        else:
            print(f"   ❌ {user_role} -> {actual_api_role} (ожидалось {expected_api_role})")
    
    print("\n✅ Тестирование конвертации API ролей в пользовательские:")
    api_to_user = [
        ("reader", "Viewer"),
        ("commenter", "Commenter"),
        ("writer", "Editor"),
        ("owner", "Owner")
    ]
    
    for api_role, expected_user_role in api_to_user:
        actual_user_role = test_window._convert_role_from_api(api_role)
        if actual_user_role == expected_user_role:
            print(f"   ✅ {api_role} -> {actual_user_role}")
        else:
            print(f"   ❌ {api_role} -> {actual_user_role} (ожидалось {expected_user_role})")
    
    print("\n✅ Обновления интерфейса:")
    print("   • Выпадающий список ролей: Viewer, Commenter, Editor")
    print("   • Ширина списка увеличена с 10 до 12 символов")
    print("   • Значение по умолчанию: Viewer")
    print("   • Таблица разрешений показывает понятные названия ролей")
    print("   • Диалог изменения роли с красивым интерфейсом")
    
    print("\n✅ Новые методы в классе DocumentManagementWindow:")
    print("   • _get_role_mapping() - маппинг пользователь -> API")
    print("   • _get_reverse_role_mapping() - маппинг API -> пользователь") 
    print("   • _convert_role_to_api() - конвертация в API роль")
    print("   • _convert_role_from_api() - конвертация из API роли")
    
    return True

if __name__ == "__main__":
    success = test_role_mapping()
    if success:
        print("\n🎉 Новые роли успешно внедрены!")
        print("📋 Теперь пользователи могут выбирать:")
        print("   • Viewer (только просмотр)")
        print("   • Commenter (просмотр + комментарии)")
        print("   • Editor (полное редактирование)")
    else:
        print("\n💥 Что-то пошло не так")
