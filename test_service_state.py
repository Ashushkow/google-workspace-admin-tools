#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест состояния сервиса в GUI режиме
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.auth import get_service
    from src.api.users_api import create_user, user_exists
    import time
    
    print("🔍 ТЕСТ СОСТОЯНИЯ API СЕРВИСА")
    print("=" * 60)
    
    # Получаем сервис как в GUI
    print("1. Получение сервиса (как в GUI)...")
    service = get_service()
    
    if not service:
        print("❌ Не удалось получить сервис")
        exit(1)
    
    print("✅ Сервис получен")
    
    # Тестируем несколько раз с небольшими паузами
    test_emails = [
        "test.state.check1@sputnik8.com",
        "test.state.check2@sputnik8.com", 
        "test.state.check3@sputnik8.com"
    ]
    
    for i, test_email in enumerate(test_emails, 1):
        print(f"\\n{i}. Тест с {test_email}...")
        
        # Проверяем существование
        print("   🔍 Проверка существования...")
        try:
            exists = user_exists(service, test_email)
            print(f"   📊 user_exists результат: {exists}")
            
            if exists is None:
                print("   ❌ ПРОБЛЕМА! user_exists вернул None")
                
                # Попробуем получить новый сервис
                print("   🔄 Попытка получить новый сервис...")
                new_service = get_service()
                
                if new_service:
                    exists_new = user_exists(new_service, test_email)
                    print(f"   📊 С новым сервисом: {exists_new}")
                    
                    if exists_new is not None:
                        print("   💡 Проблема была в состоянии старого сервиса!")
                        service = new_service  # Обновляем сервис
                    else:
                        print("   ❌ Проблема сохраняется с новым сервисом")
                else:
                    print("   ❌ Не удалось получить новый сервис")
                    
            elif exists is False:
                print("   ✅ Пользователь не существует - можно тестировать создание")
                
                # Тестируем создание
                print("   🚀 Попытка создания...")
                result = create_user(
                    service=service,
                    email=test_email,
                    first_name="Test",
                    last_name="State",
                    password="StateTest123!",
                    org_unit_path="/"
                )
                
                print(f"   📊 Результат: {result}")
                
                if "Не удалось проверить существование" in result:
                    print("   ❌ ПРОБЛЕМА ВОСПРОИЗВЕДЕНА в create_user!")
                    print("   🔍 create_user получил None от внутреннего вызова user_exists")
                elif "создан" in result.lower():
                    print("   ✅ Создание прошло успешно")
                else:
                    print(f"   ℹ️ Другой результат: {result}")
                    
            else:
                print("   ℹ️ Пользователь уже существует")
        
        except Exception as e:
            print(f"   ❌ Ошибка при тестировании: {e}")
        
        # Небольшая пауза между тестами
        if i < len(test_emails):
            print("   ⏳ Пауза 2 секунды...")
            time.sleep(2)
    
    print("\\n" + "=" * 60)
    print("🎯 ЗАКЛЮЧЕНИЕ:")
    print("   Если все тесты прошли успешно, проблема может быть:")
    print("   1. В конкретном состоянии GUI приложения")
    print("   2. В истечении OAuth токена во время работы")
    print("   3. В проблемах с сетевым подключением")
    print("   4. В превышении квот Google API")
    print()
    print("💡 РЕКОМЕНДАЦИИ:")
    print("   1. Добавить обновление сервиса при ошибках")
    print("   2. Добавить retry логику")
    print("   3. Добавить валидацию состояния сервиса")
    
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()
