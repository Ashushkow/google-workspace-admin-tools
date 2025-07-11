#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивный конфигуратор для настройки реальных пользователей Google Workspace
"""

import os
import sys
from pathlib import Path

def interactive_setup():
    """Интерактивная настройка для получения реальных пользователей"""
    print("=" * 70)
    print("⚙️  НАСТРОЙКА GOOGLE WORKSPACE ДЛЯ РЕАЛЬНЫХ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 70)
    print()
    
    print("Для получения реальных пользователей нужно настроить:")
    print("1. Реальный домен Google Workspace")
    print("2. Email администратора домена")
    print("3. Правильные OAuth 2.0 credentials")
    print()
    
    # Вариант 1: Быстрая настройка с реальным доменом
    print("ВАРИАНТ 1: Настройка для реального Google Workspace домена")
    print("-" * 50)
    domain = input("Введите ваш домен Google Workspace (например, mycompany.com): ").strip()
    
    if domain and domain not in ['testdomain.com', 'example.com', 'yourdomain.com']:
        admin_email = input(f"Введите email администратора (например, admin@{domain}): ").strip()
        
        if admin_email and '@' in admin_email:
            print()
            print("✅ Применяем настройки...")
            
            # Обновляем .env файл
            env_content = f"""# Configuration for Admin Team Tools - REAL GOOGLE WORKSPACE
# НЕ ДОБАВЛЯЙТЕ ЭТОТ ФАЙЛ В GIT!

# === Google Workspace Configuration ===
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
GOOGLE_WORKSPACE_DOMAIN={domain}
GOOGLE_WORKSPACE_ADMIN={admin_email}

# === Application Configuration ===
APP_NAME=Admin Team Tools
APP_VERSION=2.0.7
APP_DEBUG=False
APP_LOG_LEVEL=INFO
CLI_MODE=False

# === Database Configuration ===
DATABASE_URL=sqlite:///data/admin_tools.db
CACHE_TTL=300

# === Security Configuration ===
SECRET_KEY=dev-secret-key-change-me
ENCRYPTION_KEY=dev-encryption-key-change-me

# === API Configuration ===
API_RATE_LIMIT=100
API_TIMEOUT=30
API_RETRY_COUNT=3

# === UI Configuration ===
UI_THEME=light
UI_LANGUAGE=ru
UI_WINDOW_SIZE=1200x800

# === Logging Configuration ===
LOG_FILE=logs/admin_tools.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# === Development Configuration ===
DEV_MODE=False
DEBUG_SQL=False
PROFILING_ENABLED=False
"""
            
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            print(f"✅ Настройки сохранены:")
            print(f"   Домен: {domain}")
            print(f"   Админ: {admin_email}")
            print(f"   Режим разработки: отключен")
            print()
            
            print("🔐 СЛЕДУЮЩИЕ ШАГИ:")
            print("1. Убедитесь что credentials.json настроен для вашего домена")
            print("2. Проверьте права администратора в Google Workspace")
            print("3. Настройте OAuth consent screen в Google Cloud Console")
            print("4. Запустите проверку: python check_real_users.py")
            print()
            return True
        else:
            print("❌ Неверный формат email администратора")
    else:
        print("❌ Неверный домен")
    
    print()
    print("ВАРИАНТ 2: Тестирование с демо-данными")
    print("-" * 50)
    demo = input("Хотите продолжить с демо-данными? (y/n): ").strip().lower()
    
    if demo in ['y', 'yes', 'да']:
        # Включаем режим разработки
        env_content = """# Development configuration for Admin Team Tools
# НЕ ДОБАВЛЯЙТЕ ЭТОТ ФАЙЛ В GIT!

# === Google Workspace Configuration ===
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
GOOGLE_WORKSPACE_DOMAIN=testdomain.com
GOOGLE_WORKSPACE_ADMIN=admin@testdomain.com

# === Application Configuration ===
APP_NAME=Admin Team Tools
APP_VERSION=2.0.7
APP_DEBUG=True
APP_LOG_LEVEL=DEBUG
CLI_MODE=False

# === Database Configuration ===
DATABASE_URL=sqlite:///data/admin_tools.db
CACHE_TTL=300

# === Security Configuration ===
SECRET_KEY=dev-secret-key-change-me
ENCRYPTION_KEY=dev-encryption-key-change-me

# === API Configuration ===
API_RATE_LIMIT=100
API_TIMEOUT=30
API_RETRY_COUNT=3

# === UI Configuration ===
UI_THEME=light
UI_LANGUAGE=ru
UI_WINDOW_SIZE=1200x800

# === Logging Configuration ===
LOG_FILE=logs/admin_tools.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# === Development Configuration ===
DEV_MODE=True
DEBUG_SQL=False
PROFILING_ENABLED=False
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Настроен режим демо-данных")
        print("   Будут показаны тестовые пользователи")
        print("   Для реальных пользователей запустите настройку снова")
        return True
    
    return False

def main():
    """Главная функция"""
    print("🚀 Конфигуратор Admin Team Tools")
    print()
    
    if interactive_setup():
        print()
        print("=" * 70)
        print("🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
        print()
        print("Следующие команды:")
        print("1. python check_real_users.py  # Проверить настройки")
        print("2. python main.py              # Запустить приложение")
        print("=" * 70)
    else:
        print()
        print("❌ Настройка не завершена")

if __name__ == "__main__":
    main()
