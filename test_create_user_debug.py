#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест воспроизведения ошибки создания пользователя
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.auth import get_service
    from src.api.users_api import create_user, user_exists
    
    print("🧪 ТЕСТ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 50)
    
    # Получаем сервис
    print("1. Получение Google API сервиса...")
    service = get_service()
    
    if not service:
        print("❌ Не удалось получить сервис")
        exit(1)
    
    print("✅ Сервис получен")
    
    # Тестовые данные
    test_email = "test.debug.user.creation@sputnik8.com"
    first_name = "Test"
    last_name = "User"
    password = "TestPassword123!"
    
    print(f"\n2. Тестирование создания пользователя: {test_email}")
    
    # Сначала проверим существование
    print("   🔍 Проверка существования пользователя...")
    exists = user_exists(service, test_email)
    print(f"   📊 Результат user_exists: {exists} (тип: {type(exists)})")
    
    if exists is None:
        print("   ❌ ПРОБЛЕМА: user_exists вернул None!")
        print("   🔧 Это означает ошибку в API запросе")
        exit(1)
    elif exists is True:
        print("   ⚠️ Пользователь уже существует, удалим его сначала...")
        # Здесь можно добавить логику удаления, но пока пропустим
        print("   (Пропускаем тест создания, так как пользователь существует)")
        exit(0)
    else:
        print("   ✅ Пользователь не существует, можно создавать")
    
    # Теперь пытаемся создать пользователя
    print("\n   🚀 Создание пользователя...")
    result = create_user(
        service=service,
        email=test_email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        org_unit_path="/"
    )
    
    print(f"   📊 Результат создания: {result}")
    
    if "Ошибка: Не удалось проверить существование пользователя" in result:
        print("   ❌ ВОСПРОИЗВЕДЕНА ОШИБКА!")
        print("   🔍 Начинаем углубленную диагностику...")
        
        # Повторим проверку существования с подробным логированием
        print("\n3. Углубленная диагностика user_exists...")
        
        import traceback
        
        try:
            # Попробуем прямой API вызов
            print("   🔧 Прямой API вызов users().get()...")
            user_info = service.users().get(userKey=test_email).execute()
            print(f"   📊 Неожиданно: пользователь найден! {user_info.get('primaryEmail')}")
        except Exception as e:
            print(f"   📊 Ожидаемая ошибка: {e}")
            print(f"   📊 Тип ошибки: {type(e)}")
            
            # Детальный анализ ошибки
            if hasattr(e, 'resp'):
                print(f"   📊 HTTP статус: {getattr(e.resp, 'status', 'N/A')}")
            
            if 'notFound' in str(e) or '404' in str(e):
                print("   ✅ Это нормальная ошибка 'not found'")
            else:
                print("   ⚠️ Это НЕ стандартная ошибка 'not found'")
                print("   🔧 Полная информация об ошибке:")
                traceback.print_exc()
    else:
        print("   📊 Результат не содержит ошибку, проверяем успешность...")
        
        if "создан" in result.lower():
            print("   ✅ Пользователь создан успешно!")
        else:
            print(f"   ⚠️ Неожиданный результат: {result}")
    
    print("\n" + "=" * 50)
    print("🏁 ТЕСТ ЗАВЕРШЕН")
    
except Exception as e:
    print(f"❌ Критическая ошибка теста: {e}")
    import traceback
    traceback.print_exc()
