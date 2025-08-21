#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Мастер настройки для первого запуска приложения.
"""

import os
import re
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from pathlib import Path
from typing import Optional, Tuple

# Исправляем импорты для работы в разных контекстах
try:
    from ..utils.resource_path import get_resource_path, ensure_resource_dir
except (ImportError, ValueError):
    # Fallback для прямого запуска
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from utils.resource_path import get_resource_path, ensure_resource_dir
    except ImportError:
        # Простая реализация без зависимостей
        def get_resource_path(path: str) -> Path:
            return Path(path)
        
        def ensure_resource_dir(path: Path) -> None:
            path.mkdir(parents=True, exist_ok=True)


class SetupWizard:
    """Мастер настройки для первого запуска"""
    
    def __init__(self):
        self.root = None
        self.domain_var = None
        self.admin_var = None
        self.result = None
        
    def run_gui_setup(self) -> Optional[Tuple[str, str]]:
        """Запустить GUI мастер настройки"""
        try:
            self.root = tk.Tk()
            self.root.title("Настройка Admin Team Tools")
            self.root.geometry("700x600")
            self.root.resizable(True, True)
            
            # Устанавливаем минимальный размер окна
            self.root.minsize(650, 550)
            
            # Центрируем окно
            self.root.eval('tk::PlaceWindow . center')
            
            # Делаем окно поверх всех остальных
            self.root.attributes('-topmost', True)
            self.root.lift()
            self.root.focus_force()
            
            result = self._create_wizard_gui()
            
            return result
            
        except Exception as e:
            # Если GUI не работает, показываем простое окно с ошибкой
            try:
                error_root = tk.Tk()
                error_root.withdraw()
                messagebox.showerror(
                    "Ошибка настройки", 
                    f"Не удалось запустить мастер настройки: {e}\n\n"
                    f"Создайте файл .env с настройками:\n"
                    f"GOOGLE_WORKSPACE_DOMAIN=ваш-домен.com\n"
                    f"GOOGLE_WORKSPACE_ADMIN=admin@ваш-домен.com"
                )
                error_root.destroy()
            except:
                pass
            return None
    
    def _create_wizard_gui(self) -> Optional[Tuple[str, str]]:
        """Создать GUI интерфейс мастера"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок с иконкой
        title_label = ttk.Label(
            main_frame, 
            text="🚀 Добро пожаловать в Admin Team Tools!", 
            font=('Segoe UI', 18, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # Версия
        version_label = ttk.Label(
            main_frame, 
            text="Версия 2.2.0", 
            font=('Segoe UI', 10), 
            foreground='gray'
        )
        version_label.grid(row=1, column=0, columnspan=2, pady=(0, 25), sticky=tk.W)
        
        # Описание
        description = """Для начала работы с Google Workspace необходимо указать ваш домен и email администратора.

Эти данные будут сохранены в конфигурации приложения."""
        
        desc_label = ttk.Label(main_frame, text=description, wraplength=620, font=('Segoe UI', 10))
        desc_label.grid(row=2, column=0, columnspan=2, pady=(0, 30), sticky=tk.W)
        
        # Рамка для основных настроек
        settings_frame = ttk.LabelFrame(main_frame, text=" Основные настройки ", padding="20")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Поле домена
        ttk.Label(settings_frame, text="Домен Google Workspace:", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.domain_var = tk.StringVar()
        domain_entry = ttk.Entry(settings_frame, textvariable=self.domain_var, width=55, font=('Segoe UI', 10))
        domain_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        domain_help = ttk.Label(
            settings_frame, 
            text="📝 Например: mycompany.com", 
            font=('Segoe UI', 9), 
            foreground='#666666'
        )
        domain_help.grid(row=2, column=0, sticky=tk.W, pady=(0, 15))
        
        # Поле email администратора
        ttk.Label(settings_frame, text="Email администратора:", font=('Segoe UI', 10)).grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.admin_var = tk.StringVar()
        admin_entry = ttk.Entry(settings_frame, textvariable=self.admin_var, width=45, font=('Segoe UI', 10))
        admin_entry.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        admin_help = ttk.Label(
            settings_frame, 
            text="📝 Например: admin@mycompany.com", 
            font=('Segoe UI', 9), 
            foreground='#666666'
        )
        admin_help.grid(row=5, column=0, sticky=tk.W)
        
        # Информационная секция
        info_frame = ttk.LabelFrame(main_frame, text=" ℹ️ Дополнительная информация ", padding="15")
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 25))
        
        info_text = """• Google API credentials можно настроить позже через меню
• При первом подключении откроется браузер для авторизации
• Все данные сохраняются локально на вашем компьютере"""
        
        info_label = ttk.Label(info_frame, text=info_text, font=('Segoe UI', 9), foreground='#444444')
        info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky=tk.E)
        
        cancel_button = ttk.Button(
            button_frame, 
            text="❌ Отмена", 
            command=self._cancel_setup,
            width=12
        )
        cancel_button.grid(row=0, column=0, padx=(0, 15))
        
        save_button = ttk.Button(
            button_frame, 
            text="✅ Продолжить", 
            command=self._save_setup,
            width=15
        )
        save_button.grid(row=0, column=1)
        
        # Конфигурируем колонки для растягивания
        main_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Устанавливаем фокус и привязываем Enter
        domain_entry.focus()
        
        # Привязка Enter для быстрого сохранения
        def on_enter(event):
            if self._validate_input():
                self._save_setup()
        
        domain_entry.bind('<Return>', lambda e: admin_entry.focus())
        admin_entry.bind('<Return>', on_enter)
        save_button.bind('<Return>', lambda e: self._save_setup())
        
        # Ждем результата
        self.result = None
        self.root.mainloop()
        
        return self.result
    
    def _select_credentials_file(self):
        """Выбрать файл credentials.json"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл credentials.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.credentials_path = file_path
            self.creds_path_var.set(os.path.basename(file_path))
    
    def _validate_input(self) -> bool:
        """Валидация введенных данных"""
        domain = self.domain_var.get().strip()
        admin = self.admin_var.get().strip()
        
        if not domain:
            messagebox.showerror("Ошибка", "Необходимо указать домен Google Workspace")
            return False
            
        if not admin:
            messagebox.showerror("Ошибка", "Необходимо указать email администратора")
            return False
        
        # Проверка формата домена
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, domain):
            messagebox.showerror("Ошибка", "Неверный формат домена.\nПример: mycompany.com")
            return False
        
        # Проверка формата email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, admin):
            messagebox.showerror("Ошибка", "Неверный формат email.\nПример: admin@mycompany.com")
            return False
            
        # Проверка соответствия email и домена
        email_domain = admin.split('@')[1]
        if email_domain != domain:
            result = messagebox.askyesno(
                "Предупреждение", 
                f"Email администратора не соответствует домену:\n"
                f"Email: {admin}\n"
                f"Домен: {domain}\n\n"
                f"Продолжить с этими настройками?"
            )
            if not result:
                return False
        
        return True
    
    def _save_setup(self):
        """Сохранить настройки"""
        if not self._validate_input():
            return
            
        domain = self.domain_var.get().strip()
        admin = self.admin_var.get().strip()
        
        self.result = (domain, admin)
        
        # Показываем сообщение об успехе с дополнительной информацией
        messagebox.showinfo(
            "Настройка завершена",
            f"Настройки сохранены:\n\n"
            f"🏢 Домен: {domain}\n"
            f"👤 Администратор: {admin}\n\n"
            f"Далее необходимо:\n"
            f"1. Настроить Google API credentials\n"
            f"2. Выполнить первую авторизацию\n\n"
            f"Приложение продолжит запуск..."
        )
        
        self.root.destroy()
    
    def _cancel_setup(self):
        """Отменить настройку"""
        result = messagebox.askyesno(
            "Подтверждение", 
            "Отменить настройку?\n\nПриложение будет закрыто.\nВы сможете настроить его позже."
        )
        if result:
            self.result = None
            self.root.destroy()


def run_setup_wizard() -> Optional[Tuple[str, str]]:
    """Запустить GUI мастер настройки"""
    wizard = SetupWizard()
    return wizard.run_gui_setup()
