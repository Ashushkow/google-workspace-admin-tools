#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Точка входа в приложение Admin Team Tools.
Приложение для управления пользователями Google Workspace.
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import messagebox

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error.log'),
        logging.StreamHandler()
    ]
)

def check_credentials():
    """Проверка наличия файла credentials.json"""
    credentials_path = 'credentials.json'
    if not os.path.exists(credentials_path):
        messagebox.showerror(
            "Отсутствует credentials.json",
            "Файл credentials.json не найден в корневой папке проекта.\n\n"
            "Для создания OAuth 2.0 credentials:\n"
            "1. Откройте docs/OAUTH2_SETUP.md\n"
            "2. Перейдите в Google Cloud Console\n"
            "3. Создайте OAuth 2.0 Client ID (Desktop application)\n"
            "4. Скачайте credentials.json\n"
            "5. Поместите файл в корневую папку проекта\n\n"
            "📖 Подробная инструкция: docs/OAUTH2_SETUP.md"
        )
        return False
    return True

def run_application():
    """Запуск основного приложения"""
    # Проверяем наличие credentials.json
    if not check_credentials():
        sys.exit(1)
        
    try:
        # Импорт основных модулей
        from src.auth import get_service
        from src.ui.main_window import AdminToolsMainWindow
        
        # Создание основного окна
        root = AdminToolsMainWindow()
        
        # Попытка авторизации
        try:
            service = get_service()
            root.service = service
            root.check_service_status()
        except FileNotFoundError as e:
            logging.exception("Файл не найден")
            messagebox.showerror(
                "Файл не найден", 
                f"Отсутствует необходимый файл:\n{str(e)}\n\n"
                "Убедитесь, что файл credentials.json находится в корневой папке проекта."
            )
            sys.exit(1)
        except Exception as e:
            logging.exception("Ошибка авторизации")
            error_msg = str(e)
            if "DOMAIN_ADMIN_EMAIL" in error_msg:
                messagebox.showerror(
                    "Настройка Service Account", 
                    f"{error_msg}\n\n"
                    "Инструкция: docs/SERVICE_ACCOUNT_SETUP.md"
                )
            elif "insufficient permissions" in error_msg.lower() or "delegat" in error_msg.lower():
                messagebox.showerror(
                    "Права доступа", 
                    f"Проблема с правами Service Account:\n{error_msg}\n\n"
                    "Необходимо настроить Domain-wide delegation.\n"
                    "Инструкция: docs/SERVICE_ACCOUNT_SETUP.md"
                )
            elif "credentials" in error_msg.lower():
                messagebox.showerror(
                    "Ошибка конфигурации", 
                    f"Проблема с файлом credentials.json:\n{error_msg}\n\n"
                    "Проверьте правильность настройки Google API в docs/API_SETUP.md"
                )
            else:
                messagebox.showerror(
                    "Ошибка авторизации", 
                    f"Не удалось подключиться к Google API:\n{error_msg}\n\n"
                    "Проверьте:\n"
                    "• Интернет-соединение\n"
                    "• Настройки Google API\n"
                    "• Права доступа аккаунта\n"
                    "• Domain-wide delegation (для Service Account)"
                )
            sys.exit(1)
        
        # Запуск главного цикла
        root.mainloop()
        
    except ImportError as e:
        logging.exception("Ошибка модулей")
        messagebox.showerror(
            "Ошибка модулей", 
            f"Не удалось загрузить необходимые модули:\n{str(e)}\n\n"
            "Проверьте, что все файлы проекта находятся в рабочей директории."
        )
        sys.exit(1)
    except Exception as e:
        logging.exception("Критическая ошибка")
        messagebox.showerror(
            "Критическая ошибка", 
            f"Произошла непредвиденная ошибка:\n{str(e)}"
        )
        sys.exit(1)

if __name__ == "__main__":
    # Запуск приложения
    run_application()
