#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест функций работы с пользователями и OU.
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.api.orgunits_api import (
    list_orgunits, 
    get_user_orgunit, 
    get_display_name_for_orgunit_path,
    get_orgunit_path_from_display_name
)
from src.api.users_api import get_user_list
from src.auth import get_service


def get_users_direct(service):
    """Получает пользователей напрямую через Google API"""
    try:
        results = service.users().list(customer='my_customer', maxResults=50).execute()
        return results.get('users', [])
    except Exception as e:
        print(f"Ошибка получения пользователей: {e}")
        return []


def test_user_ou_functions():
    """Тестирует функции работы с пользователями и OU"""
    try:
        print("🔧 Получение сервиса Google Directory API...")
        service = get_service()
        print(f"🔍 Тип сервиса: {type(service)}")
        
        print("📋 Загрузка пользователей...")
        users = get_users_direct(service)
        print(f"🔍 Тип users: {type(users)}")
        print(f"✅ Найдено {len(users)} пользователей")
        
        print("\n📋 Загрузка OU...")
        orgunits = list_orgunits(service)
        print(f"✅ Найдено {len(orgunits)} подразделений")
        
        # Тестируем функции с первыми 5 пользователями
        print("\n👥 Информация о OU пользователей:")
        for i, user in enumerate(users[:5]):
            email = user.get('primaryEmail', '')
            name = f"{user.get('name', {}).get('givenName', '')} {user.get('name', {}).get('familyName', '')}"
            
            try:
                # Получаем OU пользователя
                user_ou_path = get_user_orgunit(service, email)
                
                # Получаем отображаемое название OU
                display_name = get_display_name_for_orgunit_path(user_ou_path, orgunits)
                
                print(f"  {i+1}. {name} ({email})")
                print(f"     📁 OU: {user_ou_path}")
                print(f"     🎨 Отображение: {display_name}")
                
                # Тестируем обратное преобразование
                back_to_path = get_orgunit_path_from_display_name(display_name, orgunits)
                match_status = "✅" if back_to_path == user_ou_path else "❌"
                print(f"     🔄 Обратное преобразование: {back_to_path} {match_status}")
                
            except Exception as e:
                print(f"     ❌ Ошибка: {e}")
            
            print()
        
        print("✅ Тест завершен успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")


if __name__ == "__main__":
    test_user_ou_functions()
