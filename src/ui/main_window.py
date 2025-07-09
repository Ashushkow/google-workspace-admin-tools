# -*- coding: utf-8 -*-
"""
Основное окно приложения Admin Team Tools.
Рефакторированная версия с разделенными компонентами.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import csv
from datetime import datetime
from typing import Any, Optional

from .ui_components import ModernColors, ModernButton, StatusIndicator, center_window
from .components import StatisticsPanel, ActivityLog, MainToolbar
from .user_windows import CreateUserWindow, EditUserWindow
from .employee_list_window import EmployeeListWindow
from .additional_windows import AsanaInviteWindow, ErrorLogWindow
from .group_management import GroupManagementWindow
from ..api.users_api import get_user_list
from ..api.groups_api import list_groups
from ..utils.data_cache import data_cache
from ..utils.simple_utils import async_manager, error_handler, SimpleProgressDialog, show_api_error


class AdminToolsMainWindow(tk.Tk):
    """
    Главное окно приложения Admin Team Tools.
    Рефакторированная версия с разделенными компонентами.
    """
    
    def __init__(self, service=None):
        super().__init__()
        self.service = service
        self._ui_initialized = False
        
        # Компоненты UI
        self.statistics_panel = None
        self.activity_log = None
        self.toolbar = None
        
        # Настройка главного окна
        self.title('Admin Team Tools v2.0 - Управление пользователями Google Workspace')
        self.geometry('750x500')
        self.configure(bg=ModernColors.BACKGROUND)
        self.resizable(True, True)
        
        # Центрируем окно
        self.center_window()
        
        # Инициализация интерфейса
        self.setup_ui()
        
        # Отложенная инициализация UI
        self.after(1000, self._delayed_init)
        
        # Статус соединения
        self.check_service_status()

    def center_window(self):
        """Центрирует окно на экране"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        self.create_header()
        
        # Панель инструментов
        self.create_toolbar()
        
        # Основная рабочая область
        self.create_main_area()
        
        # Статусная строка
        self.create_status_bar()

    def create_header(self):
        """Создание заголовка приложения"""
        header_frame = tk.Frame(self, bg=ModernColors.PRIMARY, height=60)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Заголовок
        title_label = tk.Label(
            header_frame, 
            text='Admin Team Tools',
            font=('Arial', 16, 'bold'),
            bg=ModernColors.PRIMARY,
            fg='white'
        )
        title_label.pack(side='left', padx=15, pady=15)
        
        # Кнопка обновления данных
        refresh_btn = ModernButton(
            header_frame, 
            text='🔄 Обновить',
            command=self.refresh_data,
            style='secondary',
            font=('Arial', 9)
        )
        refresh_btn.pack(side='right', padx=15, pady=15)

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar_callbacks = {
            'employee_list': self.open_employee_list,
            'create_user': self.open_create_user,
            'edit_user': self.open_edit_user,
            'groups': self.open_group_management,
            'asana': self.open_asana_invite
        }
        
        self.toolbar = MainToolbar(self, toolbar_callbacks)

    def create_main_area(self):
        """Создание основной рабочей области"""
        main_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        # Левая панель - статистика и быстрые действия
        quick_actions_callbacks = {
            'export': self.export_users,
            'error_log': self.open_error_log
        }
        
        self.statistics_panel = StatisticsPanel(
            main_frame, 
            self.service, 
            quick_actions_callbacks
        )
        
        # Правая панель - журнал активности
        self.activity_log = ActivityLog(main_frame)
        
        # Загружаем начальную статистику асинхронно (с задержкой)
        self.after(2000, self.load_statistics_async)

    def create_status_bar(self):
        """Создание статусной строки"""
        self.status_frame = tk.Frame(self, bg=ModernColors.SECONDARY, height=25)
        self.status_frame.pack(side='bottom', fill='x')
        self.status_frame.pack_propagate(False)
        
        self.status_indicator = StatusIndicator(self.status_frame)
        self.status_indicator.pack(side='left', padx=8, pady=3)
        
        self.status_label = tk.Label(
            self.status_frame,
            text='Готов к работе',
            font=('Arial', 8),
            bg=ModernColors.SECONDARY,
            fg=ModernColors.TEXT_PRIMARY
        )
        self.status_label.pack(side='left', pady=3)

    def check_service_status(self):
        """Проверка статуса подключения к Google API"""
        if self.service:
            self.status_indicator.set_status('online')
            self.status_label.config(text='Подключен к Google Workspace API')
            self.log_activity('Успешное подключение к Google Workspace API')
        else:
            self.status_indicator.set_status('offline')
            self.status_label.config(text='Нет подключения к Google API')
            self.log_activity('Ошибка: Нет подключения к Google API', 'ERROR')

    def load_statistics(self):
        """Загрузка статистики пользователей и групп"""
        if not self.service or not self.statistics_panel:
            return
            
        try:
            users_count, groups_count = self.statistics_panel.load_statistics()
            self.log_activity(f'Статистика обновлена: {users_count} пользователей, {groups_count} групп')
        except Exception as e:
            self.log_activity(f'Ошибка загрузки статистики: {str(e)}', 'ERROR')

    def log_activity(self, message: str, level: str = 'INFO'):
        """Добавляет запись в журнал активности"""
        if self.activity_log:
            self.activity_log.add_entry(message, level)

    def clear_log(self):
        """Очистка журнала активности"""
        if self.activity_log:
            self.activity_log.clear_log()

    def refresh_data(self):
        """Принудительное обновление всех данных"""
        if not self.service:
            messagebox.showwarning('Предупреждение', 'Нет подключения к Google API')
            return
            
        try:
            self.status_label.config(text='Обновление данных...')
            data_cache.clear_cache()
            
            if self.statistics_panel:
                self.statistics_panel.refresh()
                
            self.status_label.config(text='Данные обновлены')
            self.log_activity('Принудительное обновление данных выполнено')
        except Exception as e:
            self.log_activity(f'Ошибка обновления данных: {str(e)}', 'ERROR')
            messagebox.showerror('Ошибка', f'Ошибка обновления данных: {str(e)}')

    # Методы для открытия окон
    def open_employee_list(self):
        """Открытие окна списка сотрудников"""
        if not self.service:
            messagebox.showwarning('Предупреждение', 'Нет подключения к Google API')
            return
            
        try:
            window = EmployeeListWindow(self, self.service)
            self.log_activity('Открыто окно списка сотрудников')
        except Exception as e:
            self.log_activity(f'Ошибка открытия списка сотрудников: {str(e)}', 'ERROR')
            messagebox.showerror('Ошибка', f'Не удалось открыть список сотрудников: {str(e)}')

    def open_create_user(self):
        """Открытие окна создания пользователя"""
        if not self.service:
            messagebox.showwarning('Предупреждение', 'Нет подключения к Google API')
            return
            
        try:
            window = CreateUserWindow(self, self.service)
            self.log_activity('Открыто окно создания пользователя')
        except Exception as e:
            self.log_activity(f'Ошибка открытия окна создания пользователя: {str(e)}', 'ERROR')
            messagebox.showerror('Ошибка', f'Не удалось открыть окно создания пользователя: {str(e)}')

    def open_edit_user(self):
        """Открытие окна редактирования пользователя"""
        if not self.service:
            messagebox.showwarning('Предупреждение', 'Нет подключения к Google API')
            return
            
        # Запрашиваем email пользователя
        user_email = simpledialog.askstring(
            'Редактирование пользователя',
            'Введите email пользователя для редактирования:'
        )
        
        if user_email:
            try:
                window = EditUserWindow(self, self.service, user_email)
                self.log_activity(f'Открыто окно редактирования пользователя: {user_email}')
            except Exception as e:
                self.log_activity(f'Ошибка открытия окна редактирования: {str(e)}', 'ERROR')
                messagebox.showerror('Ошибка', f'Не удалось открыть окно редактирования: {str(e)}')

    def open_group_management(self):
        """Открытие окна управления группами"""
        if not self.service:
            messagebox.showwarning('Предупреждение', 'Нет подключения к Google API')
            return
            
        try:
            window = GroupManagementWindow(self, self.service)
            self.log_activity('Открыто окно управления группами')
        except Exception as e:
            self.log_activity(f'Ошибка открытия окна управления группами: {str(e)}', 'ERROR')
            messagebox.showerror('Ошибка', f'Не удалось открыть окно управления группами: {str(e)}')

    def open_asana_invite(self):
        """Открытие окна приглашения в Asana"""
        try:
            window = AsanaInviteWindow(self)
            self.log_activity('Открыто окно приглашения в Asana')
        except Exception as e:
            self.log_activity(f'Ошибка открытия окна Asana: {str(e)}', 'ERROR')
            messagebox.showerror('Ошибка', f'Не удалось открыть окно Asana: {str(e)}')

    def open_error_log(self):
        """Открытие окна журнала ошибок"""
        try:
            window = ErrorLogWindow(self)
            self.log_activity('Открыто окно журнала ошибок')
        except Exception as e:
            self.log_activity(f'Ошибка открытия журнала ошибок: {str(e)}', 'ERROR')
            messagebox.showerror('Ошибка', f'Не удалось открыть журнал ошибок: {str(e)}')

    def export_users(self):
        """Экспорт списка пользователей в файл"""
        if not self.service:
            messagebox.showwarning('Предупреждение', 'Нет подключения к Google API')
            return
            
        try:
            # Выбираем файл для сохранения
            filename = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
                title='Сохранить список пользователей'
            )
            
            if filename:
                users = get_user_list(self.service)
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Email', 'Имя', 'Фамилия', 'Организация', 'Статус'])
                    
                    for user in users:
                        name = user.get('name', {})
                        org_info = user.get('organizations', [{}])[0] if user.get('organizations') else {}
                        
                        writer.writerow([
                            user.get('primaryEmail', ''),
                            name.get('givenName', ''),
                            name.get('familyName', ''),
                            org_info.get('title', ''),
                            'Активен' if not user.get('suspended', False) else 'Заблокирован'
                        ])
                
                self.log_activity(f'Экспорт пользователей завершен: {filename}')
                messagebox.showinfo('Успех', f'Список пользователей сохранен в {filename}')
                
        except Exception as e:
            self.log_activity(f'Ошибка экспорта пользователей: {str(e)}', 'ERROR')
            messagebox.showerror('Ошибка', f'Ошибка экспорта: {str(e)}')

    def load_statistics_async(self):
        """Асинхронная загрузка статистики"""
        if not self._ui_initialized or not self.statistics_panel:
            # Если UI не готов, отложим загрузку
            self.after(500, self.load_statistics_async)
            return
            
        def load_data():
            if not self.service:
                return None, None
            
            users = get_user_list(self.service)
            groups = list_groups(self.service)
            return users, groups
        
        def on_success(result):
            if not self.statistics_panel:
                return
                
            users, groups = result
            if users is not None and groups is not None:
                users_count = len(users)
                groups_count = len(groups)
                self.statistics_panel.update_statistics(users_count, groups_count)
                self.log_activity(f'Статистика обновлена: {users_count} пользователей, {groups_count} групп')
        
        def on_error(error):
            if hasattr(self, 'log_activity'):
                self.log_activity(f'Ошибка загрузки статистики: {str(error)}', 'ERROR')
            show_api_error(self, error, "загрузка статистики")
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text='Загрузка статистики...')
        
        async_manager.run_async(load_data, on_success, on_error)

    def _delayed_init(self):
        """Отложенная инициализация после создания UI"""
        self._ui_initialized = True
        self.log_activity('Приложение готово к работе')
