#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для имитации проблемной ситуации с user_exists
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.auth import get_service
    from src.api.users_api import create_user, user_exists
    
    print("🔍 ТЕСТ ПРОБЛЕМНЫХ СЦЕНАРИЕВ")
    print("=" * 50)
    
    # Получаем сервис
    service = get_service()
    
    # Тестовые сценарии, которые могут вызвать проблемы
    problem_scenarios = [
        # Невалидные email адреса
        "invalid.email@",
        "test@nonexistent-domain-12345.com",
        "@sputnik8.com",
        "test..user@sputnik8.com",
        # Специальные символы
        "test+user@sputnik8.com",
        "test.user+tag@sputnik8.com",
        # Очень длинный email
        "very.long.email.address.that.might.cause.issues.in.api@sputnik8.com",
        # Пустые значения
        "",
        " ",
        # Существующий пользователь (возможно)
        "andrei.shushkov@sputnik8.com"
    ]
    
    print(f"Тестируем {len(problem_scenarios)} проблемных сценариев...")
    
    for i, test_email in enumerate(problem_scenarios, 1):
        print(f"\n{i}. Тест: '{test_email}'")
        
        if not test_email or not test_email.strip():
            print("   ⚠️ Пустой email, пропускаем")
            continue
            
        try:
            result = user_exists(service, test_email)
            print(f"   📊 Результат: {result} (тип: {type(result)})")
            
            if result is None:
                print("   ❌ НАЙДЕНА ПРОБЛЕМА! user_exists вернул None")
                print(f"   🔧 Проблемный email: {test_email}")
                
                # Попробуем понять, в чем проблема
                print("   🔍 Дополнительная диагностика...")
                try:
                    direct_result = service.users().get(userKey=test_email).execute()
                    print(f"   📊 Прямой API вызов успешен: {direct_result.get('primaryEmail')}")
                except Exception as direct_error:
                    print(f"   📊 Прямой API вызов дал ошибку: {direct_error}")
                    print(f"   📊 Тип ошибки: {type(direct_error)}")
                    
            elif result is True:
                print("   ✅ Пользователь существует")
            else:
                print("   ✅ Пользователь не существует")
                
        except Exception as e:
            print(f"   ❌ Ошибка при тестировании: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 ТЕСТ ЗАВЕРШЕН")
    
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()
