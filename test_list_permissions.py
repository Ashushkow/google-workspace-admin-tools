#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест метода list_document_permissions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_list_permissions():
    """Тестируем метод list_document_permissions"""
    print("🧪 Тестирование метода list_document_permissions")
    print("=" * 60)
    
    try:
        # Создаем клиент
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
        
        # Создаем DocumentService как в main_window.py
        from src.api.drive_api import DriveAPI, DrivePermission
        from dataclasses import dataclass
        from typing import List
        import logging
        
        class DocumentService:
            """Упрощенный DocumentService с методом list_document_permissions"""
            def __init__(self, credentials):
                self.drive_api = DriveAPI(credentials)
                self.logger = logging.getLogger(__name__)
            
            def list_document_permissions(self, document_url):
                """Получает список всех разрешений для документа"""
                try:
                    file_id = self.drive_api.extract_file_id_from_url(document_url)
                    if not file_id:
                        self.logger.error(f"Не удалось извлечь ID файла из URL: {document_url}")
                        return []
                    
                    # Получаем список разрешений
                    permissions = self.drive_api.get_permissions(file_id)
                    self.logger.info(f"📋 Получено {len(permissions)} разрешений для документа {file_id}")
                    return permissions
                    
                except Exception as e:
                    self.logger.error(f"Ошибка при получении разрешений: {e}")
                    return []
        
        document_service = DocumentService(credentials)
        print("✅ DocumentService создан")
        
        # Тестируем получение разрешений
        test_url = "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2"
        print("🔄 Получение разрешений документа...")
        
        permissions = document_service.list_document_permissions(test_url)
        print(f"✅ Получено {len(permissions)} разрешений:")
        
        for i, perm in enumerate(permissions[:5], 1):  # Показываем только первые 5
            print(f"   {i}. {perm.email_address} - {perm.role} ({perm.permission_type})")
        
        if len(permissions) > 5:
            print(f"   ... и еще {len(permissions) - 5} разрешений")
        
        print("\n✅ Метод list_document_permissions работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        print(f"❌ Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_list_permissions()
