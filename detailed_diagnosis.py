#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детальная диагностика ошибки создания пользователя
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.auth import get_service
    from src.api.users_api import create_user, user_exists
    
    print("🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА ОШИБКИ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 70)
    
    service = get_service()
    
    # Запрашиваем у пользователя конкретный email, с которым возникает проблема
    print("📧 Введите email пользователя, при создании которого возникает ошибка:")
    print("   (или нажмите Enter для использования тестового email)")
    
    user_input = input("Email: ").strip()
    
    if not user_input:
        test_email = "test.debug.creation.issue@sputnik8.com"
        print(f"   Используем тестовый email: {test_email}")
    else:
        test_email = user_input
        print(f"   Используем введенный email: {test_email}")
    
    print("\n" + "=" * 70)
    print("🔍 ПОШАГОВАЯ ДИАГНОСТИКА:")
    print("=" * 70)
    
    # Шаг 1: Валидация email
    print("\\n1. Проверка валидности email...")
    if not test_email or '@' not in test_email:
        print("   ❌ Неверный формат email")
        exit(1)
    
    email_domain = test_email.split('@')[-1]
    print(f"   📧 Email: {test_email}")
    print(f"   🌐 Домен: {email_domain}")
    
    if email_domain != "sputnik8.com":
        print(f"   ⚠️ Внешний домен: {email_domain}")
    else:
        print("   ✅ Домен корректный: sputnik8.com")
    
    # Шаг 2: Проверка существования
    print("\\n2. Проверка существования пользователя...")
    try:
        exists = user_exists(service, test_email)
        print(f"   📊 Результат user_exists: {exists}")
        print(f"   📊 Тип результата: {type(exists)}")
        
        if exists is None:
            print("   ❌ ПРОБЛЕМА НАЙДЕНА! user_exists вернул None")
            print("   🔧 Это означает ошибку API при проверке существования")
            
            # Дополнительная диагностика
            print("\\n   🔍 Дополнительная диагностика ошибки...")
            try:
                print("   📞 Прямой вызов Google API...")
                direct_result = service.users().get(userKey=test_email).execute()
                print(f"   📊 Неожиданно: пользователь найден через прямой API!")
                print(f"   📧 Primary email: {direct_result.get('primaryEmail')}")
            except Exception as direct_error:
                print(f"   📊 Прямой API дал ошибку (ожидаемо): {type(direct_error).__name__}")
                print(f"   📊 Детали ошибки: {str(direct_error)}")
                
                # Анализируем тип ошибки
                error_str = str(direct_error).lower()
                if '403' in error_str or 'forbidden' in error_str:
                    print("   🔍 Ошибка 403: Нет прав доступа")
                    if email_domain != "sputnik8.com":
                        print("   💡 Это внешний домен - такая ошибка нормальна")
                        print("   ❌ НО! Функция user_exists должна была вернуть False")
                    else:
                        print("   ❌ Нет прав доступа к пользователю в нашем домене!")
                elif '404' in error_str or 'not found' in error_str:
                    print("   ✅ Ошибка 404: Пользователь не найден (нормально)")
                    print("   ❌ НО! Функция user_exists должна была вернуть False")
                else:
                    print("   ⚠️ Неизвестный тип ошибки")
                    
        elif exists is True:
            print("   ℹ️ Пользователь уже существует")
        else:
            print("   ✅ Пользователь не существует - можно создавать")
            
    except Exception as e:
        print(f"   ❌ Ошибка при вызове user_exists: {e}")
        exit(1)
    
    # Шаг 3: Попытка создания (если пользователь не существует)
    if exists is False:
        print("\\n3. Попытка создания пользователя...")
        try:
            result = create_user(
                service=service,
                email=test_email,
                first_name="Test",
                last_name="Debug", 
                password="TestPass123!",
                org_unit_path="/"
            )
            
            print(f"   📊 Результат создания: {result}")
            
            if "Не удалось проверить существование" in result:
                print("   ❌ ПРОБЛЕМА ВОСПРОИЗВЕДЕНА!")
                print("   🔧 Функция create_user получила None от user_exists")
            elif "создан" in result.lower():
                print("   ✅ Пользователь создан успешно!")
            else:
                print(f"   ℹ️ Другой результат: {result}")
                
        except Exception as e:
            print(f"   ❌ Ошибка при создании: {e}")
    else:
        print("\\n3. Создание пропущено (пользователь существует или ошибка проверки)")
    
    print("\\n" + "=" * 70)
    print("🎯 ЗАКЛЮЧЕНИЕ:")
    
    if exists is None:
        print("❌ НАЙДЕНА ПРОБЛЕМА в функции user_exists!")
        print("💡 Рекомендации:")
        print("   1. Проверьте права доступа к Google Workspace API")
        print("   2. Убедитесь, что OAuth токен не истек")
        print("   3. Проверьте квоты Google API")
        print("   4. Попробуйте пересоздать токен авторизации")
    else:
        print("✅ Функция user_exists работает корректно")
        print("💡 Если проблема все еще возникает:")
        print("   1. Проблема может быть с конкретным email")
        print("   2. Временные проблемы с Google API")
        print("   3. Превышение лимитов API")
    
except Exception as e:
    print(f"❌ Критическая ошибка диагностики: {e}")
    import traceback
    traceback.print_exc()
