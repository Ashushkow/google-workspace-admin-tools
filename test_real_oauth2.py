#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест OAuth 2.0 без режима разработки.
"""

import os
import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Принудительно отключаем DEV_MODE
os.environ['DEV_MODE'] = 'False'

# Теперь импортируем модули
from dotenv import load_dotenv
load_dotenv(override=True)

import logging
from src.api.google_api_client import GoogleAPIClient

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_real_oauth2():
    """Тестирование реального OAuth 2.0"""
    print("=" * 60)
    print("🔑 ТЕСТ РЕАЛЬНОГО OAUTH 2.0")
    print("=" * 60)
    
    print(f"DEV_MODE: {os.getenv('DEV_MODE', 'False')}")
    
    # Создаем клиент
    client = GoogleAPIClient(credentials_path="credentials.json")
    
    # Инициализируем
    print("🔧 Инициализация Google API клиента...")
    success = client.initialize()
    
    if not success:
        print("❌ Не удалось инициализировать клиент")
        return False
    
    print("✅ Клиент инициализирован")
    
    # Тестируем загрузку пользователей
    print("👥 Загрузка пользователей...")
    users = client.get_users(max_results=5)
    
    if users:
        print(f"✅ Найдено {len(users)} пользователей:")
        for user in users:
            email = user.get('primaryEmail', 'N/A')
            name = user.get('name', {}).get('fullName', 'N/A')
            print(f"  • {email} ({name})")
    else:
        print("❌ Пользователи не найдены")
    
    print("=" * 60)
    return len(users) > 0

if __name__ == "__main__":
    try:
        test_real_oauth2()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
