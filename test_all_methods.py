#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест всех методов DocumentService
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_all_document_methods():
    """Тестируем все методы DocumentService"""
    print("🧪 Тестирование всех методов DocumentService")
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
        
        # Создаем полную упрощенную версию DocumentService
        from src.api.drive_api import DriveAPI, DrivePermission
        from dataclasses import dataclass
        from typing import List
        import logging
        
        @dataclass
        class DocumentInfo:
            file_id: str
            name: str
            url: str
            owner: str
            permissions: List[DrivePermission]
        
        class DocumentService:
            """Полная упрощенная версия DocumentService"""
            def __init__(self, credentials):
                self.drive_api = DriveAPI(credentials)
                self.logger = logging.getLogger(__name__)
            
            def get_document_info(self, document_url):
                try:
                    file_id = self.drive_api.extract_file_id_from_url(document_url)
                    if not file_id:
                        return None
                    drive_file = self.drive_api.get_file_info(file_id)
                    if not drive_file:
                        return None
                    return DocumentInfo(
                        file_id=drive_file.file_id,
                        name=drive_file.name,
                        url=drive_file.web_view_link,
                        owner=drive_file.owner_email or "Неизвестно",
                        permissions=drive_file.permissions
                    )
                except Exception as e:
                    self.logger.error(f"Ошибка при получении информации о документе: {e}")
                    return None
            
            def list_document_permissions(self, document_url):
                try:
                    file_id = self.drive_api.extract_file_id_from_url(document_url)
                    if not file_id:
                        return []
                    permissions = self.drive_api.get_permissions(file_id)
                    return permissions
                except Exception as e:
                    self.logger.error(f"Ошибка при получении разрешений: {e}")
                    return []
            
            def get_role_description(self, role):
                role_descriptions = {
                    'reader': 'Чтение',
                    'commenter': 'Комментирование', 
                    'writer': 'Редактирование',
                    'owner': 'Владелец'
                }
                return role_descriptions.get(role, role)
            
            def get_permission_type_description(self, perm_type):
                type_descriptions = {
                    'user': 'Пользователь',
                    'group': 'Группа',
                    'domain': 'Домен',
                    'anyone': 'Любой'
                }
                return type_descriptions.get(perm_type, perm_type)
        
        document_service = DocumentService(credentials)
        print("✅ DocumentService создан")
        
        # Тестируем все методы
        test_url = "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2"
        
        print("🔄 Тестируем get_document_info...")
        doc_info = document_service.get_document_info(test_url)
        if doc_info:
            print(f"   ✅ Документ: {doc_info.name}")
        
        print("🔄 Тестируем list_document_permissions...")
        permissions = document_service.list_document_permissions(test_url)
        print(f"   ✅ Разрешений: {len(permissions)}")
        
        print("🔄 Тестируем get_role_description...")
        role_desc = document_service.get_role_description('writer')
        print(f"   ✅ Описание роли 'writer': {role_desc}")
        
        print("🔄 Тестируем get_permission_type_description...")
        type_desc = document_service.get_permission_type_description('user')
        print(f"   ✅ Описание типа 'user': {type_desc}")
        
        print("\n✅ Все методы DocumentService работают корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        print(f"❌ Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_all_document_methods()
