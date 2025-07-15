#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест создания DocumentService напрямую
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_direct_import():
    """Тестирует прямой импорт без циклических зависимостей"""
    print("🧪 Тестирование прямого импорта DocumentService")
    print("=" * 50)
    
    try:
        # Импортируем напрямую без промежуточных модулей
        from src.api.google_api_client import GoogleAPIClient
        
        # Инициализируем клиент
        client = GoogleAPIClient("credentials.json")
        if not client.initialize():
            print("❌ Не удалось инициализировать Google API клиент")
            return False
        
        print("✅ Google API клиент инициализирован")
        
        # Получаем credentials
        credentials = client.get_credentials()
        if not credentials:
            print("❌ Не удалось получить credentials")
            return False
        
        print("✅ Credentials получены")
        
        # Импортируем DocumentService напрямую
        from src.services.document_service import DocumentService
        
        # Создаем сервис
        doc_service = DocumentService(credentials)
        print("✅ DocumentService создан успешно")
        
        # Тестируем базовую функциональность
        test_url = "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit"
        file_id = doc_service.drive_api.extract_file_id_from_url(test_url)
        
        if file_id:
            print(f"✅ ID файла извлечен: {file_id}")
            return True
        else:
            print("❌ Не удалось извлечь ID файла")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_import()
    if success:
        print("\n🎉 Тест прошел успешно!")
        print("📄 DocumentService работает корректно")
    else:
        print("\n💥 Тест не удался")
    
    sys.exit(0 if success else 1)
