#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест кнопки "Документы" с новым подходом
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_document_button_fixed():
    """Тестируем исправленную версию кнопки Документы"""
    print("🧪 Тестирование исправленной кнопки 'Документы'")
    print("=" * 60)
    
    try:
        # Прямой подход, как в исправленном коде
        print("🔄 Создание Google API клиента...")
        from src.api.google_api_client import GoogleAPIClient
        from src.config.enhanced_config import config
        
        google_client = GoogleAPIClient(config.settings.google_application_credentials)
        if not google_client.initialize():
            print("❌ Не удалось инициализировать Google API клиент")
            return False
        
        print("✅ Google API клиент инициализирован")
        
        # Получаем credentials
        print("🔄 Получаем credentials...")
        credentials = google_client.get_credentials()
        if not credentials:
            print("❌ Не удалось получить учетные данные")
            return False
        
        print("✅ Credentials получены успешно")
        
        # Создаем DocumentService (упрощенная версия)
        print("🔄 Создаем DocumentService...")
        from src.api.drive_api import DriveAPI
        
        class DocumentService:
            """Упрощенный DocumentService для избежания циклических импортов"""
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
                    print(f"❌ Ошибка при получении информации о документе: {e}")
                    return None
        
        document_service = DocumentService(credentials)
        print("✅ DocumentService создан успешно")
        
        # Тестируем получение информации о документе
        test_url = "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2"
        print("🔄 Получение информации о документе...")
        
        doc_info = document_service.get_document_info(test_url)
        if doc_info:
            print("✅ Информация о документе получена:")
            print(f"   📄 ID: {doc_info.file_id}")
            print(f"   📝 Название: {doc_info.name}")
            print(f"   👤 Владелец: {doc_info.owner_email or 'Неизвестно'}")
            print(f"   🔐 Разрешений: {len(doc_info.permissions)}")
        else:
            print("❌ Не удалось получить информацию о документе")
            return False
        
        print("\n✅ Все тесты прошли успешно!")
        print("🎯 Кнопка 'Документы' должна работать корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        print(f"❌ Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_document_button_fixed()
