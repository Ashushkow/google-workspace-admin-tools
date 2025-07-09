# -*- coding: utf-8 -*-
"""
Конфигурация и константы приложения.
"""

import json
import os
from typing import Dict, Any

# --- Константы для Google API ---
SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.orgunit',
    'https://www.googleapis.com/auth/calendar'
]
CREDENTIALS_FILE = 'credentials.json'
TOKEN_PICKLE = 'token.pickle'
SETTINGS_FILE = 'config/settings.json'

# --- Загрузка настроек из settings.json ---
def load_settings() -> Dict[str, Any]:
    """
    Загружает настройки из файла settings.json.
    
    Returns:
        Словарь с настройками приложения
    """
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки настроек: {e}")
        return {}

# Глобальные настройки
settings = load_settings()
