#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin Team Tools v2.1.0 - Google Workspace Management
Приоритет: OAuth 2.0 авторизация для безопасного интерактивного управления
"""

import sys
import os
import asyncio
import tracemalloc
from pathlib import Path

# Включаем tracemalloc для отладки
tracemalloc.start()

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.application import Application
from src.utils.enhanced_logger import setup_logging
from src.config.enhanced_config import config


def show_startup_banner():
    """Показывает стартовый баннер с информацией об OAuth 2.0"""
    print("=" * 70)
    print("🚀 ADMIN TEAM TOOLS v2.1.0")
    print("📊 Google Workspace Management System")
    print("=" * 70)
    print("🔐 Приоритет авторизации: OAuth 2.0 (интерактивная)")
    print("🔧 Запасной метод: Service Account (автоматический)")
    print()
    
    # Проверяем наличие credentials
    credentials_path = Path("credentials.json")
    if credentials_path.exists():
        try:
            import json
            with open(credentials_path, 'r') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data:
                print("✅ OAuth 2.0 credentials обнаружены")
                print("🌐 При первом запуске откроется браузер для авторизации")
            elif 'type' in creds_data and creds_data['type'] == 'service_account':
                print("⚙️ Service Account credentials обнаружены")
                print("🤖 Будет использована автоматическая авторизация")
            else:
                print("⚠️  Неизвестный формат credentials.json")
        except Exception:
            print("⚠️  Ошибка чтения credentials.json")
    else:
        print("❌ credentials.json не найден")
        print("📋 Для настройки см.: docs/OAUTH2_PRIORITY_SETUP.md")
    
    print("=" * 70)
    print()


async def main() -> int:
    """
    Главная функция приложения
    
    Returns:
        Код выхода
    """
    try:
        # Создаем и запускаем приложение
        app = Application()
        return await app.start()
        
    except KeyboardInterrupt:
        print("\\n⏹️ Приложение остановлено пользователем")
        return 0
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return 1


def cli_main():
    """Синхронная точка входа для приложения"""
    try:
        # Показываем стартовый баннер
        show_startup_banner()
        
        # Настройка обработки исключений Tkinter
        import tkinter as tk
        def handle_tkinter_error(exc, val, tb):
            if isinstance(val, tk.TclError) and "invalid command name" in str(val):
                # Игнорируем ошибки закрытых виджетов
                return
            # Для других ошибок выводим стандартное сообщение
            sys.__excepthook__(exc, val, tb)
        
        sys.excepthook = handle_tkinter_error
        
        # Запуск приложения (всегда в GUI режиме)
        return asyncio.run(main())
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return 1


if __name__ == "__main__":
    exit_code = cli_main()
    sys.exit(exit_code)
