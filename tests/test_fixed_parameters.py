#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления проблемы с перепутанными параметрами.
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.auth import get_service
from src.api.groups_api import add_user_to_group
from src.config.enhanced_config import config


def test_fixed_parameters():
    """Тестирование исправления порядка параметров"""
    print("🔧 ТЕСТ ИСПРАВЛЕНИЯ ПЕРЕПУТАННЫХ ПАРАМЕТРОВ")
    print("=" * 60)
    
    try:
        service = get_service()
        
        # Тестовые данные
        test_user = "testdecember2023@sputnik8.com"
        test_group = "admin_team@sputnik8.com"
        
        print(f"👤 Пользователь: {test_user}")
        print(f"👥 Группа: {test_group}")
        print()
        
        # Тестируем с правильным порядком параметров
        print("🚀 Попытка добавления с ПРАВИЛЬНЫМ порядком параметров...")
        print(f"   Вызов: add_user_to_group(service, group_email='{test_group}', user_email='{test_user}')")
        
        try:
            result = add_user_to_group(service, test_group, test_user)
            print(f"✅ Результат: {result}")
            
            if "403" not in str(result) and "Not Authorized" not in str(result):
                print("🎉 УСПЕХ: Ошибка 403 исчезла!")
                return True
            else:
                print("❌ Ошибка 403 все еще присутствует")
                return False
                
        except Exception as e:
            print(f"❌ Исключение: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False


def test_wrong_parameters():
    """Демонстрация проблемы с неправильным порядком (для сравнения)"""
    print("\n🚫 ДЕМОНСТРАЦИЯ ПРОБЛЕМЫ С НЕПРАВИЛЬНЫМ ПОРЯДКОМ")
    print("=" * 60)
    
    try:
        service = get_service()
        
        test_user = "testdecember2023@sputnik8.com"
        test_group = "admin_team@sputnik8.com"
        
        print("❌ Что происходило РАНЬШЕ (неправильный порядок):")
        print(f"   Вызов: add_user_to_group(service, user_email='{test_user}', group_email='{test_group}')")
        print(f"   Результат: API пытался найти группу '{test_user}' (которая не существует)")
        print(f"   Ошибка: 403 'Not Authorized to access this resource/api'")
        print()
        print("✅ Что происходит СЕЙЧАС (правильный порядок):")
        print(f"   Вызов: add_user_to_group(service, group_email='{test_group}', user_email='{test_user}')")
        print(f"   Результат: API ищет группу '{test_group}' (которая существует)")
        print(f"   Ожидаемый результат: Успешное добавление или корректная ошибка")
        
    except Exception as e:
        print(f"❌ Ошибка демонстрации: {e}")


def main():
    print("🔍 ПРОВЕРКА ИСПРАВЛЕНИЯ ПРОБЛЕМЫ С ПАРАМЕТРАМИ")
    print("=" * 60)
    
    # Демонстрируем проблему
    test_wrong_parameters()
    
    # Тестируем исправление
    success = test_fixed_parameters()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ПРОБЛЕМА ИСПРАВЛЕНА!")
        print("✅ Теперь добавление пользователей в группы должно работать корректно")
        print("📋 Порядок параметров исправлен в файлах:")
        print("   - src/ui/group_management.py")
        print("   - src/ui/additional_windows.py")
    else:
        print("⚠️ Требуется дополнительная диагностика")
        print("💡 Возможно, есть другие проблемы с правами доступа")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
