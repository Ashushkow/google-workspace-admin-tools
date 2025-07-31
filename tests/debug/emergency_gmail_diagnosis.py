#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Экстренная диагностика проблемы с Gmail API.
"""

import sys
import os
import pickle
import json
from pathlib import Path

# Добавляем src в Python path  
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def emergency_gmail_diagnosis():
    """Экстренная диагностика Gmail API"""
    print("🚨 ЭКСТРЕННАЯ ДИАГНОСТИКА GMAIL API")
    print("=" * 60)
    print("Анализируем почему Gmail API всё ещё не работает\n")
    
    # 1. Проверяем credentials.json
    print("1️⃣ ПРОВЕРКА CREDENTIALS.JSON")
    print("-" * 40)
    
    creds_path = Path("credentials.json")
    if not creds_path.exists():
        print("❌ credentials.json не найден!")
        return
    
    try:
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        if 'installed' in creds_data:
            client_id = creds_data['installed'].get('client_id', 'N/A')
            project_id = creds_data['installed'].get('project_id', 'N/A')
            print(f"✅ OAuth 2.0 Client ID найден")
            print(f"📋 Client ID: {client_id}")
            print(f"📋 Project ID: {project_id}")
        else:
            print("❌ Неверный формат credentials.json")
            return
    except Exception as e:
        print(f"❌ Ошибка чтения credentials: {e}")
        return
    
    # 2. Проверяем токен
    print(f"\n2️⃣ АНАЛИЗ ТОКЕНА")
    print("-" * 40)
    
    token_path = Path("token.pickle")
    if not token_path.exists():
        print("❌ token.pickle не найден - нужна авторизация")
        return
    
    try:
        with open(token_path, 'rb') as f:
            creds = pickle.load(f)
        
        print(f"✅ Токен загружен")
        print(f"📊 Валидный: {creds.valid}")
        print(f"⏰ Истекший: {creds.expired}")
        
        if hasattr(creds, 'scopes') and creds.scopes:
            print(f"📋 Scopes в токене ({len(creds.scopes)}):")
            gmail_found = False
            for scope in creds.scopes:
                is_gmail = " ← GMAIL!" if 'gmail' in scope else ""
                if 'gmail' in scope:
                    gmail_found = True
                print(f"   • {scope}{is_gmail}")
            
            if gmail_found:
                print(f"✅ Gmail scope найден в токене")
            else:
                print(f"❌ Gmail scope НЕ найден в токене")
        
    except Exception as e:
        print(f"❌ Ошибка анализа токена: {e}")
        return
    
    # 3. Прямое тестирование Gmail API
    print(f"\n3️⃣ ПРЯМОЕ ТЕСТИРОВАНИЕ GMAIL API")
    print("-" * 40)
    
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        # Создаем Gmail сервис
        gmail_service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail сервис создан")
        
        # Пробуем разные методы
        test_methods = [
            ("Профиль пользователя", lambda: gmail_service.users().getProfile(userId='me').execute()),
            ("Список ярлыков", lambda: gmail_service.users().labels().list(userId='me').execute()),
            ("Список черновиков", lambda: gmail_service.users().drafts().list(userId='me').execute()),
        ]
        
        for name, method in test_methods:
            try:
                result = method()
                print(f"✅ {name}: Успешно")
                if name == "Профиль пользователя":
                    print(f"   📧 Email: {result.get('emailAddress', 'N/A')}")
                elif name == "Список ярлыков":
                    print(f"   📋 Ярлыков: {len(result.get('labels', []))}")
                break  # Если хотя бы один метод работает - API доступен
            except HttpError as e:
                print(f"❌ {name}: {e}")
                if "insufficient" in str(e).lower():
                    print(f"   🔍 Проблема: Gmail scope не добавлен в OAuth Consent Screen!")
            except Exception as e:
                print(f"❌ {name}: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка создания Gmail сервиса: {e}")
    
    # 4. Показываем критическую инструкцию
    print(f"\n4️⃣ КРИТИЧЕСКАЯ ИНСТРУКЦИЯ")
    print("-" * 40)
    print("🎯 ПРОБЛЕМА: Gmail scope есть в токене, но НЕ в OAuth Consent Screen")
    print("")
    print("📋 РЕШЕНИЕ (выполните ТОЧНО в таком порядке):")
    print("")
    print("1. 🌐 Откройте console.cloud.google.com")
    print("2. 📂 Выберите проект с этим Client ID:")
    print(f"   {client_id}")
    print("3. 🔧 APIs & Services → OAuth consent screen")
    print("4. ✏️ EDIT APP")
    print("5. 📋 Перейдите к шагу 'Scopes'")
    print("6. ➕ ADD OR REMOVE SCOPES")
    print("7. 🔍 Найдите 'Gmail API'")
    print("8. ✅ Отметьте: '../auth/gmail.send - Send email on your behalf'")
    print("9. 💾 UPDATE")
    print("10. ✅ SAVE AND CONTINUE до конца")
    print("")
    print("11. 🗑️ Удалите токен: rm token.pickle")
    print("12. 🔄 Запустите: python main.py")
    print("13. ✅ Проверьте: python setup_gmail_api.py")
    
    # 5. Альтернативные решения
    print(f"\n5️⃣ АЛЬТЕРНАТИВНЫЕ РЕШЕНИЯ")
    print("-" * 40)
    print("Если проблема сохраняется:")
    print("")
    print("🔄 Вариант 1: Новый OAuth Client ID")
    print("   1. Создайте новый OAuth 2.0 Client ID")
    print("   2. Сразу добавьте Gmail scope в OAuth consent screen")
    print("   3. Скачайте новый credentials.json")
    print("   4. Удалите token.pickle")
    print("   5. Запустите приложение")
    print("")
    print("🔄 Вариант 2: Проверьте ограничения домена")
    print("   1. Google Workspace Admin Console")
    print("   2. Security → API controls")
    print("   3. Убедитесь, что Gmail API разрешен")
    print("")
    print("🔄 Вариант 3: Используйте другой Google аккаунт")
    print("   1. Попробуйте аккаунт супер-администратора")
    print("   2. Убедитесь в правах на отправку писем")


def main():
    """Главная функция экстренной диагностики"""
    emergency_gmail_diagnosis()


if __name__ == "__main__":
    main()
