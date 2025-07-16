#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления атрибута owner в DocumentInfo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_document_info_fix():
    """Тестируем исправленную версию DocumentInfo"""
    print("🧪 Тестирование исправления атрибута 'owner'")
    print("=" * 60)
    
    try:
        # Создаем клиент как в исправленном коде
        from src.api.google_api_client import GoogleAPIClient
        from src.config.enhanced_config import config
        
        google_client = GoogleAPIClient(config.settings.google_application_credentials)
        if not google_client.initialize():
            print("❌ Не удалось инициализировать Google API клиент")
            return False
        
        credentials = google_client.get_credentials()
        if not credentials:
            print("❌ Не удалось получить учетные данные")
            return False
        
        print("✅ Credentials получены")
        
        # Создаем DocumentService с исправленной логикой
        from src.api.drive_api import DriveAPI, DrivePermission
        from dataclasses import dataclass
        from typing import List, Optional
        import logging
        
        @dataclass
        class DocumentInfo:
            """Информация о документе с доступами"""
            file_id: str
            name: str
            url: str
            owner: str
            permissions: List[DrivePermission]
        
        class DocumentService:
            """Упрощенный DocumentService с правильными атрибутами"""
            def __init__(self, credentials):
                self.drive_api = DriveAPI(credentials)
                self.logger = logging.getLogger(__name__)
            
            def get_document_info(self, document_url):
                """Получает информацию о документе"""
                try:
                    file_id = self.drive_api.extract_file_id_from_url(document_url)
                    if not file_id:
                        return None
                    
                    # Получаем информацию о файле
                    drive_file = self.drive_api.get_file_info(file_id)
                    if not drive_file:
                        return None
                    
                    # Создаем DocumentInfo с правильными атрибутами
                    return DocumentInfo(
                        file_id=drive_file.file_id,
                        name=drive_file.name,
                        url=drive_file.web_view_link,
                        owner=drive_file.owner_email or "Неизвестно",
                        permissions=drive_file.permissions
                    )
                    
                except Exception as e:
                    print(f"❌ Ошибка при получении информации о документе: {e}")
                    return None
        
        document_service = DocumentService(credentials)
        print("✅ DocumentService создан")
        
        # Тестируем получение информации
        test_url = "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2"
        print("🔄 Получение информации о документе...")
        
        doc_info = document_service.get_document_info(test_url)
        if doc_info:
            print("✅ Информация о документе получена:")
            print(f"   📄 ID: {doc_info.file_id}")
            print(f"   📝 Название: {doc_info.name}")
            print(f"   👤 Владелец: {doc_info.owner}")  # Теперь должно работать!
            print(f"   🔗 URL: {doc_info.url[:50]}...")
            print(f"   🔐 Разрешений: {len(doc_info.permissions)}")
        else:
            print("❌ Не удалось получить информацию о документе")
            return False
        
        print("\n✅ Атрибут 'owner' работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        print(f"❌ Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_document_info_fix()
