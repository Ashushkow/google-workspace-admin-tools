#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для проверки реальных пользователей через новый API
"""

import os
import sys
from pathlib import Path

# Принудительно перезагружаем .env
from dotenv import load_dotenv
load_dotenv(override=True)

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.api.google_api_client import GoogleAPIClient
from src.config.enhanced_config import config

def test_real_users_new_api():
    """Тестируем получение реальных пользователей через новый API"""
    print("=== ТЕСТ НОВОГО API ===")
    
    settings = config.settings
    print(f"Домен: {settings.google_workspace_domain}")
    print(f"DEV_MODE: {os.getenv('DEV_MODE')}")
    
    # Создаем клиент
    client = GoogleAPIClient(settings.google_application_credentials)
    
    # Инициализируем
    if client.initialize():
        print("✅ GoogleAPIClient инициализирован")
        
        # Получаем пользователей
        users = client.get_users(max_results=10)
        print(f"Получено пользователей: {len(users)}")
        
        for user in users:
            email = user.get('primaryEmail', 'N/A')
            name = user.get('name', {}).get('fullName', 'N/A')
            print(f"   • {email} ({name})")
    else:
        print("❌ Не удалось инициализировать GoogleAPIClient")

if __name__ == "__main__":
    test_real_users_new_api()
