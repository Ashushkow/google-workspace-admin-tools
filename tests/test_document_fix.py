#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки исправления ошибки "Некорректный тип Google API клиента"
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_document_service_creation():
    """Тестирует создание DocumentService через различные способы получения credentials"""
    print("🧪 Тестирование создания DocumentService")
    print("=" * 50)
    
    try:
        # Тест 1: Прямое создание GoogleAPIClient
        print("1️⃣ Тест прямого создания GoogleAPIClient...")
        from src.api.google_api_client import GoogleAPIClient
        from src.config.enhanced_config import config
        
        client = GoogleAPIClient(config.settings.google_application_credentials)
        if client.initialize():
            print("   ✅ GoogleAPIClient успешно инициализирован")
            
            credentials = client.get_credentials()
            if credentials:
                print("   ✅ Credentials успешно получены")
                
                # Тест создания DocumentService
                from src.services.document_service import DocumentService
                doc_service = DocumentService(credentials)
                print("   ✅ DocumentService успешно создан")
                
                return True
            else:
                print("   ❌ Не удалось получить credentials")
                return False
        else:
            print("   ❌ Не удалось инициализировать GoogleAPIClient")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def test_repository_access():
    """Тестирует доступ к client через repository"""
    print("\n2️⃣ Тест доступа через repository...")
    
    try:
        from src.repositories.google_api_repository import GoogleUserRepository
        
        user_repo = GoogleUserRepository()
        if hasattr(user_repo, 'client'):
            print("   ✅ Repository имеет доступ к client")
            
            if user_repo.client.initialize():
                print("   ✅ Client в repository инициализирован")
                
                credentials = user_repo.client.get_credentials()
                if credentials:
                    print("   ✅ Credentials получены через repository")
                    return True
                else:
                    print("   ❌ Не удалось получить credentials через repository")
                    return False
            else:
                print("   ❌ Не удалось инициализировать client в repository")
                return False
        else:
            print("   ❌ Repository не имеет атрибута 'client'")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 Тестирование исправления ошибки управления документами")
    print("=" * 60)
    
    test1 = test_document_service_creation()
    test2 = test_repository_access()
    
    print("=" * 60)
    if test1 and test2:
        print("✅ Все тесты прошли успешно!")
        print("📄 Управление документами должно работать корректно")
        print("\n📋 Инструкции для тестирования:")
        print("   1. Запустите приложение: python main.py")
        print("   2. Нажмите кнопку '📄 Документы' или Ctrl+D")
        print("   3. Окно управления документами должно открыться без ошибок")
    else:
        print("❌ Обнаружены проблемы")
        print("🔧 Проверьте настройки Google API")
    
    return test1 and test2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
