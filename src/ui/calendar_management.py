# -*- coding: utf-8 -*-
"""
Окно управления календарями Google.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Optional

from .ui_components import ModernColors, ModernButton, center_window


class CalendarManagementWindow(tk.Toplevel):
    """
    Окно для управления календарями Google.
    """
    
    def __init__(self, master=None, service=None):
        super().__init__(master)
        self.service = service
        self.master_window = master
        
        # Настройка окна
        self.title('Управление календарями Google')
        self.geometry('800x600')
        self.resizable(True, True)
        self.configure(bg=ModernColors.BACKGROUND)
        self.transient(master)
        
        # Центрируем окно относительно родительского
        if master:
            center_window(self, master)
            
        self.setup_ui()
        self.load_calendars()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(
            header_frame,
            text='📅 Управление календарями Google',
            font=('Arial', 16, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left')
        
        # Панель кнопок
        buttons_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        buttons_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        ModernButton(
            buttons_frame,
            text='🔄 Обновить',
            command=self.load_calendars,
            style='primary'
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text='➕ Создать календарь',
            command=self.create_calendar,
            style='success'
        ).pack(side='left', padx=(0, 8))
        
        # Список календарей
        list_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Создаем Treeview для списка календарей
        columns = ('name', 'owner', 'access', 'description')
        self.calendar_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        self.calendar_tree.heading('name', text='Название')
        self.calendar_tree.heading('owner', text='Владелец')
        self.calendar_tree.heading('access', text='Доступ')
        self.calendar_tree.heading('description', text='Описание')
        
        self.calendar_tree.column('name', width=250)
        self.calendar_tree.column('owner', width=200)
        self.calendar_tree.column('access', width=150)
        self.calendar_tree.column('description', width=300)
        
        # Scrollbar для списка
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.calendar_tree.yview)
        self.calendar_tree.configure(yscrollcommand=scrollbar.set)
        
        # Упаковка
        self.calendar_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Статус бар
        self.status_label = tk.Label(
            self,
            text='Готов',
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_SECONDARY,
            anchor='w',
            padx=10,
            pady=5
        )
        self.status_label.pack(fill='x', side='bottom')

    def load_calendars(self):
        """Загрузка списка календарей"""
        try:
            self.status_label.config(text='Загрузка календарей...')
            self.update()
            
            # Очищаем список
            for item in self.calendar_tree.get_children():
                self.calendar_tree.delete(item)
            
            if not self.service:
                messagebox.showerror("Ошибка", "Сервис Google API недоступен")
                return
            
            # Здесь будет код для загрузки календарей через Calendar API
            # Пока добавим тестовые данные
            test_calendars = [
                ("Основной календарь", "admin@company.com", "Владелец", "Основной рабочий календарь"),
                ("Командный календарь", "team@company.com", "Редактор", "Календарь для командных встреч"),
                ("Праздники", "calendar@google.com", "Читатель", "Государственные праздники")
            ]
            
            for calendar_data in test_calendars:
                self.calendar_tree.insert('', 'end', values=calendar_data)
            
            self.status_label.config(text=f'Загружено календарей: {len(test_calendars)}')
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить календари:\n{str(e)}")
            self.status_label.config(text='Ошибка загрузки')

    def create_calendar(self):
        """Создание нового календаря"""
        messagebox.showinfo("В разработке", "Функция создания календаря будет реализована в следующих версиях")

    def on_closing(self):
        """Обработчик закрытия окна"""
        self.destroy()


def open_calendar_management(master=None, service=None):
    """
    Открытие окна управления календарями.
    
    Args:
        master: Родительское окно
        service: Сервис Google API
    """
    try:
        window = CalendarManagementWindow(master, service)
        window.protocol("WM_DELETE_WINDOW", window.on_closing)
        return window
    except Exception as e:
        messagebox.showerror(
            "Ошибка",
            f"Не удалось открыть окно управления календарями:\n{str(e)}"
        )
        return None