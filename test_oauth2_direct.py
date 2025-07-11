#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Прямой тест OAuth 2.0 Google API без переменных окружения.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_oauth2_direct():
    """Прямое тестирование OAuth 2.0 без режима разработки"""
    print("=" * 70)
    print("🔑 ПРЯМОЙ ТЕСТ OAUTH 2.0 GOOGLE WORKSPACE API")
    print("=" * 70)
    
    try:
        # Импортируем Google API напрямую
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        import pickle
        import json
        
        # Определяем scopes
        SCOPES = [
            'https://www.googleapis.com/auth/admin.directory.user',
            'https://www.googleapis.com/auth/admin.directory.group',
            'https://www.googleapis.com/auth/admin.directory.orgunit',
        ]
        
        credentials_file = Path("credentials.json")
        token_file = Path("token.pickle")
        
        # Проверяем файлы
        if not credentials_file.exists():
            print("❌ credentials.json не найден")
            return False
        
        # Читаем credentials
        with open(credentials_file, 'r') as f:
            creds_data = json.load(f)
        
        if 'installed' not in creds_data:
            print("❌ Неверный формат credentials.json - требуется OAuth 2.0 Desktop Application")
            return False
        
        print("✅ OAuth 2.0 credentials найдены")
        print(f"   Client ID: {creds_data['installed']['client_id']}")
        
        credentials = None
        
        # Загружаем существующий токен
        if token_file.exists():
            print("📁 Загружаем сохраненный токен...")
            try:
                with open(token_file, 'rb') as token:
                    credentials = pickle.load(token)
                print("✅ Токен загружен")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки токена: {e}")
                credentials = None
        
        # Проверяем валидность токена
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print("🔄 Обновляем истекший токен...")
                try:
                    credentials.refresh(Request())
                    print("✅ Токен обновлен")
                except Exception as e:
                    print(f"⚠️ Ошибка обновления токена: {e}")
                    credentials = None
            
            if not credentials or not credentials.valid:
                print("🌐 Запускаем новую авторизацию...")
                print("ВНИМАНИЕ: Сейчас откроется браузер для авторизации Google Workspace")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                credentials = flow.run_local_server(
                    port=0,
                    prompt='select_account'
                )
                print("✅ Авторизация завершена")
                
                # Сохраняем токен
                with open(token_file, 'wb') as token:
                    pickle.dump(credentials, token)
                print("💾 Токен сохранен")
        
        # Создаем сервис
        print("🔧 Создаем подключение к Google Admin SDK...")
        service = build('admin', 'directory_v1', credentials=credentials)
        
        # Тестируем подключение
        print("🔍 Тестируем подключение...")
        domains_result = service.domains().list(customer='my_customer').execute()
        domains = domains_result.get('domains', [])
        
        if domains:
            print(f"✅ Подключение успешно! Найдено доменов: {len(domains)}")
            for domain in domains:
                print(f"   • {domain['domainName']} ({'Основной' if domain.get('isPrimary') else 'Дополнительный'})")
        else:
            print("⚠️ Домены не найдены")
        
        # Загружаем пользователей
        print("👥 Загружаем пользователей...")
        users_result = service.users().list(
            customer='my_customer',
            maxResults=10,
            orderBy='email'
        ).execute()
        
        users = users_result.get('users', [])
        
        if users:
            print(f"✅ Найдено пользователей: {len(users)}")
            for i, user in enumerate(users[:5]):
                email = user.get('primaryEmail', 'N/A')
                name = user.get('name', {}).get('fullName', 'N/A')
                suspended = user.get('suspended', False)
                org_unit = user.get('orgUnitPath', '/')
                
                status = "🔴 ЗАБЛОКИРОВАН" if suspended else "🟢 АКТИВЕН"
                print(f"   {i+1}. {email}")
                print(f"      Имя: {name}")
                print(f"      Статус: {status}")
                print(f"      Подразделение: {org_unit}")
                print()
            
            if len(users) > 5:
                print(f"   ... и еще {len(users) - 5} пользователей")
                
            print("=" * 70)
            print("🎉 ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
            print("✅ OAuth 2.0 авторизация работает")
            print("✅ Загрузка пользователей работает")
            print("=" * 70)
            return True
            
        else:
            print("❌ Пользователи не найдены")
            print("💡 Возможные причины:")
            print("   • Нет пользователей в Google Workspace")
            print("   • Недостаточно прав у аккаунта")
            print("   • Неправильные scopes")
            return False
        
    except HttpError as e:
        print(f"❌ HTTP ошибка Google API: {e}")
        if e.resp.status == 403:
            print("💡 Ошибка 403 - проверьте права администратора")
        elif e.resp.status == 401:
            print("💡 Ошибка 401 - проблема с авторизацией")
        return False
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_oauth2_direct()
        if success:
            print("\n🎯 OAuth 2.0 настроен корректно!")
        else:
            print("\n❌ Проблемы с OAuth 2.0")
    except KeyboardInterrupt:
        print("\n⏹️ Тест прерван пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
