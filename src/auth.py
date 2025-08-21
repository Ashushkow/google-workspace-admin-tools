# -*- coding: utf-8 -*-
"""
Авторизация и работа с Google Directory API.
"""

import os
import pickle
import json
from typing import Any
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from .config.enhanced_config import config, get_domain_admin_email

# Константы для обратной совместимости
SCOPES = config.google.scopes
CREDENTIALS_FILE = config.google.credentials_file
TOKEN_PICKLE = config.google.token_file


def detect_credentials_type() -> str:
    """
    Определяет тип файла credentials.json
    
    Returns:
        'service_account' или 'oauth2'
    """
    try:
        with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            creds_data = json.load(f)
            
        return 'service_account' if creds_data.get('type') == 'service_account' else 'oauth2' if 'installed' in creds_data else (_ for _ in ()).throw(ValueError("Неизвестный формат credentials.json"))
            
    except Exception as e:
        raise ValueError(f"Ошибка чтения credentials.json: {e}")


def get_service_account_credentials():
    """Получение credentials для Service Account с Domain-wide delegation"""
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, 
        scopes=SCOPES
    )
    
    # Получаем актуальный email администратора
    domain_admin_email = get_domain_admin_email()
    
    # Делегирование полномочий администратору домена
    if domain_admin_email and domain_admin_email != 'admin@yourdomain.com':
        creds = creds.with_subject(domain_admin_email)
        print(f"✅ Используем Service Account с делегированием для {domain_admin_email}")
    else:
        print("⚠️ ВНИМАНИЕ: Service Account настроен с значениями по умолчанию!")
        print("⚠️ Для корректной работы необходимо настроить email администратора через мастер настройки.")
        # НЕ выбрасываем исключение, а возвращаем credentials как есть
        # Пусть Google API сам выдаст правильную ошибку
    
    return creds


def get_oauth2_credentials():
    """Получение credentials для OAuth 2.0"""
    creds = None
    token_path = TOKEN_PICKLE
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    # Загружаем существующий токен если есть
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # Проверяем валидность токена
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Обновляем истёкший токен
            try:
                print("🔄 Обновление токена авторизации...")
                creds.refresh(Request())
            except Exception as e:
                print(f"❌ Ошибка обновления токена: {e}")
                creds = None
        
        if not creds:
            # Инициируем новую авторизацию
            try:
                print("🌐 Запуск OAuth 2.0 авторизации...")
                print("⏰ Браузер должен открыться автоматически в течение 10 секунд")
                print("📋 Если браузер не открылся, используйте URL из консоли")
                
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                
                # Запускаем локальный сервер с таймаутом
                import threading
                import time
                
                auth_result = [None]  # Используем список для передачи результата
                auth_error = [None]
                
                def run_auth():
                    try:
                        auth_result[0] = flow.run_local_server(port=0, timeout_seconds=30)
                    except Exception as e:
                        auth_error[0] = e
                
                # Запускаем авторизацию в отдельном потоке
                auth_thread = threading.Thread(target=run_auth)
                auth_thread.daemon = True
                auth_thread.start()
                
                # Ждем результат с таймаутом
                auth_thread.join(timeout=35)
                
                if auth_thread.is_alive():
                    print("⏰ Таймаут авторизации (35 сек). Процесс будет остановлен.")
                    raise TimeoutError("OAuth 2.0 авторизация заняла слишком много времени")
                
                if auth_error[0]:
                    raise auth_error[0]
                
                if auth_result[0]:
                    creds = auth_result[0]
                    print("✅ OAuth 2.0 авторизация успешна!")
                else:
                    raise Exception("Не удалось получить credentials")
                    
            except Exception as e:
                print(f"❌ Ошибка OAuth 2.0 авторизации: {e}")
                print("💡 Попробуйте использовать Service Account credentials")
                print("📋 Или проверьте настройки OAuth 2.0 в Google Cloud Console")
                raise
        
        # Сохраняем токен для будущего использования
        if creds:
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
    
    return creds


def get_service() -> Any:
    """
    Получение авторизованного сервиса Google Directory API.
    
    Автоматически определяет тип credentials (Service Account или OAuth 2.0)
    и использует соответствующий метод аутентификации.
    
    Returns:
        Авторизованный сервис Google Directory API
        
    Raises:
        FileNotFoundError: Если файл credentials.json не найден
        ValueError: Если формат credentials.json неверный
        ConfigurationError: Если конфигурация не настроена
    """
    # Проверяем базовую конфигурацию
    if not _is_configuration_valid():
        # Не блокируем полностью - позволяем GUI запуститься для настройки
        print("⚠️ Конфигурация не настроена полностью")
        print("💡 Используйте GUI мастер настройки для завершения конфигурации")
        
        # Если переменная окружения установлена, то не блокируем
        if os.getenv('ALLOW_INCOMPLETE_CONFIG', 'False').lower() == 'true':
            print("🔄 Разрешен запуск с неполной конфигурацией")
        else:
            raise ValueError(
                "Конфигурация не настроена! Запустите приложение и используйте GUI мастер настройки."
            )
    
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"Файл {CREDENTIALS_FILE} не найден.")
    
    # Определяем тип credentials
    creds_type = detect_credentials_type()
    
    if creds_type == 'service_account':
        # Используем Service Account
        creds = get_service_account_credentials()
    elif creds_type == 'oauth2':
        # Используем OAuth 2.0
        creds = get_oauth2_credentials()
    else:
        raise ValueError(f"Неподдерживаемый тип credentials: {creds_type}")
    
    return build('admin', 'directory_v1', credentials=creds)


def _is_configuration_valid() -> bool:
    """Проверяет, настроена ли конфигурация должным образом"""
    try:
        # Проверяем основные настройки
        if config.settings.google_workspace_domain == "yourdomain.com":
            print("❌ Домен не настроен (значение по умолчанию: yourdomain.com)")
            return False
            
        if config.settings.google_workspace_admin == "admin@yourdomain.com":
            print("❌ Администратор не настроен (значение по умолчанию: admin@yourdomain.com)")
            return False
            
        print(f"✅ Конфигурация выглядит корректно: {config.settings.google_workspace_domain}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки конфигурации: {e}")
        return False
