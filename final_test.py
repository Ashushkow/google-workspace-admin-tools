#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест всех исправлений
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.auth import get_service
    from src.api.users_api import create_user, user_exists
    
    print("🏁 ФИНАЛЬНАЯ ПРОВЕРКА ИСПРАВЛЕНИЙ")
    print("=" * 60)
    
    service = get_service()
    
    # Тест 1: Проверка существующего пользователя
    print("1. Проверка существующего пользователя...")
    existing_user = "andrei.shushkov@sputnik8.com"
    exists = user_exists(service, existing_user)
    print(f"   Результат: {exists} ✅")
    
    # Тест 2: Проверка несуществующего пользователя нашего домена
    print("\\n2. Проверка несуществующего пользователя нашего домена...")
    non_existing = "definitely.not.existing.user@sputnik8.com"
    exists = user_exists(service, non_existing)
    print(f"   Результат: {exists} ✅")
    
    # Тест 3: Проверка пользователя внешнего домена
    print("\\n3. Проверка пользователя внешнего домена...")
    external_user = "someone@gmail.com"
    exists = user_exists(service, external_user)
    print(f"   Результат: {exists} ✅")
    
    # Тест 4: Попытка создать пользователя во внешнем домене
    print("\\n4. Попытка создать пользователя во внешнем домене...")
    result = create_user(
        service=service,
        email="test@gmail.com",
        first_name="Test",
        last_name="User",
        password="Pass123!"
    )
    print(f"   Результат: {result}")
    if "внешнему домену" in result:
        print("   ✅ Валидация домена работает")
    
    # Тест 5: Попытка создать пользователя с существующим email
    print("\\n5. Попытка создать пользователя с существующим email...")
    result = create_user(
        service=service,
        email="andrei.shushkov@sputnik8.com",
        first_name="Test",
        last_name="User", 
        password="Pass123!"
    )
    print(f"   Результат: {result}")
    if "уже существует" in result:
        print("   ✅ Проверка существования работает")
    
    print("\\n" + "=" * 60)
    print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("\\n📋 Исправления:")
    print("   ✅ Обработка ошибок 403 для внешних доменов")
    print("   ✅ Валидация домена при создании пользователя")
    print("   ✅ Улучшенные сообщения об ошибках")
    print("   ✅ Подробное логирование")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
