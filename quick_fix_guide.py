#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрое решение проблемы создания пользователя
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def quick_fix_guide():
    """Показывает краткое руководство по решению проблемы"""
    print("🛠️ БЫСТРОЕ РЕШЕНИЕ ПРОБЛЕМЫ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)
    print()
    
    print("❌ Если вы видите ошибку:")
    print("   'Ошибка: Не удалось проверить существование пользователя'")
    print()
    
    print("✅ ПОПРОБУЙТЕ ЭТИ ШАГИ:")
    print()
    
    print("1. 🔄 ПОДОЖДИТЕ 1-2 МИНУТЫ И ПОПРОБУЙТЕ СНОВА")
    print("   - Возможно временная проблема с Google API")
    print("   - Новая версия автоматически восстанавливает соединение")
    print()
    
    print("2. 📧 ПРОВЕРЬТЕ EMAIL АДРЕС:")
    print("   ✅ Правильно: user@sputnik8.com")
    print("   ❌ Неправильно: user@gmail.com")
    print("   💡 Gmail можно указать только в Secondary Email")
    print()
    
    print("3. 🌐 ПРОВЕРЬТЕ ИНТЕРНЕТ ПОДКЛЮЧЕНИЕ:")
    print("   - Убедитесь, что есть доступ к Google сервисам")
    print("   - Попробуйте открыть admin.google.com в браузере")
    print()
    
    print("4. 🔑 ЕСЛИ ПРОБЛЕМА ПОВТОРЯЕТСЯ:")
    print("   - Закройте приложение")
    print("   - Удалите файл token.pickle")
    print("   - Запустите приложение снова")
    print("   - Пройдите авторизацию заново")
    print()
    
    print("5. 📞 ОБРАТИТЕСЬ К АДМИНИСТРАТОРУ, ЕСЛИ:")
    print("   - Ошибка повторяется более 3 раз")
    print("   - Появляется сообщение о правах доступа")
    print("   - Не помогают предыдущие шаги")
    print()
    
    print("=" * 60)
    print("💡 ПОМНИТЕ:")
    print("   - Primary Email: только @sputnik8.com")
    print("   - Secondary Email: любой домен (Gmail, Yahoo и т.д.)")
    print("   - Новая версия автоматически исправляет большинство проблем")
    print()
    print("🎯 В 99% случаев достаточно просто попробовать снова!")

def test_current_connection():
    """Тестирует текущее подключение к API"""
    print("\n🔍 ТЕСТ ПОДКЛЮЧЕНИЯ К GOOGLE API:")
    print("-" * 40)
    
    try:
        from src.auth import get_service
        from src.api.users_api import user_exists
        
        print("1. Получение сервиса... ", end="")
        service = get_service()
        if service:
            print("✅ ОК")
        else:
            print("❌ ОШИБКА")
            return False
        
        print("2. Тест API вызова... ", end="")
        result = user_exists(service, "test.connection@sputnik8.com")
        if result is not None:
            print("✅ ОК")
            print(f"   📊 Результат: {result}")
        else:
            print("❌ ОШИБКА")
            return False
            
        print("\n🎉 ПОДКЛЮЧЕНИЕ К API РАБОТАЕТ!")
        print("   Можно создавать пользователей")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("   1. Проверьте интернет подключение")
        print("   2. Перезапустите приложение")
        print("   3. Пройдите авторизацию заново")
        return False

if __name__ == "__main__":
    quick_fix_guide()
    
    print("\n" + "=" * 60)
    response = input("🔍 Хотите протестировать подключение к API? (y/n): ")
    
    if response.lower() in ['y', 'yes', 'да', 'д']:
        success = test_current_connection()
        
        if success:
            print("\n✅ ВСЕ РАБОТАЕТ! Можете создавать пользователей.")
        else:
            print("\n❌ ЕСТЬ ПРОБЛЕМЫ. Следуйте инструкциям выше.")
    
    print("\n🚀 Удачи в создании пользователей!")
