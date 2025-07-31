#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диагностика OAuth 2.0 токена и scopes.
"""

import os
import pickle
import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config.enhanced_config import config


def check_token_scopes():
    """Проверка scopes в сохраненном токене"""
    token_path = "token.pickle"
    
    print("🔍 Диагностика OAuth 2.0 токена и scopes")
    print("=" * 60)
    
    # Проверяем конфигурацию
    print(f"📋 Требуемые scopes из конфигурации:")
    for i, scope in enumerate(config.google.scopes, 1):
        print(f"  {i}. {scope}")
    print()
    
    # Проверяем токен
    if os.path.exists(token_path):
        try:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
            
            print(f"✅ Токен найден: {token_path}")
            print(f"🔓 Действителен: {'Да' if creds.valid else 'Нет'}")
            print(f"⏰ Истек: {'Да' if creds.expired else 'Нет'}")
            
            # Проверяем scopes в токене
            if hasattr(creds, 'scopes') and creds.scopes:
                print(f"\n📊 Scopes в текущем токене:")
                for i, scope in enumerate(creds.scopes, 1):
                    print(f"  {i}. {scope}")
                
                # Проверяем, есть ли нужный scope
                member_scope = 'https://www.googleapis.com/auth/admin.directory.group.member'
                if member_scope in creds.scopes:
                    print(f"\n✅ Scope для управления участниками групп НАЙДЕН")
                else:
                    print(f"\n❌ Scope для управления участниками групп ОТСУТСТВУЕТ")
                    print(f"   Отсутствует: {member_scope}")
                    return False
            else:
                print("\n⚠️ Информация о scopes в токене недоступна")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка чтения токена: {e}")
            return False
    else:
        print(f"❌ Токен не найден: {token_path}")
        return False
    
    return True


def check_credentials_type():
    """Проверка типа credentials"""
    creds_path = "credentials.json"
    
    if os.path.exists(creds_path):
        try:
            import json
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data:
                print(f"🔐 Тип авторизации: OAuth 2.0 (Desktop Application)")
                return 'oauth2'
            elif 'type' in creds_data and creds_data['type'] == 'service_account':
                print(f"⚙️ Тип авторизации: Service Account")
                return 'service_account'
            else:
                print(f"⚠️ Неизвестный тип credentials")
                return 'unknown'
        except Exception as e:
            print(f"❌ Ошибка чтения credentials.json: {e}")
            return 'error'
    else:
        print(f"❌ credentials.json не найден")
        return 'missing'


def main():
    print("🔧 ДИАГНОСТИКА ПРОБЛЕМЫ 403")
    print("=" * 60)
    
    # Проверяем тип авторизации
    creds_type = check_credentials_type()
    print()
    
    # Проверяем токен и scopes
    token_ok = check_token_scopes()
    print()
    
    # Рекомендации
    print("💡 РЕКОМЕНДАЦИИ:")
    print("=" * 60)
    
    if creds_type == 'oauth2':
        if not token_ok:
            print("1. 🗑️ Удалите старый токен:")
            print("   Remove-Item token.pickle -Force")
            print()
            print("2. 🚀 Запустите приложение заново:")
            print("   python main.py")
            print()
            print("3. 🌐 Пройдите авторизацию в браузере")
            print("4. ✅ Разрешите ВСЕ запрашиваемые права")
        else:
            print("✅ Токен содержит необходимые scopes")
            print("❓ Возможные причины ошибки 403:")
            print("   - Недостаточные права у пользователя Google Workspace")
            print("   - Admin SDK API не включен в Google Cloud Console")
            print("   - Группа заблокирована для изменений")
    
    elif creds_type == 'service_account':
        print("⚙️ Используется Service Account")
        print("📋 Проверьте Domain-wide delegation в Google Admin Console")
        print("🔗 Должны быть авторизованы следующие scopes:")
        for scope in config.google.scopes:
            print(f"   - {scope}")
    
    print("\n📞 Если проблема остается - предоставьте этот вывод для дальнейшей диагностики")


if __name__ == "__main__":
    main()
