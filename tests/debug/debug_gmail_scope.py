#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детальная диагностика Gmail API для решения проблемы insufficient scopes.
"""

import sys
import os
import pickle
from pathlib import Path

# Добавляем src в Python path  
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def analyze_token_details():
    """Анализ деталей токена"""
    print("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ТОКЕНА")
    print("=" * 50)
    
    token_path = Path("token.pickle")
    
    if not token_path.exists():
        print("❌ Токен не найден")
        return False
    
    try:
        with open(token_path, 'rb') as token_file:
            credentials = pickle.load(token_file)
        
        print(f"📊 Тип объекта: {type(credentials)}")
        print(f"✅ Токен валиден: {credentials.valid}")
        print(f"⏰ Токен истек: {credentials.expired}")
        
        if hasattr(credentials, 'scopes'):
            print(f"\n📋 Scopes в токене:")
            for i, scope in enumerate(credentials.scopes or [], 1):
                is_gmail = " ← GMAIL!" if 'gmail' in scope else ""
                print(f"  {i}. {scope}{is_gmail}")
            
            gmail_scope = 'https://www.googleapis.com/auth/gmail.send'
            if gmail_scope in (credentials.scopes or []):
                print(f"\n✅ Gmail scope найден в токене!")
            else:
                print(f"\n❌ Gmail scope НЕ найден в токене!")
                print(f"🔍 Ожидаемый scope: {gmail_scope}")
        
        if hasattr(credentials, 'token'):
            print(f"\n🔑 Access token присутствует: {bool(credentials.token)}")
        
        if hasattr(credentials, 'refresh_token'):
            print(f"🔄 Refresh token присутствует: {bool(credentials.refresh_token)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа токена: {e}")
        return False


def test_gmail_api_call():
    """Тестирование прямого вызова Gmail API"""
    print(f"\n🧪 ТЕСТИРОВАНИЕ ПРЯМОГО ВЫЗОВА GMAIL API")
    print("=" * 50)
    
    try:
        from src.api.google_api_client import GoogleAPIClient
        from src.config.enhanced_config import config
        
        client = GoogleAPIClient(config.settings.google_application_credentials)
        
        if not client.initialize():
            print("❌ Не удалось инициализировать клиент")
            return False
        
        print("✅ Google API клиент инициализирован")
        
        # Попробуем создать Gmail сервис напрямую
        try:
            from googleapiclient.discovery import build
            gmail_service = build('gmail', 'v1', credentials=client.credentials)
            print("✅ Gmail сервис создан")
            
            # Попробуем получить профиль
            try:
                profile = gmail_service.users().getProfile(userId='me').execute()
                print(f"✅ Профиль получен: {profile.get('emailAddress')}")
                return True
            except Exception as profile_error:
                print(f"❌ Ошибка получения профиля: {profile_error}")
                
                # Попробуем более простой вызов - список ярлыков
                try:
                    labels = gmail_service.users().labels().list(userId='me').execute()
                    print(f"✅ Список ярлыков получен: {len(labels.get('labels', []))} ярлыков")
                    return True
                except Exception as labels_error:
                    print(f"❌ Ошибка получения ярлыков: {labels_error}")
                    return False
                    
        except Exception as service_error:
            print(f"❌ Ошибка создания Gmail сервиса: {service_error}")
            return False
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False


def check_oauth_consent_status():
    """Проверка статуса OAuth Consent Screen"""
    print(f"\n📋 ПРОВЕРКА OAUTH CONSENT SCREEN")
    print("=" * 50)
    
    print("🔍 Требуемые действия в Google Cloud Console:")
    print("")
    print("1. 🌐 Откройте console.cloud.google.com")
    print("2. 📂 Выберите ваш проект")
    print("3. 🔧 APIs & Services → OAuth consent screen")
    print("4. ✏️ Нажмите 'EDIT APP'")
    print("5. 📋 Перейдите к шагу 'Scopes'")
    print("6. ➕ Нажмите 'ADD OR REMOVE SCOPES'")
    print("7. 🔍 Найдите 'Gmail API'")
    print("8. ✅ Отметьте: 'Send email on your behalf'")
    print("   📎 Scope: https://www.googleapis.com/auth/gmail.send")
    print("9. 💾 Нажмите 'UPDATE'")
    print("10. ✅ Завершите настройку")
    
    print(f"\n⚠️ КРИТИЧЕСКИ ВАЖНО:")
    print("Gmail scope должен быть добавлен именно в OAuth consent screen,")
    print("а не только в конфигурацию приложения!")


def suggest_immediate_fix():
    """Предложить немедленное исправление"""
    print(f"\n🛠️ НЕМЕДЛЕННОЕ ИСПРАВЛЕНИЕ")
    print("=" * 50)
    
    print("Судя по ошибке 'insufficient authentication scopes',")
    print("Gmail scope не был добавлен в OAuth consent screen.")
    print("")
    print("📋 ПОШАГОВОЕ РЕШЕНИЕ:")
    print("")
    print("1. ✅ Добавьте Gmail scope в OAuth consent screen (см. выше)")
    print("2. 🗑️ Удалите текущий токен:")
    print("   rm token.pickle")
    print("3. 🔄 Запустите приложение для повторной авторизации:")
    print("   python main.py")
    print("4. ✅ Проверьте результат:")
    print("   python setup_gmail_api.py")
    
    print(f"\n💡 АЛЬТЕРНАТИВА:")
    print("Если проблема сохраняется, возможно Gmail API не включен:")
    print("APIs & Services → Library → 'Gmail API' → ENABLE")


def main():
    """Главная функция детальной диагностики"""
    print("🔬 ДЕТАЛЬНАЯ ДИАГНОСТИКА GMAIL API")
    print("=" * 60)
    print("Анализируем проблему 'insufficient authentication scopes'\n")
    
    # Анализируем токен
    token_ok = analyze_token_details()
    
    # Тестируем API
    api_ok = test_gmail_api_call()
    
    # Показываем инструкции
    check_oauth_consent_status()
    
    # Предлагаем решение
    suggest_immediate_fix()
    
    print(f"\n📊 ЗАКЛЮЧЕНИЕ:")
    print("=" * 50)
    
    if not api_ok:
        print("❌ Gmail API недоступен из-за отсутствующего scope")
        print("🔧 Добавьте Gmail scope в OAuth consent screen")
        print("📋 Следуйте инструкциям выше")
    else:
        print("✅ Gmail API работает корректно!")


if __name__ == "__main__":
    main()
