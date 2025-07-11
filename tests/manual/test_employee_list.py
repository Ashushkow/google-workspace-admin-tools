#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест окна списка пользователей
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.auth import get_service


def test_employee_list():
    """Тест загрузки пользователей в окне списка"""
    print("=" * 70)
    print("🔍 ТЕСТ ОКНА СПИСКА ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 70)
    
    try:
        # Получаем сервис
        service = get_service()
        print("✅ Сервис получен")
        
        # Загружаем пользователей напрямую через Google API (как это делает старый код)
        all_users = []
        page_token = None
        page_count = 0
        
        while True:
            page_count += 1
            print(f"  📄 Загружаем страницу {page_count}...")
            
            request_params = {
                'customer': 'my_customer',
                'maxResults': 500,
                'orderBy': 'email'
            }
            
            if page_token:
                request_params['pageToken'] = page_token
            
            result = service.users().list(**request_params).execute()
            page_users = result.get('users', [])
            
            if page_users:
                all_users.extend(page_users)
                print(f"    ✅ Получено {len(page_users)} пользователей (всего: {len(all_users)})")
            
            page_token = result.get('nextPageToken')
            if not page_token:
                print(f"    🏁 Достигнута последняя страница")
                break
            
            if page_count > 50:
                print(f"    ⚠️ Остановлено после {page_count} страниц (защита от бесконечного цикла)")
                break
        
        print(f"\\n✅ Всего загружено: {len(all_users)} пользователей")
        
        # Проверяем наличие проблемного пользователя
        kirill_user = None
        for i, user in enumerate(all_users):
            email = user.get('primaryEmail', '')
            if 'kirill.kropochev' in email.lower():
                kirill_user = user
                print(f"🔍 Найден пользователь Kirill на позиции {i+1}: {email}")
                print(f"   Данные пользователя:")
                for key, value in user.items():
                    if key in ['primaryEmail', 'name', 'suspended', 'orgUnitPath', 'creationTime']:
                        print(f"     {key}: {value}")
                break
        
        if not kirill_user:
            print("❌ Пользователь kirill.kropochev не найден")
            print("🔍 Поиск похожих по имени 'kirill':")
            for i, user in enumerate(all_users):
                email = user.get('primaryEmail', '').lower()
                name = str(user.get('name', {})).lower()
                if 'kirill' in email or 'kirill' in name:
                    print(f"  {i+1:3d}. {user.get('primaryEmail', '')} - {user.get('name', {})}")
        
        # Проверяем пользователей вокруг алфавитной позиции Kirill
        print(f"\\n� Пользователи в алфавитном порядке вокруг буквы 'K':")
        k_users = []
        for i, user in enumerate(all_users):
            email = user.get('primaryEmail', '').lower()
            if email.startswith('k'):
                k_users.append((i+1, user.get('primaryEmail', ''), user.get('name', {}).get('fullName', '')))
        
        for pos, email, name in k_users[:20]:  # Показываем первых 20 пользователей на букву K
            print(f"  {pos:3d}. {email} ({name})")
            
        if len(k_users) > 20:
            print(f"  ... и еще {len(k_users)-20} пользователей на букву 'K'")
        
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_employee_list()
