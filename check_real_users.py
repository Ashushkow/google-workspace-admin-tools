#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования загрузки реальных пользователей Google Workspace
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def check_real_users():
    """Проверяем загрузку реальных пользователей"""
    print("=" * 70)
    print("🔍 ПРОВЕРКА РЕАЛЬНЫХ ПОЛЬЗОВАТЕЛЕЙ GOOGLE WORKSPACE")
    print("=" * 70)
    
    # Проверяем конфигурацию
    print("1. Проверяем конфигурацию...")
    from src.config.enhanced_config import config
    
    settings = config.settings
    print(f"   Домен: {settings.google_workspace_domain}")
    print(f"   Админ: {settings.google_workspace_admin}")
    print(f"   Режим разработки: {os.getenv('DEV_MODE', 'False')}")
    
    if settings.google_workspace_domain in ['testdomain.com', 'your-real-domain.com', 'yourdomain.com', 'example.com']:
        print("❌ ОШИБКА: Необходимо установить реальный домен Google Workspace!")
        print("   Откройте .env файл и замените:")
        print("   GOOGLE_WORKSPACE_DOMAIN=your-real-domain.com")
        print("   на ваш реальный домен Google Workspace")
        return False
        
    if settings.google_workspace_admin in ['admin@testdomain.com', 'admin@your-real-domain.com', 'admin@yourdomain.com']:
        print("❌ ОШИБКА: Необходимо установить реальный email администратора!")
        print("   Откройте .env файл и замените:")
        print("   GOOGLE_WORKSPACE_ADMIN=admin@your-real-domain.com")
        print("   на email администратора вашего Google Workspace")
        return False
    
    print("✅ Конфигурация выглядит корректно")
    
    # Проверяем credentials
    print("\\n2. Проверяем credentials.json...")
    creds_path = Path(settings.google_application_credentials)
    if not creds_path.exists():
        print(f"❌ ОШИБКА: Файл {creds_path} не найден!")
        return False
    
    try:
        import json
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        if 'installed' in creds_data:
            print("✅ OAuth 2.0 credentials найдены")
            client_id = creds_data['installed'].get('client_id', 'N/A')
            project_id = creds_data['installed'].get('project_id', 'N/A')
            print(f"   Client ID: {client_id}")
            print(f"   Project ID: {project_id}")
        else:
            print("❌ ОШИБКА: credentials.json не содержит OAuth 2.0 данные!")
            return False
            
    except Exception as e:
        print(f"❌ ОШИБКА: Не удалось прочитать credentials.json: {e}")
        return False
    
    # Проверяем подключение к Google API
    print("\\n3. Тестируем подключение к Google Workspace...")
    try:
        from src.auth import get_service, detect_credentials_type
        
        creds_type = detect_credentials_type()
        print(f"   Тип credentials: {creds_type}")
        
        if creds_type != 'oauth2':
            print("❌ ОШИБКА: Ожидался OAuth 2.0, но найден другой тип!")
            return False
        
        print("   Получаем Google API сервис...")
        print("   ⚠️  ВНИМАНИЕ: Может открыться браузер для авторизации!")
        
        service = get_service()
        if not service:
            print("❌ ОШИБКА: Не удалось получить Google API сервис!")
            return False
            
        print("✅ Google API сервис получен")
        
        # Проверяем домены
        print("\\n4. Проверяем доступ к доменам...")
        try:
            domains_result = service.domains().list(customer='my_customer').execute()
            domains = domains_result.get('domains', [])
            
            if not domains:
                print("❌ ОШИБКА: Домены не найдены!")
                print("   Возможные причины:")
                print("   - Аккаунт не имеет прав администратора")
                print("   - Неправильно настроен OAuth consent screen")
                print("   - Приложение не верифицировано")
                return False
                
            print(f"✅ Найдено доменов: {len(domains)}")
            for domain in domains:
                domain_name = domain.get('domainName', 'N/A')
                verified = domain.get('verified', False)
                print(f"   • {domain_name} (верифицирован: {verified})")
                
        except Exception as e:
            print(f"❌ ОШИБКА доступа к доменам: {e}")
            if "insufficient permissions" in str(e).lower():
                print("   🔒 Недостаточно прав доступа!")
                print("   Решение:")
                print("   1. Войдите в Google Cloud Console")
                print("   2. Настройте OAuth consent screen")
                print("   3. Добавьте необходимые scopes")
                print("   4. Убедитесь что используете аккаунт администратора")
            return False
        
        # Проверяем пользователей
        print("\\n5. Проверяем доступ к пользователям...")
        try:
            users_result = service.users().list(
                customer='my_customer',
                maxResults=5
            ).execute()
            
            users = users_result.get('users', [])
            if not users:
                print("❌ ОШИБКА: Пользователи не найдены!")
                print("   Возможные причины:")
                print("   - В домене нет пользователей")
                print("   - Недостаточно прав для просмотра пользователей")
                return False
                
            print(f"✅ Найдено пользователей: {len(users)}")
            print("   Первые 5 пользователей:")
            for i, user in enumerate(users[:5], 1):
                email = user.get('primaryEmail', 'N/A')
                name = user.get('name', {}).get('fullName', 'N/A')
                suspended = user.get('suspended', False)
                status = "приостановлен" if suspended else "активен"
                print(f"   {i}. {email} ({name}) - {status}")
                
            return True
            
        except Exception as e:
            print(f"❌ ОШИБКА доступа к пользователям: {e}")
            if "insufficient permissions" in str(e).lower():
                print("   🔒 Недостаточно прав для просмотра пользователей!")
            return False
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

def main():
    """Главная функция"""
    success = check_real_users()
    
    print("\\n" + "=" * 70)
    if success:
        print("🎉 ВСЁ РАБОТАЕТ! Реальные пользователи найдены!")
        print("\\nТеперь можете запустить основное приложение:")
        print("python main.py")
    else:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("\\nИнструкции по настройке:")
        print("1. Откройте .env файл")
        print("2. Установите реальный домен Google Workspace")
        print("3. Установите email администратора")
        print("4. Убедитесь что credentials.json настроен правильно")
        print("5. Проверьте права доступа в Google Cloud Console")
        print("\\nДокументация: docs/OAUTH2_SETUP.md")
    print("=" * 70)

if __name__ == "__main__":
    main()
