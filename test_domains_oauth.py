#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест проверки OAuth 2.0 с новыми scopes для доменов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth import get_service
from src.config.enhanced_config import config

def test_domains_access():
    """Тестирует доступ к доменам через Google API"""
    print("🔧 Тестируем доступ к доменам...")
    print(f"📋 Используемые scopes:")
    for scope in config.google.scopes:
        print(f"  • {scope}")
    print()
    
    try:
        # Получаем сервис
        print("🔗 Подключаемся к Google API...")
        service = get_service()
        print("✅ Подключение успешно!")
        
        # Тестируем доступ к доменам
        print("\n🏢 Пытаемся получить список доменов...")
        try:
            domains_result = service.domains().list(customer='my_customer').execute()
            domains = domains_result.get('domains', [])
            
            if domains:
                print(f"✅ Успешно получены домены ({len(domains)}):")
                for domain in domains:
                    print(f"  • {domain.get('domainName')} - статус: {domain.get('verified', 'неизвестно')}")
            else:
                print("⚠️ Домены не найдены (пустой список)")
                
        except Exception as domain_error:
            print(f"❌ Ошибка при получении доменов: {domain_error}")
            if "403" in str(domain_error) or "Insufficient Permission" in str(domain_error):
                print("💡 Это ошибка недостатка прав доступа")
                print("🔧 Попробуйте:")
                print("  1. Удалить token.pickle и переавторизоваться")
                print("  2. Проверить scope в OAuth consent screen")
                print("  3. Убедиться, что приложение имеет scope 'admin.directory.domain.readonly'")
            return False
        
        # Тестируем доступ к пользователям
        print("\n👥 Проверяем доступ к пользователям...")
        try:
            users_result = service.users().list(customer='my_customer', maxResults=3).execute()
            users = users_result.get('users', [])
            print(f"✅ Доступ к пользователям работает: найдено {len(users)} пользователей")
        except Exception as users_error:
            print(f"❌ Ошибка при получении пользователей: {users_error}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Тест OAuth 2.0 доступа к доменам Google Workspace")
    print("=" * 60)
    
    success = test_domains_access()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Тест пройден успешно!")
    else:
        print("❌ Тест не пройден. Проверьте настройки OAuth 2.0.")
    print("=" * 60)
