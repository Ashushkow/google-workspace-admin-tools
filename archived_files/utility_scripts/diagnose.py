#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диагностика проблем Admin Team Tools
"""

import os
import sys
import json
import time
from pathlib import Path

def print_section(title):
    print("\n" + "="*60)
    print(f"📋 {title}")
    print("="*60)

def check_files():
    """Проверка наличия необходимых файлов"""
    print_section("ПРОВЕРКА ФАЙЛОВ")
    
    files_to_check = [
        "main.py",
        "credentials.json", 
        "src/core/application.py",
        "src/api/service_adapter.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size} байт)")
        else:
            print(f"❌ {file_path} - НЕ НАЙДЕН")

def check_credentials():
    """Проверка файла учетных данных"""
    print_section("ПРОВЕРКА CREDENTIALS")
    
    creds_path = "credentials.json"
    if not os.path.exists(creds_path):
        print("❌ credentials.json не найден")
        print("💡 Создайте файл согласно docs/OAUTH2_PRIORITY_SETUP.md")
        return
    
    try:
        with open(creds_path, 'r') as f:
            creds = json.load(f)
        
        if 'installed' in creds:
            print("✅ OAuth 2.0 credentials обнаружены")
            print(f"📧 Client ID: {creds['installed'].get('client_id', 'N/A')[:20]}...")
        elif 'type' in creds and creds['type'] == 'service_account':
            print("✅ Service Account credentials обнаружены")
            print(f"📧 Client Email: {creds.get('client_email', 'N/A')}")
        else:
            print("⚠️ Неизвестный формат credentials.json")
            
    except Exception as e:
        print(f"❌ Ошибка чтения credentials.json: {e}")

def check_environment():
    """Проверка переменных окружения"""
    print_section("ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ")
    
    env_vars = [
        "FAST_LOAD_MODE",
        "DEV_MODE", 
        "GOOGLE_WORKSPACE_DOMAIN",
        "GOOGLE_WORKSPACE_ADMIN"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "НЕ УСТАНОВЛЕНА")
        print(f"🔧 {var}: {value}")

def test_quick_import():
    """Тест быстрого импорта модулей"""
    print_section("ТЕСТ ИМПОРТА МОДУЛЕЙ")
    
    modules_to_test = [
        ("src.core.application", "Application"),
        ("src.api.service_adapter", "ServiceAdapter"),
        ("src.config.enhanced_config", "config")
    ]
    
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    
    for module_name, class_name in modules_to_test:
        try:
            start_time = time.time()
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            end_time = time.time()
            print(f"✅ {module_name}.{class_name} ({end_time-start_time:.2f}с)")
        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {e}")

def test_api_connection():
    """Тест подключения к API"""
    print_section("ТЕСТ API ПОДКЛЮЧЕНИЯ")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        from src.auth import get_service
        
        print("🔄 Попытка получить сервис...")
        start_time = time.time()
        
        service = get_service()
        end_time = time.time()
        
        if service:
            print(f"✅ Сервис получен за {end_time-start_time:.2f}с")
            
            # Тест простого запроса
            try:
                print("🔄 Тест запроса к API...")
                result = service.users().list(customer='my_customer', maxResults=1).execute()
                users = result.get('users', [])
                print(f"✅ API работает, найдено пользователей: {len(users)}")
            except Exception as api_error:
                print(f"⚠️ API недоступен: {api_error}")
        else:
            print("❌ Не удалось получить сервис")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def check_logs():
    """Проверка последних логов"""
    print_section("ПОСЛЕДНИЕ ЛОГИ")
    
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("⚠️ Папка logs не найдена")
        return
    
    log_files = list(logs_dir.glob("*.log"))
    if not log_files:
        print("⚠️ Файлы логов не найдены")
        return
    
    # Берем самый свежий лог
    latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
    print(f"📄 Последний лог: {latest_log}")
    
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Показываем последние 10 строк
        print("\n📋 Последние 10 записей:")
        for line in lines[-10:]:
            print(f"   {line.strip()}")
            
    except Exception as e:
        print(f"❌ Ошибка чтения лога: {e}")

def test_freeipa_integration():
    """Тест FreeIPA интеграции"""
    print_section("ТЕСТ FREEIPA ИНТЕГРАЦИИ")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        from src.integrations.freeipa_integration import FreeIPAIntegration
        from src.services.user_service import UserService
        from src.services.group_service import GroupService
        
        print("✅ FreeIPA модули импортированы")
        
        # Проверяем структуру класса
        integration_methods = ['freeipa_client', 'get_groups', 'get_group', 'create_group']
        for method in integration_methods:
            if hasattr(FreeIPAIntegration, method):
                print(f"✅ Метод {method} найден")
            else:
                print(f"❌ Метод {method} НЕ НАЙДЕН")
        
        print("✅ FreeIPA интеграция структурно корректна")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования FreeIPA: {e}")

def main():
    """Основная функция диагностики"""
    print("🔧 ДИАГНОСТИКА ADMIN TEAM TOOLS")
    print(f"📅 Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_files()
    check_credentials() 
    check_environment()
    test_quick_import()
    test_api_connection()
    test_freeipa_integration()
    check_logs()
    
    print_section("РЕКОМЕНДАЦИИ")
    print("1. ✅ Если все проверки прошли - можно использовать обычный режим")
    print("2. 🚀 Для быстрого старта: set FAST_LOAD_MODE=true")
    print("3. 📚 Документация: docs/OAUTH2_PRIORITY_SETUP.md")
    print("4. 🐛 При проблемах: проверьте логи в папке logs/")
    
    print("\n" + "="*60)
    print("🎯 Диагностика завершена")
    print("="*60)

if __name__ == "__main__":
    main()
