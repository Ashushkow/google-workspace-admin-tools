#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для отладки OAuth 2.0 загрузки пользователей.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Добавляем корневую папку в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Загружаем .env переменные
from dotenv import load_dotenv
load_dotenv(override=True)

# Принудительно устанавливаем DEV_MODE=False для тестирования реального API
os.environ['DEV_MODE'] = 'False'

from src.api.google_api_client import GoogleAPIClient
from src.config.enhanced_config import config

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_oauth2_debug():
    """Тестирование OAuth 2.0 с подробной отладкой"""
    print("=" * 80)
    print("🔍 ТЕСТИРОВАНИЕ OAUTH 2.0 И ЗАГРУЗКИ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 80)
    
    # Проверяем наличие файлов
    print("\n1. Проверка файлов конфигурации:")
    credentials_file = Path("credentials.json")
    if credentials_file.exists():
        print(f"✅ credentials.json найден: {credentials_file.absolute()}")
        
        # Проверяем тип credentials
        try:
            import json
            with open(credentials_file, 'r') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data:
                print("✅ Обнаружены OAuth 2.0 credentials")
                print(f"   Client ID: {creds_data['installed']['client_id']}")
                print(f"   Project ID: {creds_data['installed']['project_id']}")
            else:
                print("⚠️ Неизвестный тип credentials")
                
        except Exception as e:
            print(f"❌ Ошибка чтения credentials.json: {e}")
    else:
        print(f"❌ credentials.json не найден")
        return False
    
    # Проверяем .env файл
    env_file = Path(".env")
    if env_file.exists():
        print(f"✅ .env файл найден")
        
        # Читаем содержимое .env файла напрямую
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        # Ищем DEV_MODE в содержимом
        if 'DEV_MODE' in env_content:
            for line in env_content.split('\n'):
                if line.strip().startswith('DEV_MODE'):
                    print(f"   Содержимое .env: {line.strip()}")
                    break
        
        # Принудительно перезагружаем .env
        load_dotenv(override=True)
        
        print(f"   DEV_MODE (из os.getenv): {os.getenv('DEV_MODE', 'False')}")
        
        # Печатаем актуальное значение после принудительного изменения
        print(f"   DEV_MODE (после принудительного изменения): {os.getenv('DEV_MODE', 'False')}")
        print(f"   GOOGLE_WORKSPACE_DOMAIN: {os.getenv('GOOGLE_WORKSPACE_DOMAIN', 'не установлен')}")
        print(f"   GOOGLE_WORKSPACE_ADMIN: {os.getenv('GOOGLE_WORKSPACE_ADMIN', 'не установлен')}")
    else:
        print(f"⚠️ .env файл не найден")
    
    # Проверяем token.pickle
    token_file = Path("token.pickle")
    if token_file.exists():
        print(f"✅ token.pickle найден (размер: {token_file.stat().st_size} байт)")
        
        # Проверяем можем ли загрузить токен
        try:
            import pickle
            with open(token_file, 'rb') as f:
                token_data = pickle.load(f)
            print(f"✅ Токен успешно загружен")
            if hasattr(token_data, 'valid'):
                print(f"   Валидность: {token_data.valid}")
            if hasattr(token_data, 'expired'):
                print(f"   Истек: {token_data.expired}")
        except Exception as e:
            print(f"❌ Ошибка загрузки токена: {e}")
    else:
        print(f"⚠️ token.pickle не найден (потребуется новая авторизация)")
    
    print("\n2. Инициализация Google API Client:")
    try:
        client = GoogleAPIClient(credentials_path="credentials.json")
        print("✅ Google API Client создан")
        
        # Пытаемся инициализировать
        print("🔧 Инициализация клиента...")
        success = client.initialize()
        
        if success:
            print("✅ Клиент инициализирован успешно")
        else:
            print("❌ Ошибка инициализации клиента")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка создания клиента: {e}")
        return False
    
    print("\n3. Тестирование подключения:")
    try:
        # Проверяем подключение асинхронно
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        connection_ok = loop.run_until_complete(client.test_connection())
        
        if connection_ok:
            print("✅ Подключение к Google API работает")
        else:
            print("❌ Проблема с подключением к Google API")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования подключения: {e}")
    finally:
        loop.close()
    
    print("\n4. Загрузка пользователей:")
    try:
        print("👥 Запрашиваем список пользователей...")
        users = client.get_users(max_results=10)
        
        if users:
            print(f"✅ Получено {len(users)} пользователей:")
            for i, user in enumerate(users[:5]):
                email = user.get('primaryEmail', 'N/A')
                name = user.get('name', {}).get('fullName', 'N/A')
                suspended = user.get('suspended', False)
                print(f"   {i+1}. {email} ({name}) {'[ЗАБЛОКИРОВАН]' if suspended else ''}")
            
            if len(users) > 5:
                print(f"   ... и еще {len(users) - 5} пользователей")
                
        else:
            print("❌ Пользователи не найдены")
            print("💡 Возможные причины:")
            print("   • Нет пользователей в домене")
            print("   • Недостаточно прав доступа")
            print("   • Неправильные scopes в OAuth")
            print("   • Проблемы с авторизацией")
            
    except Exception as e:
        print(f"❌ Ошибка загрузки пользователей: {e}")
    
    print("\n5. Диагностика режима разработки:")
    is_dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'
    print(f"DEV_MODE: {is_dev_mode}")
    
    if is_dev_mode:
        print("🔧 Режим разработки активен - используются демо данные")
        print("💡 Для тестирования реального API отключите DEV_MODE в .env")
    
    print("\n" + "=" * 80)
    print("🔍 ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        test_oauth2_debug()
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
