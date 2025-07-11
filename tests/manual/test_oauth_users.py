#!/usr/bin/env python3
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path

# Добавляем корневую папку в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pickle
import json

# Необходимые области доступа
SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.orgunit',
]

def get_credentials():
    """Получение и обновление OAuth 2.0 credentials"""
    creds = None
    token_path = Path("token.pickle")
    credentials_path = Path("credentials.json")

    # Проверяем существующий токен
    if token_path.exists():
        print("🔍 Найден существующий токен, пробуем использовать его...")
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # Если нет валидного токена, получаем новый
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Обновляем просроченный токен...")
            creds.refresh(Request())
        else:
            print("🔐 Запускаем процесс OAuth 2.0 авторизации...")
            if not credentials_path.exists():
                raise FileNotFoundError("❌ Файл credentials.json не найден!")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Сохраняем токен для следующего запуска
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            print("💾 Токен сохранен для последующих запусков")

    return creds

def main():
    """Основная функция теста"""
    print("=" * 70)
    print("🔍 ТЕСТ ПОДКЛЮЧЕНИЯ OAUTH 2.0 К GOOGLE WORKSPACE")
    print("=" * 70)

    try:
        # Проверяем credentials.json
        credentials_path = Path("credentials.json")
        if credentials_path.exists():
            with open(credentials_path, 'r') as f:
                creds_data = json.load(f)
                if 'installed' not in creds_data:
                    print("❌ credentials.json не является OAuth 2.0 Desktop типом!")
                    print("📋 Скачайте правильный credentials.json из Google Cloud Console")
                    return 1
        else:
            print("❌ Файл credentials.json не найден!")
            return 1

        # Получаем credentials
        creds = get_credentials()
        print("✅ Успешно получили credentials")

        # Создаем сервис Directory API
        print("🌐 Создаем сервис Directory API...")
        service = build('admin', 'directory_v1', credentials=creds)
        
        # Пробуем получить список пользователей
        print("👥 Запрашиваем список пользователей...")
        results = service.users().list(
            customer='my_customer',
            maxResults=10,
            orderBy='email'
        ).execute()
        users = results.get('users', [])

        if not users:
            print("⚠️ Пользователи не найдены. Возможные причины:")
            print("1. У вашего аккаунта нет прав администратора Workspace")
            print("2. В домене нет пользователей")
            print("3. Неправильно настроен OAuth consent screen")
        else:
            print(f"✅ Успешно получили {len(users)} пользователей:")
            for user in users:
                print(f"  📧 {user['primaryEmail']} ({user['name']['fullName']})")

        print("\n✅ Тест завершен успешно!")
        return 0

    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        print("\n🔍 Рекомендации:")
        print("1. Проверьте, что вы используете OAuth 2.0 Desktop credentials")
        print("2. Убедитесь, что у вас есть права администратора Workspace")
        print("3. Проверьте настройки OAuth consent screen")
        return 1

if __name__ == '__main__':
    exit(main())
