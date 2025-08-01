#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки интеграции с "Моей Командой"
"""

import tkinter as tk
from src.ui.myteam_user_window import open_myteam_user_window
from src.api.myteam_api import create_myteam_api, MyTeamUser, validate_myteam_user_data

def test_api_without_token():
    """Тестирует API без токена"""
    print("🔧 Тестирование API без токена...")
    
    api_client = create_myteam_api("")
    result = api_client.test_connection()
    
    print(f"✅ Результат тестирования: {result}")
    print(f"   Успешность: {result['success']}")
    print(f"   Endpoints: {list(result['endpoints'].keys())}")
    
    for endpoint, data in result['endpoints'].items():
        status = "✅ Доступен" if data.get('accessible') else "❌ Недоступен"
        auth_req = " (требует авторизацию)" if data.get('requires_auth') else ""
        print(f"     {endpoint}: {status}{auth_req}")

def test_user_validation():
    """Тестирует валидацию пользователя"""
    print("\n🔧 Тестирование валидации данных пользователя...")
    
    # Правильные данные
    result1 = validate_myteam_user_data(
        email="test@sputnik8.com",
        first_name="Иван",
        last_name="Петров",
        phone="+7 (999) 123-45-67",
        department="IT",
        position="Разработчик"
    )
    print(f"✅ Правильные данные: {result1}")
    
    # Неправильные данные
    result2 = validate_myteam_user_data(
        email="invalid-email",
        first_name="",
        last_name="Петров",
        phone="abc",
        department="IT",
        position="Разработчик"
    )
    print(f"❌ Неправильные данные: {result2}")

def test_ui_window():
    """Тестирует UI окно"""
    print("\n🔧 Тестирование UI окна...")
    
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    
    def on_created():
        print("✅ Callback: Пользователь создан!")
    
    window = open_myteam_user_window(
        master=root,
        api_token="",  # Пустой токен для теста
        on_created=on_created
    )
    
    if window:
        print("✅ Окно открыто успешно")
        print("ℹ️  Закройте окно для завершения теста")
        root.mainloop()
    else:
        print("❌ Не удалось открыть окно")

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С \"МОЕЙ КОМАНДОЙ\"\n")
    
    try:
        # Тестируем API
        test_api_without_token()
        
        # Тестируем валидацию
        test_user_validation()
        
        # Спрашиваем пользователя о тестировании UI
        print("\n❓ Хотите протестировать UI окно? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes', 'да', 'д']:
            test_ui_window()
        
        print("\n✅ Тестирование завершено!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()