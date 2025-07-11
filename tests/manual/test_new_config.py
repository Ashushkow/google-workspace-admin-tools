import os
import sys
from pathlib import Path

# Добавляем корневую папку в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# Принудительно перезагружаем .env
from dotenv import load_dotenv
load_dotenv(override=True)

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("=== ТЕКУЩИЕ НАСТРОЙКИ ===")
print(f"GOOGLE_WORKSPACE_DOMAIN: {os.getenv('GOOGLE_WORKSPACE_DOMAIN', 'НЕ НАЙДЕНО')}")
print(f"GOOGLE_WORKSPACE_ADMIN: {os.getenv('GOOGLE_WORKSPACE_ADMIN', 'НЕ НАЙДЕНО')}")
print(f"DEV_MODE: {os.getenv('DEV_MODE', 'НЕ НАЙДЕНО')}")
print()

# Тестируем подключение
try:
    from src.auth import get_service, detect_credentials_type
    
    print("=== ТЕСТ ПОДКЛЮЧЕНИЯ ===")
    creds_type = detect_credentials_type()
    print(f"Тип credentials: {creds_type}")
    
    if creds_type == 'oauth2':
        print("Получаем Google API сервис...")
        service = get_service()
        
        if service:
            print("✅ Сервис получен, тестируем пользователей...")
            
            try:
                result = service.users().list(customer='my_customer', maxResults=3).execute()
                users = result.get('users', [])
                
                if users:
                    print(f"✅ Найдено {len(users)} реальных пользователей:")
                    for user in users:
                        email = user.get('primaryEmail', 'N/A')
                        name = user.get('name', {}).get('fullName', 'N/A')
                        print(f"   • {email} ({name})")
                else:
                    print("⚠️  Пользователи не найдены")
                    
            except Exception as e:
                print(f"❌ Ошибка получения пользователей: {e}")
        else:
            print("❌ Не удалось получить сервис")
    else:
        print(f"❌ Неверный тип credentials: {creds_type}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
