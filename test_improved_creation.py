#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест улучшенной функции создания пользователя с retry логикой
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.auth import get_service
    from src.api.users_api import create_user, user_exists
    
    print("🧪 ТЕСТ УЛУЧШЕННОЙ ФУНКЦИИ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)
    
    service = get_service()
    
    # Тестируем с новыми адресами
    test_emails = [
        "test.retry.logic1@sputnik8.com",
        "test.retry.logic2@sputnik8.com"
    ]
    
    for i, test_email in enumerate(test_emails, 1):
        print(f"\\n{i}. Тест создания: {test_email}")
        
        # Сначала проверим существование
        exists = user_exists(service, test_email) 
        print(f"   📊 user_exists: {exists}")
        
        if exists is False:
            print("   🚀 Попытка создания с улучшенной логикой...")
            
            result = create_user(
                service=service,
                email=test_email,
                first_name="Test",
                last_name="Retry",
                password="RetryTest123!",
                org_unit_path="/"
            )
            
            print(f"   📊 Результат: {result}")
            
            if "создан" in result.lower():
                print("   ✅ Создание успешно!")
            elif "Не удалось проверить существование" in result:
                print("   ❌ Ошибка все еще возникает")
            elif "восстановить" in result:
                print("   🔄 Сработала логика восстановления")
            else:
                print(f"   ℹ️ Другой результат: {result}")
        else:
            print("   ℹ️ Пользователь существует или ошибка проверки")
    
    print("\\n" + "=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЕН")
    
    print("\\n💡 ЕСЛИ ПРОБЛЕМА ВСЕ ЕЩЕ ВОЗНИКАЕТ В GUI:")
    print("   1. Проблема может быть в конкретном email")
    print("   2. Истечение OAuth токена во время работы")
    print("   3. Превышение квот Google API")
    print("   4. Временные проблемы с сетью")
    print()
    print("🛠️ ДОПОЛНИТЕЛЬНЫЕ УЛУЧШЕНИЯ:")
    print("   ✅ Добавлена retry логика в user_exists (3 попытки)")
    print("   ✅ Добавлено восстановление сервиса в create_user")
    print("   ✅ Улучшено логирование ошибок")
    print("   ✅ Добавлены временные задержки между попытками")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
