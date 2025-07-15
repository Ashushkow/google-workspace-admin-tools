#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест прямого импорта без использования __init__.py
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_direct_module_import():
    """Тестирует импорт напрямую из модуля, минуя __init__.py"""
    print("🧪 Тестирование прямого импорта модуля")
    print("=" * 50)
    
    try:
        # Импортируем GoogleAPIClient
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
        
        # Импортируем напрямую из файла модуля
        import importlib.util
        
        # Загружаем DocumentService напрямую
        doc_service_path = Path(__file__).parent / 'src' / 'services' / 'document_service.py'
        spec = importlib.util.spec_from_file_location("document_service", doc_service_path)
        document_service_module = importlib.util.module_from_spec(spec)
        
        # Сначала загружаем зависимости
        drive_api_path = Path(__file__).parent / 'src' / 'api' / 'drive_api.py'
        drive_spec = importlib.util.spec_from_file_location("drive_api", drive_api_path)
        drive_api_module = importlib.util.module_from_spec(drive_spec)
        
        # Добавляем модули в sys.modules
        sys.modules['drive_api'] = drive_api_module
        sys.modules['document_service'] = document_service_module
        
        # Выполняем загрузку
        drive_spec.loader.exec_module(drive_api_module)
        spec.loader.exec_module(document_service_module)
        
        # Получаем класс DocumentService
        DocumentService = document_service_module.DocumentService
        
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
    success = test_direct_module_import()
    if success:
        print("\n🎉 Тест прошел успешно!")
        print("📄 DocumentService можно создать напрямую")
    else:
        print("\n💥 Тест не удался")
    
    sys.exit(0 if success else 1)
