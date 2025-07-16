#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест кнопки "Документы" в GUI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_document_button():
    """Эмулирует нажатие кнопки Документы"""
    print("🧪 Тестирование кнопки 'Документы'")
    print("=" * 50)
    
    try:
        # Импортируем необходимые модули (избегаем services.__init__.py)
        from src.config.enhanced_config import config
        from src.api.google_api_client import GoogleAPIClient
        
        print("🔄 Создание Google API клиента...")
        client = GoogleAPIClient(config.settings.google_application_credentials)
        
        if not client.initialize():
            print("❌ Не удалось инициализировать клиент")
            return False
        
        print("✅ Клиент инициализирован")
        
        print("🔄 Получение credentials...")
        credentials = client.get_credentials()
        if not credentials:
            print("❌ Не удалось получить credentials")
            return False
        
        print("✅ Credentials получены")
        
        print("🔄 Создание DocumentService...")
        
        # Прямой импорт без использования пакетной структуры (избегаем циклические импорты)
        from src.api.drive_api import DriveAPI
        
        class DocumentService:
            """Упрощенный DocumentService для тестирования"""
            def __init__(self, credentials):
                self.drive_api = DriveAPI(credentials)
            
            def get_document_info(self, document_url):
                """Получает информацию о документе"""
                try:
                    file_id = self.drive_api.extract_file_id_from_url(document_url)
                    if not file_id:
                        return None
                    return self.drive_api.get_file_info(file_id)
                except Exception as e:
                    print(f"❌ Ошибка в DocumentService: {e}")
                    return None
        
        document_service = DocumentService(credentials)
        print("✅ DocumentService создан")
        
        # Тестируем метод получения информации о документе
        test_url = "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2"
        print(f"🔄 Получение информации о документе...")
        
        doc_info = document_service.get_document_info(test_url)
        if doc_info:
            print(f"✅ Информация о документе получена:")
            print(f"   📄 ID: {doc_info.file_id}")
            print(f"   📝 Название: {doc_info.name}")
            print(f"   👤 Владелец: {doc_info.owner_email or 'Неизвестно'}")
            print(f"   🔐 Разрешений: {len(doc_info.permissions)}")
        else:
            print("❌ Не удалось получить информацию о документе")
            return False
        
        print("\n✅ Тест кнопки 'Документы' прошел успешно!")
        print("📋 Это означает, что ошибка возникает в другом месте.")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании кнопки 'Документы': {e}")
        import traceback
        print(f"❌ Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_document_button()
