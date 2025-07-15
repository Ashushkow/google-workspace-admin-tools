#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тестовый скрипт для проверки Google Drive API функциональности.
"""

import sys
import json
from pathlib import Path

def test_credentials():
    """Проверяет наличие и корректность credentials.json"""
    print("🔍 Проверка файла credentials.json...")
    
    creds_path = Path("credentials.json")
    if not creds_path.exists():
        print("❌ Файл credentials.json не найден")
        print("📋 Для настройки см.: docs/OAUTH2_PRIORITY_SETUP.md")
        return False
    
    try:
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        if 'installed' in creds_data:
            print("✅ OAuth 2.0 credentials обнаружены")
            client_id = creds_data['installed'].get('client_id', 'Не указан')
            print(f"   Client ID: {client_id[:20]}...")
            return True
        elif 'type' in creds_data and creds_data['type'] == 'service_account':
            print("✅ Service Account credentials обнаружены")
            client_email = creds_data.get('client_email', 'Не указан')
            print(f"   Client Email: {client_email}")
            return True
        else:
            print("⚠️ Неизвестный формат credentials.json")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка чтения credentials.json: {e}")
        return False

def test_google_libraries():
    """Проверяет наличие библиотек Google API"""
    print("🔍 Проверка библиотек Google API...")
    
    try:
        import google.oauth2.service_account
        import googleapiclient.discovery
        import google_auth_oauthlib.flow
        print("✅ Все необходимые библиотеки Google API установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствуют библиотеки Google API: {e}")
        print("💡 Установите: pip install google-api-python-client google-auth-oauthlib")
        return False

def test_document_url():
    """Проверяет корректность URL документа"""
    print("🔍 Проверка URL документа...")
    
    document_url = "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2"
    
    # Простая проверка на извлечение ID
    from urllib.parse import urlparse
    
    try:
        parsed_url = urlparse(document_url)
        path_parts = parsed_url.path.split('/')
        
        if 'd' in path_parts:
            d_index = path_parts.index('d')
            if d_index + 1 < len(path_parts):
                file_id = path_parts[d_index + 1]
                print(f"✅ ID файла успешно извлечен: {file_id}")
                return True
        
        print("❌ Не удалось извлечь ID файла из URL")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка обработки URL: {e}")
        return False

def test_basic_functionality():
    """Базовый тест функциональности без Google API"""
    print("🧪 Базовое тестирование функциональности...")
    
    # Тест 1: Проверка credentials
    test1 = test_credentials()
    
    # Тест 2: Проверка библиотек
    test2 = test_google_libraries()
    
    # Тест 3: Проверка URL
    test3 = test_document_url()
    
    return test1 and test2 and test3

def main():
    """Главная функция тестирования"""
    print("🚀 Тестирование готовности модуля управления документами")
    print("=" * 60)
    
    success = test_basic_functionality()
    
    print("=" * 60)
    if success:
        print("✅ Все проверки прошли успешно!")
        print("📄 Модуль управления документами готов к использованию")
        print()
        print("📋 Для полного тестирования:")
        print("   1. Запустите основное приложение: python main.py")
        print("   2. Откройте меню 'Документы' -> 'Управление доступом'")
        print("   3. Вставьте URL документа и протестируйте функции")
    else:
        print("❌ Обнаружены проблемы с настройкой")
        print("🔧 Исправьте ошибки перед использованием модуля")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
