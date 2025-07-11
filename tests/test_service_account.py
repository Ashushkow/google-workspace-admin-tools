#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест Service Account credentials
"""

import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_service_account():
    """Простой тест подключения Service Account"""
    print("🧪 Тестирование Service Account...")
    
    try:
        # Загружаем credentials
        creds = service_account.Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/admin.directory.user.readonly']
        )
        
        print("✅ Credentials загружены успешно")
        print(f"📧 Service Account: {creds.service_account_email}")
        
        # Пробуем создать сервис (без делегирования)
        service = build('admin', 'directory_v1', credentials=creds)
        print("✅ Service создан успешно")
        
        print("\n⚠️  Следующий шаг: настройка Domain-wide delegation")
        print("📖 Инструкция: docs/SERVICE_ACCOUNT_SETUP.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_service_account()
