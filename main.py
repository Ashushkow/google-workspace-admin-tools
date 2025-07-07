# -*- coding: utf-8 -*-
"""
Главный файл приложения Admin Team Tools.
Точка входа в приложение для управления пользователями Google Workspace.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_window import AdminToolsMainWindow
    from auth import get_service
    from config import CREDENTIALS_FILE
except ImportError as e:
    messagebox.showerror(
        'Ошибка импорта', 
        f'Не удалось импортировать необходимые модули: {e}\n'
        'Убедитесь, что все файлы модулей находятся в той же директории.'
    )
    sys.exit(1)


def main():
    """
    Главная функция приложения.
    Инициализирует главное окно и запускает GUI.
    """
    # Проверяем наличие файла credentials.json
    if not os.path.exists(CREDENTIALS_FILE):
        messagebox.showerror(
            'Ошибка конфигурации',
            f'Файл {CREDENTIALS_FILE} не найден.\n'
            'Скачайте его из Google Cloud Console и поместите в папку с приложением.'
        )
        return
    
    try:
        # Создаем главное окно
        root = tk.Tk()
        root.withdraw()  # Скрываем корневое окно
        
        # Инициализируем сервис Google API
        service = get_service()
        
        # Создаем и показываем главное окно приложения
        app = AdminToolsMainWindow(service=service)
        
        # Запускаем главный цикл событий
        app.mainloop()
        
    except Exception as e:
        messagebox.showerror(
            'Ошибка запуска',
            f'Произошла ошибка при запуске приложения:\n{str(e)}\n\n'
            'Проверьте подключение к интернету и настройки Google API.'
        )
        print(f"Ошибка: {e}")


if __name__ == '__main__':
    main()
