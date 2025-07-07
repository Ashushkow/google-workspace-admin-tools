#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Точка входа в приложение Admin Team Tools.
Приложение для управления пользователями Google Workspace.
"""

import sys
import tkinter as tk
from tkinter import messagebox

def run_application():
    """Запуск основного приложения"""
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
        except Exception as e:
            messagebox.showerror(
                "Ошибка авторизации", 
                f"Не удалось подключиться к Google API:\n{str(e)}\n\n"
                "Убедитесь, что файл credentials.json настроен правильно."
            )
        
        # Запуск главного цикла
        root.mainloop()
        
    except ImportError as e:
        messagebox.showerror(
            "Ошибка модулей", 
            f"Не удалось загрузить необходимые модули:\n{str(e)}\n\n"
            "Проверьте, что все файлы проекта находятся в рабочей директории."
        )
    except Exception as e:
        messagebox.showerror(
            "Критическая ошибка", 
            f"Произошла непредвиденная ошибка:\n{str(e)}"
        )

if __name__ == "__main__":
    # Запуск приложения
    run_application()
