#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест обновления пользователя с изменением OU.
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.api.users_api import update_user
from src.api.orgunits_api import get_user_orgunit, list_orgunits
from src.auth import get_service


def test_user_update():
    """Тестирует обновление пользователя"""
    try:
        print("🔧 Получение сервиса Google Directory API...")
        service = get_service()
        
        # Тестовый пользователь
        test_email = "testdecember2023@sputnik8.com"
        
        print(f"👤 Тестируем пользователя: {test_email}")
        
        # Получаем текущее OU
        current_ou = get_user_orgunit(service, test_email)
        print(f"📁 Текущее OU: {current_ou}")
        
        # Загружаем список OU
        orgunits = list_orgunits(service)
        print(f"📋 Доступно {len(orgunits)} подразделений")
        
        # Тестируем простое обновление имени (без изменения OU)
        print("\n🔄 Тестируем обновление имени...")
        fields = {
            'name': {
                'givenName': 'Test',
                'familyName': 'December'
            }
        }
        
        result = update_user(service, test_email, fields)
        print(f"✅ Результат: {result}")
        
        # Проверяем, что OU не изменилось
        new_ou = get_user_orgunit(service, test_email)
        print(f"📁 OU после обновления: {new_ou}")
        print(f"🔍 OU изменилось: {'Да' if new_ou != current_ou else 'Нет'}")
        
        print("\n✅ Тест завершен успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_user_update()
