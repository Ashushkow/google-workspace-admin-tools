#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест создания пользователя с secondary email Gmail
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.auth import get_service
    from src.api.users_api import create_user
    
    print("🧪 ТЕСТ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ С SECONDARY EMAIL GMAIL")
    print("=" * 60)
    
    service = get_service()
    
    # Тестируем создание пользователя с правильным primary email и Gmail secondary
    print("Попытка создать пользователя:")
    print("  Primary email: test.secondary.gmail@sputnik8.com")
    print("  Secondary email: recovery.email@gmail.com")
    
    result = create_user(
        service=service,
        email="test.secondary.gmail@sputnik8.com",  # Правильный домен
        first_name="Test",
        last_name="SecondaryGmail", 
        password="TestPassword123!",
        secondary_email="recovery.email@gmail.com",  # Gmail для восстановления
        org_unit_path="/"
    )
    
    print(f"\nРезультат: {result}")
    
    if "создан" in result.lower():
        print("✅ Пользователь создан успешно!")
        print("✅ Secondary email Gmail работает корректно")
    elif "внешнему домену" in result:
        print("❌ ПРОБЛЕМА: Валидация неправильно обрабатывает secondary email")
        print("💡 Нужно исправить валидацию в create_user")
    else:
        print(f"ℹ️ Другой результат: {result}")
    
    print("\n" + "=" * 60)
    print("🏁 ТЕСТ ЗАВЕРШЕН")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
