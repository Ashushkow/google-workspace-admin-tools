# -*- coding: utf-8 -*-
"""
Авторизация и работа с Google Directory API.
"""

import os
import pickle
from typing import Any
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from .config import SCOPES, CREDENTIALS_FILE, TOKEN_PICKLE


def get_service() -> Any:
    """
    Получение авторизованного сервиса Google Directory API.
    
    Использует OAuth 2.0 для аутентификации. При первом запуске откроет
    браузер для авторизации. Последующие запуски будут использовать
    сохранённый токен.
    
    Returns:
        Авторизованный сервис Google Directory API
        
    Raises:
        FileNotFoundError: Если файл credentials.json не найден
    """
    creds = None
    
    # Загружаем существующий токен если есть
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    
    # Проверяем валидность токена
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Обновляем истёкший токен
            try:
                creds.refresh(Request())
            except Exception:
                # Если обновление не удалось, удаляем старый токен
                if os.path.exists(TOKEN_PICKLE):
                    os.remove(TOKEN_PICKLE)
                creds = None
        
        # Если токена нет или он не обновился, запускаем новую авторизацию
        if not creds or not creds.valid:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Файл {CREDENTIALS_FILE} не найден.\n"
                    "Создайте OAuth 2.0 credentials в Google Cloud Console и "
                    "скачайте credentials.json в корневую папку проекта."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Сохраняем токен для будущего использования
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('admin', 'directory_v1', credentials=creds)
