#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка и обновление scopes для OAuth 2.0.
"""

import os
import sys
import json
import pickle
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def check_token_scopes():
    """Проверяем scopes в существующем токене"""
    print("=" * 60)
    print("🔍 ПРОВЕРКА SCOPES В ТОКЕНЕ")
    print("=" * 60)
    
    token_file = Path("token.pickle")
    
    if not token_file.exists():
        print("❌ token.pickle не найден")
        return False
    
    try:
        with open(token_file, 'rb') as f:
            credentials = pickle.load(f)
        
        print("✅ Токен загружен")
        
        if hasattr(credentials, 'scopes'):
            print("📋 Scopes в токене:")
            for scope in credentials.scopes:
                print(f"   • {scope}")
        else:
            print("⚠️ Информация о scopes недоступна")
        
        print(f"📊 Валидность токена: {credentials.valid}")
        print(f"📊 Истек ли токен: {credentials.expired}")
        
        if hasattr(credentials, 'token'):
            print(f"📊 Токен присутствует: {'Да' if credentials.token else 'Нет'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка чтения токена: {e}")
        return False

def regenerate_token_with_admin_scopes():
    """Пересоздаем токен с правильными scopes для Google Workspace Admin"""
    print("\n" + "=" * 60)
    print("🔄 ПЕРЕСОЗДАНИЕ ТОКЕНА С ADMIN SCOPES")
    print("=" * 60)
    
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle
        
        # Расширенные scopes для Google Workspace Admin
        ADMIN_SCOPES = [
            'https://www.googleapis.com/auth/admin.directory.user',
            'https://www.googleapis.com/auth/admin.directory.group',
            'https://www.googleapis.com/auth/admin.directory.orgunit',
            'https://www.googleapis.com/auth/admin.directory.domain',
            'https://www.googleapis.com/auth/admin.directory.customer',
            'https://www.googleapis.com/auth/calendar',
        ]
        
        credentials_file = Path("credentials.json")
        token_file = Path("token.pickle")
        
        if not credentials_file.exists():
            print("❌ credentials.json не найден")
            return False
        
        print("📋 Новые scopes для авторизации:")
        for scope in ADMIN_SCOPES:
            print(f"   • {scope}")
        
        print("\n⚠️  ВНИМАНИЕ!")
        print("Для корректной работы требуется аккаунт с правами администратора Google Workspace")
        print("Убедитесь, что вы авторизуетесь под аккаунтом администратора!")
        
        response = input("\nПродолжить пересоздание токена? (y/N): ")
        if response.lower() != 'y':
            print("❌ Отменено пользователем")
            return False
        
        # Удаляем старый токен
        if token_file.exists():
            token_file.unlink()
            print("🗑️ Старый токен удален")
        
        # Создаем новый поток авторизации
        print("🌐 Запускаем новую авторизацию с расширенными правами...")
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, ADMIN_SCOPES)
        
        credentials = flow.run_local_server(
            port=0,
            prompt='select_account',
            authorization_prompt_message='🔐 Авторизуйтесь под аккаунтом администратора Google Workspace...',
            success_message='✅ Авторизация завершена! Проверяем права...'
        )
        
        # Сохраняем новый токен
        with open(token_file, 'wb') as token:
            pickle.dump(credentials, token)
        
        print("✅ Новый токен сохранен с расширенными правами")
        
        # Проверяем новый токен
        print("\n🔍 Проверяем новый токен...")
        if hasattr(credentials, 'scopes'):
            print("📋 Scopes в новом токене:")
            for scope in credentials.scopes:
                print(f"   • {scope}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка пересоздания токена: {e}")
        return False

def test_admin_permissions():
    """Тестируем права администратора"""
    print("\n" + "=" * 60)
    print("🔍 ТЕСТИРОВАНИЕ ПРАВ АДМИНИСТРАТОРА")
    print("=" * 60)
    
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        import pickle
        
        token_file = Path("token.pickle")
        
        if not token_file.exists():
            print("❌ token.pickle не найден")
            return False
        
        with open(token_file, 'rb') as f:
            credentials = pickle.load(f)
        
        service = build('admin', 'directory_v1', credentials=credentials)
        
        # Тест 1: Получение информации о домене
        print("🔍 Тест 1: Получение доменов...")
        try:
            domains_result = service.domains().list(customer='my_customer').execute()
            domains = domains_result.get('domains', [])
            
            if domains:
                print(f"✅ Найдено доменов: {len(domains)}")
                for domain in domains:
                    print(f"   • {domain['domainName']} ({'Основной' if domain.get('isPrimary') else 'Дополнительный'})")
            else:
                print("⚠️ Домены не найдены")
        except HttpError as e:
            print(f"❌ Ошибка получения доменов: {e}")
            return False
        
        # Тест 2: Получение пользователей
        print("\n🔍 Тест 2: Получение пользователей...")
        try:
            users_result = service.users().list(
                customer='my_customer',
                maxResults=3
            ).execute()
            
            users = users_result.get('users', [])
            
            if users:
                print(f"✅ Найдено пользователей: {len(users)}")
                for user in users:
                    email = user.get('primaryEmail', 'N/A')
                    name = user.get('name', {}).get('fullName', 'N/A')
                    print(f"   • {email} ({name})")
            else:
                print("⚠️ Пользователи не найдены")
        except HttpError as e:
            print(f"❌ Ошибка получения пользователей: {e}")
            return False
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("✅ OAuth 2.0 настроен корректно")
        print("✅ Права администратора подтверждены")
        print("✅ Загрузка пользователей работает")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    try:
        # Проверяем текущий токен
        check_token_scopes()
        
        # Спрашиваем о пересоздании токена
        print("\n" + "=" * 60)
        print("💡 РЕКОМЕНДАЦИЯ")
        print("=" * 60)
        print("Для корректной работы с Google Workspace Admin API")
        print("рекомендуется пересоздать токен с расширенными правами.")
        
        choice = input("\nПересоздать токен? (y/N): ")
        if choice.lower() == 'y':
            success = regenerate_token_with_admin_scopes()
            if success:
                test_admin_permissions()
        else:
            print("Тестирование с существующим токеном...")
            test_admin_permissions()
            
    except KeyboardInterrupt:
        print("\n⏹️ Процесс прерван пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
