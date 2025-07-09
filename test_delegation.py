#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка Domain-wide delegation для Service Account
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_domain_delegation():
    """Тестирование Domain-wide delegation"""
    print("🧪 Тестирование Domain-wide delegation...")
    print(f"📧 Admin Email: andrei.shushkov@sputnik8.com")
    print(f"🏢 Domain: sputnik8.com")
    print()
    
    try:
        # Загружаем Service Account credentials
        creds = service_account.Credentials.from_service_account_file(
            'credentials.json',
            scopes=[
                'https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group',
                'https://www.googleapis.com/auth/admin.directory.orgunit',
                'https://www.googleapis.com/auth/calendar'
            ],
            subject='andrei.shushkov@sputnik8.com'  # Делегирование
        )
        
        print("✅ Service Account credentials загружены")
        print(f"📧 Service Account: {creds.service_account_email}")
        
        # Создаем сервис Admin SDK
        service = build('admin', 'directory_v1', credentials=creds)
        print("✅ Admin SDK service создан")
        
        # Пробуем получить список пользователей (простой тест)
        print("🔍 Тестируем доступ к API...")
        
        result = service.users().list(
            customer='my_customer',
            maxResults=1,
            fields='users(primaryEmail)'
        ).execute()
        
        users = result.get('users', [])
        
        if users:
            print("🎉 УСПЕХ! Domain-wide delegation настроен правильно")
            print(f"✅ Найден пользователь: {users[0]['primaryEmail']}")
            print()
            print("🚀 Можно запускать основное приложение:")
            print("   python main.py")
        else:
            print("⚠️  API работает, но пользователи не найдены")
            print("   Проверьте права доступа к домену")
            
    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        error_reason = error_details.get('reason', 'unknown')
        
        print(f"❌ HTTP ошибка: {e.resp.status}")
        print(f"📝 Детали: {error_details}")
        
        if error_reason == 'unauthorized':
            print()
            print("🔧 РЕШЕНИЕ:")
            print("1. Откройте https://admin.google.com")
            print("2. Security → API Controls → Domain-wide delegation")
            print("3. Add new:")
            print("   Client ID: 117649742513308469203")
            print("   OAuth scopes: https://www.googleapis.com/auth/admin.directory.user,https://www.googleapis.com/auth/admin.directory.group,https://www.googleapis.com/auth/admin.directory.orgunit,https://www.googleapis.com/auth/calendar")
            print("4. Authorize")
        elif error_reason == 'forbidden':
            print()
            print("🔧 РЕШЕНИЕ:")
            print("Убедитесь, что andrei.shushkov@sputnik8.com имеет права Super Admin")
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка: {error_msg}")
        
        if 'unauthorized_client' in error_msg:
            print()
            print("🔧 РЕШЕНИЕ:")
            print("Domain-wide delegation не настроен или настроен неправильно")
            print()
            print("Настройте в Google Workspace Admin Console:")
            print("1. https://admin.google.com")
            print("2. Security → API Controls → Domain-wide delegation")
            print("3. Client ID: 117649742513308469203")
            print("4. OAuth scopes: https://www.googleapis.com/auth/admin.directory.user,https://www.googleapis.com/auth/admin.directory.group,https://www.googleapis.com/auth/admin.directory.orgunit,https://www.googleapis.com/auth/calendar")
        else:
            print("📖 Проверьте docs/SERVICE_ACCOUNT_SETUP.md")

if __name__ == "__main__":
    test_domain_delegation()
