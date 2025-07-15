#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки функциональности управления документами Google Drive.
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.api.drive_api import DriveAPI
from src.services.document_service import DocumentService, DocumentAccessRequest
from src.api.google_api_client import GoogleAPIClient

def test_document_management():
    """Тестирует управление документами"""
    print("🧪 Тестирование управления документами Google Drive")
    print("=" * 60)
    
    # URL тестового документа
    document_url = "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2"
    test_email = "andrei.shushkov@sputnik8.com"
    
    try:
        # Инициализация Google API клиента
        print("🔧 Инициализация Google API клиента...")
        client = GoogleAPIClient("credentials.json")
        
        if not client.initialize():
            print("❌ Не удалось инициализировать Google API клиент")
            return False
        
        # Получение credentials
        credentials = client.get_credentials()
        if not credentials:
            print("❌ Не удалось получить credentials")
            return False
        
        # Создание сервиса управления документами
        print("📄 Создание сервиса управления документами...")
        document_service = DocumentService(credentials)
        
        # Получение информации о документе
        print(f"📋 Получение информации о документе...")
        doc_info = document_service.get_document_info(document_url)
        
        if doc_info:
            print(f"✅ Документ найден:")
            print(f"   Название: {doc_info.name}")
            print(f"   Владелец: {doc_info.owner}")
            print(f"   ID файла: {doc_info.file_id}")
            print(f"   Разрешений: {len(doc_info.permissions)}")
            
            # Показываем текущие разрешения
            print("\\n📋 Текущие разрешения:")
            for perm in doc_info.permissions:
                email = perm.email_address or perm.display_name or "Неизвестно"
                role = document_service.get_role_description(perm.role)
                perm_type = document_service.get_permission_type_description(perm.permission_type)
                print(f"   • {email} - {role} ({perm_type})")
        else:
            print("❌ Не удалось получить информацию о документе")
            return False
        
        # Тест предоставления доступа (если нужно)
        print(f"\\n🔑 Проверка доступа для {test_email}...")
        
        # Проверим, есть ли уже доступ
        has_access = False
        for perm in doc_info.permissions:
            if perm.email_address == test_email:
                has_access = True
                print(f"✅ У пользователя {test_email} уже есть доступ: {document_service.get_role_description(perm.role)}")
                break
        
        if not has_access:
            print(f"🔐 Предоставление доступа для {test_email}...")
            request = DocumentAccessRequest(
                document_url=document_url,
                user_email=test_email,
                role="reader",
                notify=False  # Не отправляем уведомление при тестировании
            )
            
            success = document_service.grant_access(request)
            if success:
                print(f"✅ Доступ успешно предоставлен!")
            else:
                print(f"❌ Не удалось предоставить доступ")
        
        print("\\n✅ Тестирование завершено успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестирования управления документами...")
    print("📝 Этот скрипт проверяет возможность работы с Google Drive API")
    print("🔐 Убедитесь, что файл credentials.json настроен правильно")
    print()
    
    success = test_document_management()
    
    if success:
        print("\\n🎉 Все тесты прошли успешно!")
        print("📄 Функциональность управления документами готова к использованию")
    else:
        print("\\n💥 Тестирование не удалось")
        print("🔧 Проверьте настройки Google API и credentials.json")
    
    sys.exit(0 if success else 1)
