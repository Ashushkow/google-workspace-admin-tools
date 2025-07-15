#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест Google Drive API после добавления новых scopes
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.config.enhanced_config import config
from src.api.google_api_client import GoogleAPIClient


def test_drive_api_access():
    """Тест доступа к Drive API"""
    print("🔍 Тестирование доступа к Google Drive API...")
    print(f"📋 Используемые scopes:")
    for i, scope in enumerate(config.google.scopes, 1):
        print(f"   {i}. {scope}")
    print()
    
    # Создаем Google API клиент
    client = GoogleAPIClient(config.settings.google_application_credentials)
    
    if not client.initialize():
        print("❌ Не удалось инициализировать Google API клиент")
        return False
    
    print("✅ Google API клиент инициализирован")
    
    # Получаем credentials
    creds = client.get_credentials()
    if not creds:
        print("❌ Не удалось получить credentials")
        return False
    
    print("✅ Credentials получены")
    
    try:
        # Тестируем Drive API
        from googleapiclient.discovery import build
        
        drive_service = build('drive', 'v3', credentials=creds)
        print("✅ Drive API сервис создан")
        
        # Пробуем получить информацию о файле
        file_id = "1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk"
        
        file_info = drive_service.files().get(
            fileId=file_id,
            fields="id,name,mimeType,webViewLink,owners"
        ).execute()
        
        print("✅ Успешно получена информация о документе:")
        print(f"   📄 Название: {file_info.get('name', 'Неизвестно')}")
        print(f"   🔗 ID: {file_info.get('id', 'Неизвестно')}")
        print(f"   👤 Владелец: {file_info.get('owners', [{}])[0].get('displayName', 'Неизвестно')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании Drive API: {e}")
        return False


if __name__ == "__main__":
    success = test_drive_api_access()
    if success:
        print("\n🎉 Тест завершен успешно! Drive API работает корректно.")
    else:
        print("\n💥 Тест не прошел. Проверьте авторизацию и scopes.")
