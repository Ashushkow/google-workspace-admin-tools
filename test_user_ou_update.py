#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест обновления пользователя с изменением OU через API.
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.api.users_api import update_user
from src.api.orgunits_api import get_user_orgunit, list_orgunits, get_display_name_for_orgunit_path
from src.auth import get_service


def test_user_ou_update():
    """Тестирует обновление OU пользователя"""
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
        
        # Выберем целевое OU (например, /HR/Admin)
        target_ou = "/HR/Admin"
        target_display = get_display_name_for_orgunit_path(target_ou, orgunits)
        print(f"🎯 Целевое OU: {target_ou} ({target_display})")
        
        # Проверяем, не находится ли пользователь уже в целевом OU
        if current_ou == target_ou:
            print("⚠️ Пользователь уже находится в целевом OU")
            # Переместим в корневое
            target_ou = "/"
            target_display = "🏠 Корневое подразделение"
            print(f"🎯 Новое целевое OU: {target_ou}")
        
        # Тестируем обновление с изменением OU
        print(f"\n🔄 Перемещаем в OU: {target_ou}")
        fields = {
            'orgUnitPath': target_ou
        }
        
        result = update_user(service, test_email, fields)
        print(f"✅ Результат API: {result}")
        
        # Проверяем, что OU изменилось
        new_ou = get_user_orgunit(service, test_email)
        print(f"📁 OU после обновления: {new_ou}")
        
        success = new_ou == target_ou
        print(f"🔍 OU изменилось корректно: {'✅ Да' if success else '❌ Нет'}")
        
        if success:
            new_display = get_display_name_for_orgunit_path(new_ou, orgunits)
            print(f"🎨 Отображаемое название: {new_display}")
        
        print("\n✅ Тест завершен успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_user_ou_update()
