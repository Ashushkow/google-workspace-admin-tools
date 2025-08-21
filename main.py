#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin Team Tools v2.2.0 - Google Workspace Management
Приоритет: OAuth 2.0 авторизация для безопасного интерактивного управления
"""

import sys
import os
import asyncio
import tracemalloc
from pathlib import Path

# Настройка кодировки для вывода в консоль
try:
    # Для Windows настраиваем UTF-8 output
    if os.name == 'nt':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
except Exception:
    # Если настройка не удалась, продолжаем без неё
    pass

# Добавляем src в Python path сразу
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Безопасная инициализация конфигурации
try:
    from src.config.enhanced_config import config
    
    print("[*] Проверяем необходимость первоначальной настройки...")
    
    # Проверяем, нужна ли первоначальная настройка
    if config.is_first_run():
        print("[>] Обнаружен первый запуск - показываем мастер настройки")
        
        # Показываем GUI мастер настройки
        from src.config.setup_wizard import run_setup_wizard
        
        setup_result = run_setup_wizard()
        if setup_result is None:
            print("[!] Пользователь отменил настройку")
            # Пользователь отменил настройку
            sys.exit(1)
            
        domain, admin_email = setup_result
        print(f"[+] Получены настройки: {domain}, {admin_email}")
        config.create_initial_config(domain, admin_email)
        print("[+] Настройка завершена, запускаем приложение...")
    else:
        print("[+] Конфигурация найдена, продолжаем запуск...")
        
except Exception as e:
    print(f"[!] ОШИБКА при инициализации конфигурации: {e}")
    import traceback
    traceback.print_exc()
    
    # В случае критической ошибки показываем сообщение через tkinter
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showerror(
            "Ошибка настройки", 
            f"Ошибка инициализации: {e}\n\n"
            f"Для решения проблемы:\n"
            f"1. Создайте файл .env с настройками\n"
            f"2. Или установите переменную SKIP_CONFIG_VALIDATION=True\n\n"
            f"Подробности в файле QUICK_CONFIG_FIX.md"
        )
        root.destroy()
    except:
        # Если и GUI не работает, выводим в консоль
        print(f"[!] Ошибка инициализации конфигурации: {e}")
        print("[i] См. файл QUICK_CONFIG_FIX.md для решения проблемы")
    
    sys.exit(1)

# Включаем tracemalloc только в профилировании/DEV
try:
    if config.settings.profiling_enabled or config.settings.app_debug or os.getenv('DEV_MODE', 'False').lower() == 'true':
        tracemalloc.start()
except Exception:
    # Если настройки недоступны, проверяем только переменные окружения
    if os.getenv('DEV_MODE', 'False').lower() == 'true' or os.getenv('PROFILING_ENABLED', 'False').lower() == 'true':
        tracemalloc.start()

def show_startup_banner():
    """Показывает стартовый баннер с информацией об OAuth 2.0"""
    print("=" * 70)
    print("🚀 ADMIN TEAM TOOLS v2.2.0")
    print("📊 Google Workspace Management System")
    print("=" * 70)
    print("🔐 Приоритет авторизации: OAuth 2.0 (интерактивная)")
    print("🔧 Запасной метод: Service Account (автоматический)")
    print()
    
    # Проверяем наличие credentials
    credentials_path = Path(config.settings.google_application_credentials)
    if credentials_path.exists():
        try:
            import json
            with open(credentials_path, 'r', encoding='utf-8') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data:
                print("[+] OAuth 2.0 credentials обнаружены")
                print("[>] При первом запуске откроется браузер для авторизации")
            elif 'type' in creds_data and creds_data['type'] == 'service_account':
                print("[+] Service Account credentials обнаружены")
                print("[>] Будет использована автоматическая авторизация")
            else:
                print("[!] Неизвестный формат", credentials_path)
        except Exception:
            print("[!] Ошибка чтения", credentials_path)
    else:
        print("[!]", credentials_path, "не найден")
        print("[i] Для настройки см.: docs/OAUTH2_PRIORITY_SETUP.md")
    
    print("=" * 70)
    print()


async def main() -> int:
    """
    Главная функция приложения
    
    Returns:
        Код выхода
    """
    try:
        from src.core.application import Application
        from src.utils.enhanced_logger import setup_logging
        
        # Попытка запуска через новую архитектуру
        try:
            app = Application()
            return await app.start()
        except Exception as app_error:
            print(f"[!] Ошибка новой архитектуры: {app_error}")
            print("[>] Запуск GUI напрямую...")
            
            # Fallback - запуск GUI напрямую
            return await _fallback_gui_start()
            
    except KeyboardInterrupt:
        print("\n[*] Приложение остановлено пользователем")
        return 0
    except Exception as e:
        print(f"[!] Критическая ошибка: {e}")
        return 1

async def _fallback_gui_start() -> int:
    """Запуск GUI напрямую в случае ошибок новой архитектуры"""
    try:
        print("[>] Попытка прямого запуска GUI...")
        
        # Импортируем необходимые модули
        from src.ui.main_window import AdminToolsMainWindow
        from src.api.service_adapter import ServiceAdapter
        from src.services.user_service import UserService
        from src.services.group_service import GroupService
        
        # Создаем минимальные сервисы
        user_service = UserService(None)  # Передаем None как репозиторий
        group_service = GroupService(None)  # Передаем None как репозиторий
        
        # Создаем адаптер
        service_adapter = ServiceAdapter(user_service, group_service)
        
        # Запускаем GUI
        gui_app = AdminToolsMainWindow(service=service_adapter)
        gui_app.mainloop()
        
        return 0
        
    except Exception as fallback_error:
        print(f"[!] Ошибка fallback запуска: {fallback_error}")
        
        # Последняя попытка - старый код без новых сервисов
        try:
            print("[>] Последняя попытка - простой GUI...")
            from src.ui.main_window import AdminToolsMainWindow
            
            gui_app = AdminToolsMainWindow(service=None)
            gui_app.mainloop()
            return 0
            
        except Exception as final_error:
            print(f"[!] Все попытки запуска провалились: {final_error}")
            return 1


def cli_main():
    """Синхронная точка входа для приложения"""
    try:
        show_startup_banner()
        # Запуск приложения
        return asyncio.run(main())
    except Exception as e:
        print(f"[!] Ошибка запуска: {e}")
        return 1


if __name__ == "__main__":
    exit_code = cli_main()
    sys.exit(exit_code)
