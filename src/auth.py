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
from .config.enhanced_config import config

# Константы для обратной совместимости
SCOPES = config.google.scopes
CREDENTIALS_FILE = config.google.credentials_file
TOKEN_PICKLE = config.google.token_file
DOMAIN_ADMIN_EMAIL = config.settings.google_workspace_admin


def detect_credentials_type() -> str:
    """
    Определяет тип файла credentials.json
    
    Returns:
        'service_account' или 'oauth2'
    """
    try:
        with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            creds_data = json.load(f)
            
        if creds_data.get('type') == 'service_account':
            return 'service_account'
        elif 'installed' in creds_data:
            return 'oauth2'
        else:
            raise ValueError("Неизвестный формат credentials.json")
            
    except Exception as e:
        raise ValueError(f"Ошибка чтения credentials.json: {e}")


def get_service_account_credentials():
    """Получение credentials для Service Account с Domain-wide delegation"""
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, 
        scopes=SCOPES
    )
    
    # Делегирование полномочий администратору домена
    if DOMAIN_ADMIN_EMAIL != 'admin@yourdomain.com':
        creds = creds.with_subject(DOMAIN_ADMIN_EMAIL)
    else:
        raise ValueError(
            "Необходимо настроить DOMAIN_ADMIN_EMAIL в src/config.py!\n"
            "Замените 'admin@yourdomain.com' на email администратора вашего домена."
        )
    
    return creds


def get_oauth2_credentials():
    """Получение credentials для OAuth 2.0"""
    creds = None
    
    # Загружаем существующий токен если есть
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    
    # Проверяем валидность токена
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Обновляем истёкший токен
            creds.refresh(Request())
        else:
            # Инициируем новую авторизацию
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Сохраняем токен для будущего использования
        with open(TOKEN_PICKLE, 'wb') as token:
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
    """
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
