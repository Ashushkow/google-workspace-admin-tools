#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилита для интерактивной проверки подключения к Google Workspace через OAuth 2.0
"""

import sys
import os
import asyncio
from pathlib import Path

# Добавляем корневую папку в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

from src.api.google_api_client import GoogleAPIClient
from src.utils.enhanced_logger import setup_logging
from src.config.enhanced_config import config


def oauth2_check():
    """Проверка OAuth 2.0 подключения"""
    # Настраиваем логирование
    logger = setup_logging()
    
    print("🔐 ПРОВЕРКА OAUTH 2.0 ПОДКЛЮЧЕНИЯ К GOOGLE WORKSPACE")
    print("=" * 60)
    
    # Проверяем наличие credentials.json
    credentials_path = "credentials.json"
    if not os.path.exists(credentials_path):
        print("❌ Файл credentials.json не найден!")
        print("📋 Для настройки OAuth 2.0 выполните следующие шаги:")
        print("1. Перейдите в Google Cloud Console")
        print("2. Создайте проект и включите Admin SDK API")
        print("3. Создайте OAuth 2.0 credentials (Desktop Application)")
        print("4. Скачайте файл и переименуйте в credentials.json")
        print("5. Запустите эту утилиту снова")
        return False
    
    # Инициализируем клиент
    print("🔧 Инициализируем Google API клиент...")
    client = GoogleAPIClient(credentials_path)
    
    try:
        # Временно отключаем режим разработки
        os.environ['DEV_MODE'] = 'False'
        
        # Пытаемся инициализировать подключение
        if not client.initialize():
            print("❌ Не удалось инициализировать подключение к Google API")
            return False
        
        print("✅ Подключение к Google API успешно установлено!")
        
        # Получаем информацию о пользователях
        print("\n📊 Получаем информацию о пользователях...")
        users = client.get_users(max_results=5)
        
        if users:
            print(f"👥 Найдено пользователей: {len(users)}")
            print("📋 Первые 5 пользователей:")
            for i, user in enumerate(users[:5], 1):
                print(f"  {i}. {user.get('primaryEmail', 'N/A')} - {user.get('name', {}).get('fullName', 'N/A')}")
        else:
            print("⚠️ Пользователи не найдены или недостаточно прав")
        
        # Получаем информацию о группах
        print("\n📊 Получаем информацию о группах...")
        groups = client.get_groups(max_results=5)
        
        if groups:
            print(f"👥 Найдено групп: {len(groups)}")
            print("📋 Первые 5 групп:")
            for i, group in enumerate(groups[:5], 1):
                print(f"  {i}. {group.get('email', 'N/A')} - {group.get('name', 'N/A')}")
        else:
            print("⚠️ Группы не найдены или недостаточно прав")
        
        print("\n" + "=" * 60)
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА УСПЕШНО!")
        print("🎉 Google Workspace API готов к использованию через OAuth 2.0")
        print("=" * 60)
        
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Операция прервана пользователем")
        return False
    except Exception as e:
        print(f"\n❌ Ошибка при проверке подключения: {e}")
        logger.error(f"Ошибка проверки OAuth 2.0: {e}")
        return False
    finally:
        # Восстанавливаем режим разработки
        os.environ['DEV_MODE'] = 'True' if config.settings.dev_mode else 'False'


async def test_async_connection(client):
    """Тестирование асинхронного соединения"""
    return await client.test_connection()


def test_oauth_connection():
    """Функция для обратной совместимости"""
    print("🧪 ТЕСТИРОВАНИЕ GOOGLE API OAUTH 2.0")
    print("=" * 60)
    
    # Проверяем настройки
    print("⚙️ Текущие настройки:")
    print(f"   DEV_MODE: {config.settings.dev_mode}")
    print(f"   Домен: {config.settings.google_workspace_domain}")
    print(f"   Админ: {config.settings.google_workspace_admin}")
    
    return oauth2_check()


def main():
    """Главная функция"""
    success = oauth2_check()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
