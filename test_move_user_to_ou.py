#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест перемещения пользователя через специальную функцию move_user_to_orgunit.
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.api.orgunits_api import move_user_to_orgunit, get_user_orgunit, list_orgunits, get_display_name_for_orgunit_path
from src.auth import get_service


def test_move_user_to_ou():
    """Тестирует перемещение пользователя в OU"""
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
        
        # Выберем целевое OU
        target_ou = "/HR/Admin"
        
        # Проверяем, не находится ли пользователь уже в целевом OU
        if current_ou == target_ou:
            print("⚠️ Пользователь уже находится в целевом OU")
            # Переместим в корневое
            target_ou = "/"
            print(f"🎯 Новое целевое OU: {target_ou}")
        
        target_display = get_display_name_for_orgunit_path(target_ou, orgunits)
        print(f"🎯 Целевое OU: {target_ou} ({target_display})")
        
        # Используем специальную функцию перемещения
        print(f"\n🔄 Перемещаем пользователя через move_user_to_orgunit...")
        result = move_user_to_orgunit(service, test_email, target_ou)
        
        print(f"✅ Результат операции:")
        print(f"   Успешно: {result['success']}")
        print(f"   Сообщение: {result['message']}")
        
        if result['success']:
            # Проверяем, что OU изменилось
            new_ou = get_user_orgunit(service, test_email)
            print(f"📁 OU после обновления: {new_ou}")
            
            success = new_ou == target_ou
            print(f"🔍 OU изменилось корректно: {'✅ Да' if success else '❌ Нет'}")
            
            if success:
                new_display = get_display_name_for_orgunit_path(new_ou, orgunits)
                print(f"🎨 Отображаемое название: {new_display}")
        
        print("\n✅ Тест завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_move_user_to_ou()
