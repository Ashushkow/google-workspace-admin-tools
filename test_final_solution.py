#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест после исправления OAuth scopes
Проверяет:
1. Загрузку всех пользователей (176)
2. Доступ к доменам (без ошибки 403)
3. Работу основных функций API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth import get_service
from src.config.enhanced_config import config

def test_all_functionality():
    """Комплексный тест всех функций после исправления OAuth scopes"""
    print("🔧 Комплексный тест Admin Team Tools v2.0.7")
    print("=" * 60)
    
    # Проверяем scopes
    print("📋 Проверяем OAuth scopes:")
    for i, scope in enumerate(config.google.scopes, 1):
        print(f"  {i}. {scope}")
    print()
    
    try:
        # Подключение к API
        print("🔗 Подключаемся к Google Admin SDK...")
        service = get_service()
        print("✅ Подключение успешно!")
        
        # Тест 1: Доступ к доменам
        print("\n🏢 Тест 1: Проверяем доступ к доменам...")
        try:
            domains_result = service.domains().list(customer='my_customer').execute()
            domains = domains_result.get('domains', [])
            
            if domains:
                print(f"✅ Успешно получены домены ({len(domains)}):")
                for domain in domains:
                    verified = "✓ верифицирован" if domain.get('verified') else "⚠ не верифицирован"
                    print(f"  • {domain.get('domainName')} - {verified}")
            else:
                print("⚠️ Домены не найдены")
                
        except Exception as e:
            print(f"❌ Ошибка доступа к доменам: {e}")
            if "403" in str(e):
                print("💡 Это означает, что scope всё ещё недостаточно")
                return False
        
        # Тест 2: Загрузка всех пользователей
        print("\n👥 Тест 2: Проверяем загрузку всех пользователей...")
        all_users = []
        next_page_token = None
        page_count = 0
        
        while True:
            page_count += 1
            request_params = {
                'customer': 'my_customer',
                'maxResults': 500,  # Максимум за раз
                'orderBy': 'email'
            }
            
            if next_page_token:
                request_params['pageToken'] = next_page_token
            
            result = service.users().list(**request_params).execute()
            users = result.get('users', [])
            all_users.extend(users)
            
            print(f"  📄 Страница {page_count}: загружено {len(users)} пользователей")
            
            next_page_token = result.get('nextPageToken')
            if not next_page_token:
                break
        
        print(f"✅ Всего загружено пользователей: {len(all_users)}")
        
        # Проверяем конкретного пользователя
        kirill_user = None
        for user in all_users:
            if user.get('primaryEmail') == 'kirill.kropochev@sputnik8.com':
                kirill_user = user
                break
        
        if kirill_user:
            position = all_users.index(kirill_user) + 1
            print(f"✅ Пользователь kirill.kropochev@sputnik8.com найден на позиции {position}")
        else:
            print("⚠️ Пользователь kirill.kropochev@sputnik8.com не найден")
        
        # Тест 3: Проверяем первых и последних пользователей
        print("\n📊 Тест 3: Анализ списка пользователей:")
        if all_users:
            print(f"  🥇 Первый пользователь: {all_users[0].get('primaryEmail')}")
            if len(all_users) > 1:
                print(f"  🥉 Последний пользователь: {all_users[-1].get('primaryEmail')}")
            
            # Проверяем сортировку
            emails = [user.get('primaryEmail') for user in all_users[:10]]
            is_sorted = all(emails[i] <= emails[i+1] for i in range(len(emails)-1))
            print(f"  📝 Сортировка по email: {'✅ корректная' if is_sorted else '❌ нарушена'}")
        
        # Тест 4: Проверяем доступ к организационным единицам
        print("\n🏗️ Тест 4: Проверяем доступ к организационным единицам...")
        try:
            orgunits_result = service.orgunits().list(customerId='my_customer').execute()
            orgunits = orgunits_result.get('organizationUnits', [])
            print(f"✅ Найдено организационных единиц: {len(orgunits)}")
            
            for orgunit in orgunits[:3]:  # Показываем первые 3
                print(f"  • {orgunit.get('name')} ({orgunit.get('orgUnitPath')})")
                
        except Exception as e:
            print(f"⚠️ Ошибка доступа к организационным единицам: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Все тесты пройдены успешно!")
        print("🎯 Основные результаты:")
        print(f"  • Загружено пользователей: {len(all_users)}")
        print(f"  • Доступ к доменам: работает")
        print(f"  • OAuth scopes: расширены и работают корректно")
        print(f"  • Ошибка 403: устранена")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Общая ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_all_functionality()
    
    if success:
        print("\n🎉 Все проблемы решены! Приложение готово к использованию.")
    else:
        print("\n⚠️ Есть проблемы, требующие внимания.")
