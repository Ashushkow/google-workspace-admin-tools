#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для отображения информационных баннеров, включая информацию
о приоритетности OAuth 2.0 для авторизации.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ..config.enhanced_config import config

logger = logging.getLogger(__name__)


def show_oauth2_priority_banner() -> bool:
    """
    Показывает информационный баннер о приоритете OAuth 2.0
    и проверяет наличие/тип учетных данных.
    
    Returns:
        bool: True если обнаружены OAuth 2.0 credentials
    """
    print("=" * 70)
    print("🚀 ADMIN TEAM TOOLS v2.0.7")
    print("📊 Google Workspace Management System")
    print("=" * 70)
    print("🔐 Приоритет авторизации: OAuth 2.0 (интерактивная)")
    print("🔧 Запасной метод: Service Account (автоматический)")
    print()
    
    # Проверяем наличие credentials
    credentials_path = Path(config.settings.google_application_credentials)
    oauth2_detected = False
    
    if credentials_path.exists():
        try:
            with open(credentials_path, 'r') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data:
                print("✅ OAuth 2.0 credentials обнаружены")
                print("🌐 При первом запуске откроется браузер для авторизации")
                oauth2_detected = True
            elif 'type' in creds_data and creds_data['type'] == 'service_account':
                print("⚙️ Service Account credentials обнаружены")
                print("🤖 Будет использована автоматическая авторизация")
                print("⚠️ Для интерактивной авторизации настройте OAuth 2.0")
            else:
                print("⚠️ Неизвестный формат credentials.json")
        except Exception as e:
            logger.error(f"Ошибка чтения credentials.json: {e}")
            print("⚠️ Ошибка чтения credentials.json")
    else:
        print("❌ credentials.json не найден")
        print("📋 Для настройки OAuth 2.0 см.: docs/OAUTH2_PRIORITY_SETUP.md")
    
    # Проверяем наличие токена
    token_path = Path("token.pickle")
    if token_path.exists() and oauth2_detected:
        print("🔑 Токен OAuth 2.0 найден, будет использован для авторизации")
    
    # Проверяем режим разработки
    if config.settings.dev_mode:
        print("\n⚠️ ВНИМАНИЕ: Приложение работает в режиме разработки (DEV_MODE=True)")
        print("📊 Используются демонстрационные данные вместо реального API")
    
    print("=" * 70)
    print()
    
    return oauth2_detected


def show_oauth2_authorization_info() -> None:
    """Показывает информацию о процессе авторизации OAuth 2.0"""
    print("\n" + "="*60)
    print("🔐 АВТОРИЗАЦИЯ GOOGLE WORKSPACE")
    print("="*60)
    print("1. Сейчас откроется браузер для авторизации.")
    print("2. Войдите в Google аккаунт с правами администратора.")
    print("3. Разрешите доступ приложению к запрошенным ресурсам.")
    print("4. После успешной авторизации вернитесь в это приложение.")
    print("="*60 + "\n")


def show_api_connection_result(success: bool, user_count: int = 0, group_count: int = 0) -> None:
    """
    Показывает результат подключения к API
    
    Args:
        success: Успешно ли подключение
        user_count: Количество пользователей
        group_count: Количество групп
    """
    if success:
        print("\n✅ Подключение к Google API успешно!")
        if user_count > 0:
            print(f"👥 Получено пользователей: {user_count}")
        if group_count > 0:
            print(f"👥 Получено групп: {group_count}")
    else:
        print("\n❌ Не удалось подключиться к Google API")
        print("⚠️ Приложение работает в режиме заглушек")
    
    print()
