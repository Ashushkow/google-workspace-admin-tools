#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка и диагностика Google Drive API
"""

import sys
import webbrowser
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config.enhanced_config import config


def check_drive_api_status():
    """Проверка статуса Google Drive API"""
    print("🔍 Диагностика Google Drive API...")
    print("=" * 60)
    
    # Информация о проекте
    print(f"📋 Информация о проекте:")
    
    try:
        # Попробуем извлечь project ID из credentials
        import json
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        if 'installed' in creds:
            client_id = creds['installed']['client_id']
            project_id = client_id.split('-')[0]
            print(f"   🔑 Client ID: {client_id}")
            print(f"   📦 Project ID: {project_id}")
        else:
            print("   ⚠️  Не удалось определить Project ID")
            project_id = "547622531218"  # Fallback из ошибки
            
    except Exception as e:
        print(f"   ❌ Ошибка чтения credentials.json: {e}")
        project_id = "547622531218"  # Fallback из ошибки
    
    print()
    print(f"🎯 Текущие OAuth scopes:")
    for i, scope in enumerate(config.google.scopes, 1):
        drive_scope = "✅" if "drive" in scope else "  "
        print(f"   {drive_scope} {i}. {scope}")
    
    print()
    print("🚨 ПРОБЛЕМА: Google Drive API не включен в проекте")
    print(f"   Project ID: {project_id}")
    print()
    
    # Предлагаем решения
    print("💡 РЕШЕНИЯ:")
    print()
    
    print("1️⃣ АВТОМАТИЧЕСКОЕ ВКЛЮЧЕНИЕ (РЕКОМЕНДУЕТСЯ):")
    api_url = f"https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project={project_id}"
    print(f"   🔗 {api_url}")
    print()
    
    print("2️⃣ РУЧНОЕ ВКЛЮЧЕНИЕ:")
    console_url = f"https://console.cloud.google.com/apis/library?project={project_id}"
    print(f"   🔗 {console_url}")
    print("   📝 Найдите 'Google Drive API' и нажмите 'Enable'")
    print()
    
    print("3️⃣ ЧЕРЕЗ GCLOUD CLI:")
    print(f"   gcloud config set project {project_id}")
    print("   gcloud services enable drive.googleapis.com")
    print()
    
    # Предлагаем открыть ссылку
    choice = input("🌐 Открыть ссылку для включения API автоматически? (y/n): ").lower().strip()
    if choice in ['y', 'yes', 'да', 'д']:
        print("🌐 Открываем браузер...")
        webbrowser.open(api_url)
        print("✅ Ссылка открыта в браузере")
        print()
        print("📋 ДАЛЬНЕЙШИЕ ДЕЙСТВИЯ:")
        print("   1. Включите Google Drive API в открывшейся странице")
        print("   2. Подождите 2-3 минуты")
        print("   3. Перезапустите приложение")
        print("   4. Попробуйте снова открыть управление документами")
    else:
        print("📋 Включите API вручную по одной из предложенных ссылок")
    
    print()
    print("⏰ ВАЖНО: После включения API подождите 2-3 минуты")
    print("   для распространения изменений в системе Google.")


def test_drive_api_after_enable():
    """Тест Drive API после включения"""
    print("\n🧪 Тестирование доступа к Drive API...")
    
    try:
        from src.api.google_api_client import GoogleAPIClient
        
        client = GoogleAPIClient(config.settings.google_application_credentials)
        if not client.initialize():
            print("❌ Не удалось инициализировать Google API клиент")
            return False
        
        creds = client.get_credentials()
        if not creds:
            print("❌ Не удалось получить credentials")
            return False
        
        from googleapiclient.discovery import build
        
        # Пробуем создать Drive service
        drive_service = build('drive', 'v3', credentials=creds)
        print("✅ Drive API сервис создан успешно")
        
        # Пробуем простой запрос (получение информации о пользователе)
        about = drive_service.about().get(fields="user").execute()
        user_email = about.get('user', {}).get('emailAddress', 'Неизвестно')
        print(f"✅ Подключение к Drive API успешно (пользователь: {user_email})")
        
        return True
        
    except Exception as e:
        if "accessNotConfigured" in str(e):
            print("❌ Drive API всё ещё не включен или изменения не распространились")
            print("   Подождите ещё несколько минут и попробуйте снова")
        else:
            print(f"❌ Ошибка тестирования Drive API: {e}")
        return False


if __name__ == "__main__":
    print("🔧 ДИАГНОСТИКА GOOGLE DRIVE API")
    print("=" * 60)
    
    check_drive_api_status()
    
    # Предлагаем протестировать после включения
    print("\n" + "=" * 60)
    test_choice = input("🧪 Протестировать доступ к Drive API сейчас? (y/n): ").lower().strip()
    if test_choice in ['y', 'yes', 'да', 'д']:
        success = test_drive_api_after_enable()
        if success:
            print("\n🎉 Drive API работает! Можно использовать управление документами.")
        else:
            print("\n💥 Drive API пока не работает. Проверьте включение API и повторите тест.")
    
    print("\n📚 Подробная инструкция: docs/ENABLE_DRIVE_API.md")
