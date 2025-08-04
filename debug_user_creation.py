#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диагностика проблемы с созданием пользователя
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def debug_api_connection():
    """Проверяем подключение к Google API"""
    print("🔍 ДИАГНОСТИКА ПОДКЛЮЧЕНИЯ К GOOGLE API")
    print("=" * 60)
    
    try:
        # 1. Проверяем импорт модулей
        print("1. Проверка импорта модулей...")
        from src.auth import get_service, detect_credentials_type
        from src.api.users_api import user_exists
        print("   ✅ Модули импортированы успешно")
        
        # 2. Проверяем тип credentials
        print("\n2. Проверка типа credentials...")
        creds_type = detect_credentials_type()
        print(f"   📋 Тип credentials: {creds_type}")
        
        # 3. Проверяем получение сервиса
        print("\n3. Попытка получить Google API сервис...")
        service = get_service()
        if service:
            print("   ✅ Google API сервис получен успешно")
        else:
            print("   ❌ Не удалось получить Google API сервис")
            return False
            
        # 4. Тестируем простой API вызов
        print("\n4. Тестируем простой API вызов...")
        try:
            # Попробуем получить информацию о домене
            domains = service.domains().list(customer='my_customer').execute()
            print(f"   ✅ API вызов успешен, найдено доменов: {len(domains.get('domains', []))}")
            
            for domain in domains.get('domains', []):
                print(f"      • {domain.get('domainName')} (верифицирован: {domain.get('verified')})")
                
        except Exception as e:
            print(f"   ❌ Ошибка API вызова: {e}")
            return False
        
        # 5. Тестируем функцию user_exists с несуществующим пользователем
        print("\n5. Тестируем функцию user_exists...")
        test_email = "nonexistent.user.test123@sputnik8.com"
        print(f"   📧 Тестовый email: {test_email}")
        
        try:
            result = user_exists(service, test_email)
            print(f"   📊 Результат user_exists: {result}")
            
            if result is None:
                print("   ❌ Функция user_exists вернула None - есть проблема с API")
                return False
            elif result is False:
                print("   ✅ Функция user_exists работает корректно (пользователь не найден)")
            else:
                print("   ⚠️ Неожиданно: тестовый пользователь существует")
                
        except Exception as e:
            print(f"   ❌ Ошибка в user_exists: {e}")
            return False
        
        print("\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_user_creation_error():
    """Специфическая диагностика ошибки создания пользователя"""
    print("\n🛠️ ДИАГНОСТИКА ОШИБКИ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)
    
    try:
        from src.auth import get_service
        from src.api.users_api import user_exists, create_user
        
        service = get_service()
        if not service:
            print("❌ Не удалось получить Google API сервис")
            return False
        
        # Тестируем с разными сценариями
        test_cases = [
            "test.nonexistent.user1@sputnik8.com",
            "another.test.user2@sputnik8.com", 
            "debug.user.test@sputnik8.com"
        ]
        
        for i, test_email in enumerate(test_cases, 1):
            print(f"\n📧 Тест {i}: {test_email}")
            
            try:
                # Проверяем существование
                exists = user_exists(service, test_email)
                print(f"   🔍 user_exists результат: {exists}")
                
                if exists is None:
                    print(f"   ❌ Проблема: user_exists вернул None для {test_email}")
                    print("   🔧 Возможные причины:")
                    print("      - Проблема с API токеном/credentials")
                    print("      - Недостаточно прав доступа")
                    print("      - Проблема с сетевым подключением")
                    print("      - Ошибка в Google API")
                    return False
                elif exists is True:
                    print(f"   ℹ️ Пользователь {test_email} уже существует")
                else:
                    print(f"   ✅ Пользователь {test_email} не существует - можно создавать")
                    
            except Exception as e:
                print(f"   ❌ Ошибка при проверке {test_email}: {e}")
                return False
        
        print("\n🎯 ДИАГНОСТИКА ЗАВЕРШЕНА")
        print("   Если все тесты прошли успешно, проблема может быть в:")
        print("   1. Конкретном email пользователя")
        print("   2. Временных проблемах с Google API") 
        print("   3. Ограничениях квот API")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка диагностики: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 ЗАПУСК ДИАГНОСТИКИ ОШИБКИ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 70)
    
    # Основная диагностика
    api_ok = debug_api_connection()
    
    if api_ok:
        # Специфическая диагностика создания пользователя
        debug_user_creation_error()
    else:
        print("\n❌ ОСНОВНАЯ ДИАГНОСТИКА НЕ ПРОЙДЕНА")
        print("   Необходимо сначала исправить проблемы с API подключением")
        
    print("\n" + "=" * 70)
    print("🏁 ДИАГНОСТИКА ЗАВЕРШЕНА")
