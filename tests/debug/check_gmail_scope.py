#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка Gmail scope в OAuth consent screen и токене.
"""

import sys
import os
import pickle
import json
from pathlib import Path

# Добавляем src в Python path  
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config.enhanced_config import config


def check_required_scopes():
    """Проверка требуемых scopes в конфигурации"""
    print("📋 ТРЕБУЕМЫЕ SCOPES В КОНФИГУРАЦИИ:")
    print("=" * 50)
    
    gmail_scope = 'https://www.googleapis.com/auth/gmail.send'
    
    for i, scope in enumerate(config.google.scopes, 1):
        is_gmail = "📧" if scope == gmail_scope else "  "
        print(f"{is_gmail} {i}. {scope}")
    
    if gmail_scope in config.google.scopes:
        print(f"\n✅ Gmail scope найден в позиции {config.google.scopes.index(gmail_scope) + 1}")
        return True
    else:
        print(f"\n❌ Gmail scope отсутствует в конфигурации")
        return False


def check_token_scopes():
    """Проверка scopes в сохраненном токене"""
    print(f"\n🔍 ПРОВЕРКА SCOPES В ТОКЕНЕ:")
    print("=" * 50)
    
    token_path = Path("token.pickle")
    
    if not token_path.exists():
        print("⚠️ Файл token.pickle не найден")
        print("💡 Токен будет создан при первом запуске приложения")
        return False
    
    try:
        with open(token_path, 'rb') as token_file:
            credentials = pickle.load(token_file)
        
        if hasattr(credentials, 'scopes') and credentials.scopes:
            print("📊 Scopes в текущем токене:")
            gmail_scope = 'https://www.googleapis.com/auth/gmail.send'
            gmail_found = False
            
            for i, scope in enumerate(credentials.scopes, 1):
                is_gmail = "📧" if scope == gmail_scope else "  "
                if scope == gmail_scope:
                    gmail_found = True
                print(f"{is_gmail} {i}. {scope}")
            
            if gmail_found:
                print(f"\n✅ Gmail scope найден в токене!")
                return True
            else:
                print(f"\n❌ Gmail scope ОТСУТСТВУЕТ в текущем токене!")
                print("🔄 Требуется обновление токена")
                return False
        else:
            print("⚠️ Информация о scopes в токене недоступна")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка чтения токена: {e}")
        return False


def check_oauth_consent_setup():
    """Проверка настройки OAuth consent screen"""
    print(f"\n🌐 НАСТРОЙКА OAUTH CONSENT SCREEN:")
    print("=" * 50)
    
    print("📋 Для корректной работы Gmail API необходимо:")
    print("1. ✅ Включить Gmail API в Google Cloud Console")
    print("2. ✅ Добавить следующие scopes в OAuth consent screen:")
    
    required_scopes = [
        'https://www.googleapis.com/auth/admin.directory.user',
        'https://www.googleapis.com/auth/admin.directory.group',
        'https://www.googleapis.com/auth/admin.directory.group.member',
        'https://www.googleapis.com/auth/admin.directory.orgunit',
        'https://www.googleapis.com/auth/admin.directory.domain.readonly',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/gmail.send'  # ← ЭТОТ SCOPE КРИТИЧЕН!
    ]
    
    for i, scope in enumerate(required_scopes, 1):
        is_gmail = "📧 [НОВЫЙ]" if 'gmail.send' in scope else ""
        print(f"   {i}. {scope} {is_gmail}")
    
    print(f"\n🔗 Инструкция по добавлению scopes:")
    print("1. Откройте Google Cloud Console")
    print("2. Перейдите в 'APIs & Services' → 'OAuth consent screen'")
    print("3. Нажмите 'EDIT APP'")
    print("4. Перейдите на шаг 'Scopes'")
    print("5. Нажмите 'ADD OR REMOVE SCOPES'")
    print("6. Найдите и добавьте недостающие scopes")
    print("7. Обязательно добавьте 'Gmail API' → 'Send email on your behalf'")
    print("8. Сохраните изменения")


def suggest_fix_steps():
    """Предложить шаги для исправления"""
    print(f"\n🔧 ПОШАГОВОЕ ИСПРАВЛЕНИЕ:")
    print("=" * 50)
    
    print("1. 🌐 Откройте Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    
    print("2. 📂 Выберите ваш проект")
    
    print("3. 🔧 Включите Gmail API:")
    print("   APIs & Services → Library → 'Gmail API' → Enable")
    
    print("4. ⚙️ Обновите OAuth consent screen:")
    print("   APIs & Services → OAuth consent screen → EDIT APP")
    
    print("5. 📋 Добавьте Gmail scope:")
    print("   Scopes → ADD OR REMOVE SCOPES → Gmail API")
    print("   ✅ Выберите: '../auth/gmail.send - Send email on your behalf'")
    
    print("6. 💾 Сохраните изменения")
    
    print("7. 🔄 Обновите токен:")
    print("   python update_oauth_token.py")
    
    print("8. 🚀 Перезапустите приложение:")
    print("   python main.py")
    
    print("9. ✅ Проверьте настройку:")
    print("   python setup_gmail_api.py")


def main():
    """Главная функция диагностики"""
    print("🔍 ДИАГНОСТИКА GMAIL SCOPE В OAUTH CONSENT SCREEN")
    print("=" * 60)
    print("Проверяем настройку Gmail API для отправки приветственных писем\n")
    
    # Проверяем конфигурацию
    config_ok = check_required_scopes()
    
    # Проверяем токен
    token_ok = check_token_scopes()
    
    # Показываем инструкции
    check_oauth_consent_setup()
    
    # Итоговая оценка
    print(f"\n📊 РЕЗУЛЬТАТ ДИАГНОСТИКИ:")
    print("=" * 50)
    
    print(f"✅ Конфигурация scopes: {'OK' if config_ok else 'ОШИБКА'}")
    print(f"{'✅' if token_ok else '❌'} Токен содержит Gmail scope: {'OK' if token_ok else 'ТРЕБУЕТ ОБНОВЛЕНИЯ'}")
    
    if config_ok and token_ok:
        print(f"\n🎉 ВСЕ НАСТРОЕНО КОРРЕКТНО!")
        print("Gmail API готов к использованию")
        print("\n📧 Попробуйте создать пользователя с отправкой письма")
    else:
        print(f"\n⚠️ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ НАСТРОЙКА")
        
        if config_ok and not token_ok:
            print("💡 Конфигурация корректна, но токен нужно обновить")
            print("🔄 Запустите: python update_oauth_token.py")
        
        suggest_fix_steps()


if __name__ == "__main__":
    main()
