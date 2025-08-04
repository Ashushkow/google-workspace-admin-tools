#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест создания пользователя с внешним доменом
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.auth import get_service
    from src.api.users_api import create_user
    
    print("🧪 ТЕСТ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ С ВНЕШНИМ ДОМЕНОМ")
    print("=" * 60)
    
    service = get_service()
    
    # Тестируем с внешним доменом
    external_email = "test.user@external-domain.com"
    print(f"Попытка создать пользователя: {external_email}")
    
    result = create_user(
        service=service,
        email=external_email,
        first_name="Test",
        last_name="User",
        password="TestPassword123!"
    )
    
    print(f"Результат: {result}")
    
    # Тестируем с правильным доменом
    print(f"\nПопытка создать пользователя в правильном домене:")
    correct_email = "test.fix.verification@sputnik8.com"
    
    result2 = create_user(
        service=service,
        email=correct_email,
        first_name="Test",
        last_name="Fix",
        password="TestPassword123!"
    )
    
    print(f"Результат: {result2}")
    
    print("\n" + "=" * 60)
    print("🏁 ТЕСТ ЗАВЕРШЕН")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
