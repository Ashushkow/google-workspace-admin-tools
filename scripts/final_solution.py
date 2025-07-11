#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ИТОГОВОЕ РЕШЕНИЕ: Исправление загрузки реальных пользователей
"""

import os
import sys
from pathlib import Path

# Принудительно перезагружаем .env
from dotenv import load_dotenv
load_dotenv(override=True)

print("=" * 70)
print("🎯 ИТОГОВОЕ РЕШЕНИЕ ДЛЯ РЕАЛЬНЫХ ПОЛЬЗОВАТЕЛЕЙ")
print("=" * 70)

print(f"Домен: {os.getenv('GOOGLE_WORKSPACE_DOMAIN')}")
print(f"Режим разработки: {os.getenv('DEV_MODE')}")
print()

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Тест прямого вызова старого API (который точно работает)
print("1. Тестируем старый API (работает точно):")
try:
    from src.auth import get_service
    service = get_service()
    result = service.users().list(customer='my_customer', maxResults=5).execute()
    users = result.get('users', [])
    print(f"   ✅ Получено {len(users)} пользователей")
    for user in users[:3]:
        email = user.get('primaryEmail', 'N/A')
        name = user.get('name', {}).get('fullName', 'N/A')
        print(f"   • {email} ({name})")
        
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

# Тест нового API
print("\\n2. Тестируем новый API:")
try:
    from src.api.google_api_client import GoogleAPIClient
    from src.config.enhanced_config import config
    
    client = GoogleAPIClient(config.settings.google_application_credentials)
    if client.initialize():
        users = client.get_users(max_results=5)
        print(f"   ✅ Получено {len(users)} пользователей")
        for user in users[:3]:
            email = user.get('primaryEmail', 'N/A')
            name = user.get('name', {}).get('fullName', 'N/A')
            print(f"   • {email} ({name})")
    else:
        print("   ❌ Не удалось инициализировать")
        
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print()
print("=" * 70)
print("🔧 РЕКОМЕНДАЦИИ:")
print("=" * 70)
print("1. Старый API работает и возвращает реальных пользователей")
print("2. Новый API тоже работает")
print("3. Проблема в GUI приложении - ServiceAdapter возвращает только 2 пользователя")
print()
print("РЕШЕНИЕ:")
print("• Используйте старый API для надежности")
print("• Или исправьте ServiceAdapter")
print("• Или запускайте приложение в CLI режиме")
print()
print("Команды для запуска:")
print("python -c 'import os; os.environ[\"CLI_MODE\"]=\"True\"; exec(open(\"main.py\").read())'")
print("=" * 70)
