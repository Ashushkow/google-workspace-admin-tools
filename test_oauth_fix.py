#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный тестовый скрипт для проверки исправления OAuth 2.0 загрузки пользователей
"""

import sys
import os
import asyncio
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config.enhanced_config import config
from src.api.google_api_client import GoogleAPIClient
from src.utils.enhanced_logger import setup_logging


async def test_oauth_users():
    """Тестируем загрузку пользователей через OAuth 2.0"""
    print("=" * 60)
    print("🧪 ТЕСТ ЗАГРУЗКИ ПОЛЬЗОВАТЕЛЕЙ ЧЕРЕЗ OAUTH 2.0")
    print("=" * 60)
    
    # Настройка логирования
    logger = setup_logging("DEBUG")
    
    try:
        # 1. Проверка конфигурации
        print("🔧 Проверяем конфигурацию...")
        settings = config.settings
        print(f"   Домен: {settings.google_workspace_domain}")
        print(f"   Админ: {settings.google_workspace_admin}")
        print(f"   Режим разработки: {os.getenv('DEV_MODE', 'False')}")
        print(f"   Credentials: {settings.google_application_credentials}")
        
        # 2. Проверка файла credentials
        creds_path = Path(settings.google_application_credentials)
        if not creds_path.exists():
            print(f"❌ Файл credentials не найден: {creds_path}")
            return
        print("✅ Файл credentials найден")
        
        # 3. Инициализация Google API клиента
        print("\\n🔑 Инициализируем Google API клиент...")
        client = GoogleAPIClient(settings.google_application_credentials)
        
        if not client.initialize():
            print("❌ Не удалось инициализировать Google API клиент")
            return
        print("✅ Google API клиент инициализирован")
        
        # 4. Тест подключения
        print("\\n🔍 Тестируем подключение...")
        if not await client.test_connection():
            print("❌ Тест подключения неуспешен")
            return
        print("✅ Подключение работает")
        
        # 5. Получение пользователей
        print("\\n👥 Получаем список пользователей...")
        users = client.get_users(max_results=10)
        
        if not users:
            print("⚠️ Пользователи не получены")
            return
            
        print(f"✅ Получено {len(users)} пользователей:")
        for i, user in enumerate(users[:5], 1):
            email = user.get('primaryEmail', 'N/A')
            name = user.get('name', {}).get('fullName', 'N/A')
            print(f"   {i}. {email} ({name})")
        
        if len(users) > 5:
            print(f"   ... и еще {len(users) - 5} пользователей")
        
        # 6. Простой тест через старый API
        print("\\n🏗️ Тестируем через старый API...")
        try:
            from src.auth import get_service, detect_credentials_type
            
            creds_type = detect_credentials_type()
            print(f"📄 Тип credentials: {creds_type}")
            
            if creds_type == 'oauth2':
                service = get_service()
                result = service.users().list(customer='my_customer', maxResults=3).execute()
                old_users = result.get('users', [])
                print(f"✅ Через старый API получено {len(old_users)} пользователей")
            else:
                print("⚠️ Credentials не OAuth 2.0, пропускаем тест старого API")
                
        except Exception as e:
            print(f"⚠️ Ошибка старого API: {e}")
        
        print("\\n🎉 ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка во время теста: {e}")
        logger.error(f"Ошибка теста: {e}", exc_info=True)
        return False


async def test_oauth_flow():
    """Тестируем OAuth 2.0 flow отдельно"""
    print("\\n" + "=" * 60)
    print("🔐 ТЕСТ OAUTH 2.0 FLOW")
    print("=" * 60)
    
    try:
        from src.auth import get_service, detect_credentials_type
        
        # Проверяем тип credentials
        creds_type = detect_credentials_type()
        print(f"📄 Тип credentials: {creds_type}")
        
        if creds_type != 'oauth2':
            print("⚠️ Файл credentials не содержит OAuth 2.0 данные")
            return False
        
        # Пробуем получить сервис
        print("🔧 Получаем Google API сервис...")
        service = get_service()
        
        if not service:
            print("❌ Не удалось получить Google API сервис")
            return False
        
        print("✅ Google API сервис получен")
        
        # Тестируем получение пользователей через старый API
        print("👥 Получаем пользователей через старый API...")
        result = service.users().list(customer='my_customer', maxResults=5).execute()
        users = result.get('users', [])
        
        print(f"✅ Получено {len(users)} пользователей через старый API")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка OAuth 2.0 flow: {e}")
        return False


def main():
    """Главная функция"""
    print("🚀 Запуск тестирования исправления OAuth 2.0...")
    
    try:
        # Тест нового API
        success1 = asyncio.run(test_oauth_users())
        
        # Тест старого API для совместимости
        success2 = asyncio.run(test_oauth_flow())
        
        if success1 and success2:
            print("\\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("OAuth 2.0 загрузка пользователей работает корректно.")
        else:
            print("\\n⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
            print("Проверьте логи для диагностики проблем.")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
