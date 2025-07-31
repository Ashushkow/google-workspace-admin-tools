#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест проверки Drive API для документов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.enhanced_config import config
from src.api.google_api_client import GoogleAPIClient

def test_drive_api():
    """Тест Drive API"""
    print("🧪 Тестирование Drive API для документов")
    print("=" * 50)
    
    try:
        # Создаем клиент
        print("🔄 Создание Google API клиента...")
        client = GoogleAPIClient(config.settings.google_application_credentials)
        
        if not client.initialize():
            print("❌ Не удалось инициализировать клиент")
            return False
        
        print("✅ Клиент инициализирован")
        
        # Получаем credentials
        print("🔄 Получение credentials...")
        credentials = client.get_credentials()
        if not credentials:
            print("❌ Не удалось получить credentials")
            return False
        
        print("✅ Credentials получены")
        
        # Создаем Drive API
        print("🔄 Создание Drive API...")
        from src.api.drive_api import DriveAPI
        drive_api = DriveAPI(credentials)
        
        print("✅ Drive API создан")
        
        # Тестируем извлечение ID из URL
        test_url = "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2"
        print(f"🔄 Извлечение ID из URL: {test_url[:50]}...")
        
        file_id = drive_api.extract_file_id_from_url(test_url)
        if file_id:
            print(f"✅ ID файла: {file_id}")
        else:
            print("❌ Не удалось извлечь ID файла")
            return False
        
        # Тестируем получение информации о файле
        print("🔄 Получение информации о файле...")
        file_info = drive_api.get_file_info(file_id)
        
        if file_info:
            print(f"✅ Информация о файле получена:")
            print(f"   📄 Название: {file_info.name}")
            print(f"   🔗 URL: {file_info.web_view_link[:50]}...")
            print(f"   👤 Владелец: {file_info.owner_email or 'Неизвестно'}")
            print(f"   🔐 Разрешений: {len(file_info.permissions)}")
        else:
            print("❌ Не удалось получить информацию о файле")
            return False
        
        print("\n✅ Все тесты Drive API прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании Drive API: {e}")
        import traceback
        print(f"❌ Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_drive_api()
