#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Мастер настройки Admin Team Tools с Gmail API.
"""

import sys
import os
import json
from pathlib import Path

# Добавляем src в Python path  
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config.enhanced_config import config


def check_credentials():
    """Проверка наличия и типа credentials"""
    print("🔍 Проверка учетных данных...")
    
    credentials_path = Path("credentials.json")
    
    if not credentials_path.exists():
        print("❌ Файл credentials.json не найден")
        print("📋 Создайте учетные данные в Google Cloud Console:")
        print("   1. Перейдите в https://console.cloud.google.com/")
        print("   2. APIs & Services → Credentials")
        print("   3. Create Credentials → OAuth 2.0 Client ID")
        print("   4. Application type: Desktop Application")
        print("   5. Скачайте JSON файл как credentials.json")
        return False
    
    try:
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
        
        if 'installed' in creds_data:
            print("✅ OAuth 2.0 credentials найдены")
            return True
        elif 'type' in creds_data and creds_data['type'] == 'service_account':
            print("⚙️ Service Account credentials найдены")
            print("💡 Рекомендуется использовать OAuth 2.0 для Gmail API")
            return True
        else:
            print("❌ Неизвестный формат credentials.json")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка чтения credentials.json: {e}")
        return False


def check_gmail_scopes():
    """Проверка Gmail scopes"""
    print("\n🔍 Проверка Gmail scopes...")
    
    gmail_scope = 'https://www.googleapis.com/auth/gmail.send'
    
    if gmail_scope in config.google.scopes:
        print("✅ Gmail scope настроен")
        return True
    else:
        print("❌ Gmail scope отсутствует")
        return False


def check_token_status():
    """Проверка статуса токена"""
    print("\n🔍 Проверка токена авторизации...")
    
    token_path = Path("token.pickle")
    
    if not token_path.exists():
        print("⚠️ Токен авторизации отсутствует")
        print("💡 При первом запуске откроется браузер для авторизации")
        return False
    
    print("✅ Токен авторизации найден")
    return True


def test_google_api():
    """Тестирование Google API"""
    print("\n🧪 Тестирование Google API...")
    
    try:
        from src.api.google_api_client import GoogleAPIClient
        
        client = GoogleAPIClient(config.settings.google_application_credentials)
        
        if client.initialize():
            print("✅ Google API инициализирован успешно")
            
            # Проверяем Gmail API
            if hasattr(client, 'gmail_service') and client.gmail_service:
                print("✅ Gmail API доступен")
                return True
            else:
                print("⚠️ Gmail API недоступен")
                return False
        else:
            print("❌ Не удалось инициализировать Google API")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования API: {e}")
        return False


def test_gmail_functionality():
    """Тестирование Gmail функциональности"""
    print("\n📧 Тестирование Gmail функциональности...")
    
    try:
        from src.api.google_api_client import GoogleAPIClient
        from src.api.gmail_api import create_gmail_service
        
        client = GoogleAPIClient(config.settings.google_application_credentials)
        
        if not client.initialize():
            print("❌ Не удалось инициализировать Google API")
            return False
        
        gmail_service = create_gmail_service(client.credentials)
        
        if not gmail_service:
            print("❌ Не удалось создать Gmail сервис")
            return False
        
        if gmail_service.test_gmail_access():
            print("✅ Gmail API полностью функционален")
            return True
        else:
            print("❌ Gmail API недоступен")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования Gmail: {e}")
        return False


def show_next_steps():
    """Показать следующие шаги"""
    print("\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
    print("=" * 50)
    print("1. 📧 Запустите приложение: python main.py")
    print("2. 🔧 Создайте тестового пользователя")
    print("3. ✅ Убедитесь, что отмечен checkbox 'Отправить приветственное письмо'")
    print("4. 📨 Проверьте, что письмо дошло до получателя")
    print("5. 🎉 Готово! Gmail API настроен и работает")
    
    print("\n📋 ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ:")
    print("- python test_gmail_api.py - полное тестирование Gmail API") 
    print("- python demo_welcome_email.py - демонстрация отправки письма")
    
    print("\n📖 ДОКУМЕНТАЦИЯ:")
    print("- docs/GMAIL_API_SETUP.md - полное руководство по настройке")
    print("- docs/GOOGLE_API_SETUP.md - основная настройка Google API")


def show_troubleshooting():
    """Показать решение проблем"""
    print("\n🔧 РЕШЕНИЕ ПРОБЛЕМ:")
    print("=" * 50)
    
    print("❌ Gmail API недоступен:")
    print("   1. Включите Gmail API в Google Cloud Console")
    print("   2. Добавьте gmail.send scope в OAuth consent screen")
    print("   3. Удалите token.pickle и повторите авторизацию")
    
    print("\n❌ Письма не отправляются:")
    print("   1. Проверьте права администратора Google Workspace")
    print("   2. Убедитесь в корректности настройки admin_email")
    print("   3. Проверьте логи приложения на ошибки")
    
    print("\n❌ Письма в спаме:")
    print("   1. Настройте SPF записи для домена")
    print("   2. Включите DKIM в Google Workspace")
    print("   3. Первое письмо может попасть в спам - это нормально")


def main():
    """Главная функция мастера настройки"""
    print("🧙‍♂️ МАСТЕР НАСТРОЙКИ ADMIN TEAM TOOLS + GMAIL API")
    print("=" * 60)
    print("Этот мастер поможет настроить отправку приветственных писем")
    print("для новых пользователей Google Workspace.\n")
    
    # Проверяем компоненты
    checks = [
        ("Учетные данные", check_credentials),
        ("Gmail scopes", check_gmail_scopes), 
        ("Токен авторизации", check_token_status),
        ("Google API", test_google_api),
        ("Gmail функциональность", test_gmail_functionality)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Ошибка при проверке {name}: {e}")
            results.append((name, False))
    
    # Показываем итоги
    print("\n📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if not result:
            all_passed = False
    
    # Заключение
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("Gmail API готов к использованию!")
        show_next_steps()
    else:
        print("⚠️ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ НАСТРОЙКА")
        print("Некоторые компоненты требуют внимания.")
        show_troubleshooting()
        
        print("\n📞 НУЖНА ПОМОЩЬ?")
        print("1. Изучите документацию: docs/GMAIL_API_SETUP.md")
        print("2. Запустите диагностику: python test_gmail_api.py")
        print("3. Проверьте логи приложения")


if __name__ == "__main__":
    main()
