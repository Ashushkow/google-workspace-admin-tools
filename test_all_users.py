#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест получения ВСЕХ пользователей с пагинацией
"""

import os
import sys
from pathlib import Path

# Принудительно перезагружаем .env
from dotenv import load_dotenv
load_dotenv(override=True)

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_all_users():
    """Тестируем получение всех пользователей"""
    print("=" * 70)
    print("🔍 ТЕСТ ПОЛУЧЕНИЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 70)
    
    print(f"Домен: {os.getenv('GOOGLE_WORKSPACE_DOMAIN')}")
    print(f"DEV_MODE: {os.getenv('DEV_MODE')}")
    print()
    
    # Тест 1: Старый API с пагинацией
    print("1. Тестируем старый API с полной пагинацией:")
    try:
        from src.auth import get_service
        service = get_service()
        
        all_users = []
        page_token = None
        page_count = 0
        
        while True:
            page_count += 1
            print(f"   Загружаем страницу {page_count}...")
            
            request_params = {
                'customer': 'my_customer',
                'maxResults': 500,  # Максимум за запрос
                'orderBy': 'email'
            }
            
            if page_token:
                request_params['pageToken'] = page_token
            
            result = service.users().list(**request_params).execute()
            page_users = result.get('users', [])
            
            if page_users:
                all_users.extend(page_users)
                print(f"     Получено {len(page_users)} пользователей (всего: {len(all_users)})")
            
            page_token = result.get('nextPageToken')
            if not page_token:
                print(f"     Достигнута последняя страница")
                break
                
            if page_count > 20:  # Защита
                print(f"     Остановлено после {page_count} страниц")
                break
        
        print(f"   ✅ ИТОГО через старый API: {len(all_users)} пользователей")
        
        # Показываем первых 5 и последних 5
        if len(all_users) > 10:
            print("   Первые 5:")
            for user in all_users[:5]:
                email = user.get('primaryEmail', 'N/A')
                name = user.get('name', {}).get('fullName', 'N/A')
                print(f"     • {email} ({name})")
            
            print("   ...")
            print("   Последние 5:")
            for user in all_users[-5:]:
                email = user.get('primaryEmail', 'N/A')
                name = user.get('name', {}).get('fullName', 'N/A')
                print(f"     • {email} ({name})")
        else:
            for user in all_users:
                email = user.get('primaryEmail', 'N/A')
                name = user.get('name', {}).get('fullName', 'N/A')
                print(f"     • {email} ({name})")
        
        return len(all_users)
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return 0

def test_new_api():
    """Тестируем новый API"""
    print("\\n2. Тестируем новый API с пагинацией:")
    try:
        from src.api.google_api_client import GoogleAPIClient
        from src.config.enhanced_config import config
        
        client = GoogleAPIClient(config.settings.google_application_credentials)
        if client.initialize():
            users = client.get_users()  # Без лимита = все пользователи
            print(f"   ✅ Новый API получил: {len(users)} пользователей")
            return len(users)
        else:
            print("   ❌ Не удалось инициализировать новый API")
            return 0
            
    except Exception as e:
        print(f"   ❌ Ошибка нового API: {e}")
        return 0

if __name__ == "__main__":
    total_old = test_all_users()
    total_new = test_new_api()
    
    print("\\n" + "=" * 70)
    print("📊 РЕЗУЛЬТАТЫ:")
    print("=" * 70)
    print(f"Старый API (с пагинацией): {total_old} пользователей")
    print(f"Новый API (с пагинацией):  {total_new} пользователей")
    
    if total_old > 100 or total_new > 100:
        print("\\n🎉 ОТЛИЧНО! Получено более 100 пользователей!")
        print("Теперь в приложении будут показаны ВСЕ пользователи.")
    elif total_old > 50 or total_new > 50:
        print("\\n✅ Хорошо! Получено больше 50 пользователей.")
    else:
        print("\\n⚠️  Получено мало пользователей. Возможно есть ограничения.")
    print("=" * 70)
