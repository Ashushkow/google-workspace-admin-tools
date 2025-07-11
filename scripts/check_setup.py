#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки настройки Google API.
"""

import os
import json

def check_credentials_file():
    """Проверка файла credentials.json"""
    print("🔍 Проверка credentials.json...")
    
    if not os.path.exists('credentials.json'):
        print("❌ Файл credentials.json не найден в корневой папке")
        print("📋 Что нужно сделать:")
        print("   1. Откройте docs/API_SETUP.md")
        print("   2. Создайте проект в Google Cloud Console")
        print("   3. Включите Admin SDK API и Calendar API")
        print("   4. Создайте OAuth 2.0 credentials")
        print("   5. Скачайте credentials.json")
        print("   6. Поместите файл в корневую папку проекта")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
            
        if creds.get('type') == 'service_account':
            print("✅ credentials.json найден (Service Account)")
            client_email = creds.get('client_email', '')
            if client_email:
                print(f"📧 Service Account: {client_email}")
                print("⚠️  Убедитесь, что Service Account имеет права Domain-wide delegation")
                return True
            else:
                print("❌ Service Account не содержит client_email")
                return False
                
        elif 'installed' in creds:
            client_id = creds['installed'].get('client_id', '')
            if 'YOUR_CLIENT_ID' in client_id:
                print("❌ credentials.json содержит тестовые данные")
                print("📋 Замените содержимое на данные из Google Cloud Console")
                return False
            else:
                print("✅ credentials.json найден (OAuth 2.0)")
                return True
        else:
            print("❌ Неверный формат credentials.json")
            print("📋 Поддерживаются только Service Account и OAuth 2.0 credentials")
            return False
            
    except json.JSONDecodeError:
        print("❌ credentials.json поврежден (неверный JSON)")
        return False
    except Exception as e:
        print(f"❌ Ошибка чтения credentials.json: {e}")
        return False

def check_dependencies():
    """Проверка зависимостей"""
    print("\n🔍 Проверка зависимостей...")
    
    try:
        import google.auth
        import googleapiclient.discovery
        print("✅ Google API библиотеки установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствуют зависимости: {e}")
        print("📋 Установите зависимости: pip install -r requirements.txt")
        return False

def check_internet():
    """Проверка интернет-соединения"""
    print("\n🔍 Проверка интернет-соединения...")
    
    try:
        import urllib.request
        urllib.request.urlopen('https://www.googleapis.com', timeout=5)
        print("✅ Интернет-соединение в порядке")
        return True
    except Exception:
        print("❌ Нет доступа к Google APIs")
        print("📋 Проверьте интернет-соединение и firewall")
        return False

def main():
    """Основная функция проверки"""
    print("🚀 Проверка настройки Admin Team Tools\n")
    
    all_good = True
    
    # Проверяем все компоненты
    all_good &= check_credentials_file()
    all_good &= check_dependencies() 
    all_good &= check_internet()
    
    print("\n" + "="*50)
    if all_good:
        print("🎉 Все настройки в порядке! Можно запускать приложение.")
        print("💡 Запуск: python main.py")
    else:
        print("❌ Обнаружены проблемы с настройкой")
        print("📖 Полные инструкции: docs/API_SETUP.md")

if __name__ == "__main__":
    main()
