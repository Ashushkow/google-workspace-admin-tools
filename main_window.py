# -*- coding: utf-8 -*-
"""
Основное окно приложения Admin Team Tools.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, simpledialog, filedialog
import csv
from datetime import datetime
from typing import Any, Optional

from ui_components import ModernColors, ModernButton, StatusIndicator, center_window
from user_windows import CreateUserWindow, EditUserWindow
from employee_list_window import EmployeeListWindow
from additional_windows import AsanaInviteWindow, AddToGroupWindow, ErrorLogWindow
from group_management import GroupManagementWindow
from users_api import get_user_list
from groups_api import list_groups
from data_cache import data_cache


class AdminToolsMainWindow(tk.Tk):
    """
    Главное окно приложения Admin Team Tools.
    Предоставляет интерфейс для управления пользователями Google Workspace.
    """
    
    def __init__(self, service=None):
        super().__init__()
        self.service = service
        
        # Настройка главного окна
        self.title('Admin Team Tools - Управление пользователями Google Workspace')
        self.geometry('900x650')
        self.configure(bg=ModernColors.BACKGROUND)
        self.resizable(True, True)
        
        # Центрируем окно
        self.center_window()
        
        # Инициализация интерфейса
        self.setup_ui()
        
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
        header_frame = tk.Frame(self, bg=ModernColors.PRIMARY, height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Заголовок
        title_label = tk.Label(
            header_frame, 
            text='Admin Team Tools',
            font=('Arial', 20, 'bold'),
            bg=ModernColors.PRIMARY,
            fg='white'
        )
        title_label.pack(side='left', padx=20, pady=20)
        
        # Кнопка обновления данных
        refresh_btn = ModernButton(
            header_frame, 
            text='🔄 Обновить данные',
            command=self.refresh_data,
            style='secondary',
            font=('Arial', 10)
        )
        refresh_btn.pack(side='right', padx=20, pady=20)

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar_frame = tk.Frame(self, bg=ModernColors.BACKGROUND, height=60)
        toolbar_frame.pack(fill='x', padx=20, pady=(10, 0))
        toolbar_frame.pack_propagate(False)
        
        # Основные действия
        ModernButton(
            toolbar_frame,
            text='👥 Список сотрудников',
            command=self.open_employee_list,
            style='primary'
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            toolbar_frame,
            text='➕ Создать пользователя',
            command=self.open_create_user,
            style='success'
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            toolbar_frame,
            text='✏️ Редактировать пользователя',
            command=self.open_edit_user,
            style='secondary'
        ).pack(side='left', padx=(0, 10))
        
        # Группы
        ModernButton(
            toolbar_frame,
            text='👥 Управление группами',
            command=self.open_group_management,
            style='info'
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            toolbar_frame,
            text='🔗 Добавить в группу',
            command=self.open_add_to_group,
            style='secondary'
        ).pack(side='left', padx=(0, 10))
        
        # Дополнительные инструменты
        ModernButton(
            toolbar_frame,
            text='📧 Asana приглашение',
            command=self.open_asana_invite,
            style='warning'
        ).pack(side='right', padx=(10, 0))

    def create_main_area(self):
        """Создание основной рабочей области"""
        main_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Левая панель - статистика и быстрые действия
        left_panel = tk.Frame(main_frame, bg=ModernColors.CARD_BG, relief='solid', bd=1)
        left_panel.pack(side='left', fill='y', padx=(0, 10), pady=0, ipadx=15, ipady=15)
        
        # Заголовок панели
        tk.Label(
            left_panel,
            text='📊 Статистика',
            font=('Arial', 14, 'bold'),
            bg=ModernColors.CARD_BG,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 15))
        
        # Статистические карточки
        self.stats_frame = tk.Frame(left_panel, bg=ModernColors.CARD_BG)
        self.stats_frame.pack(fill='x', pady=(0, 20))
        
        self.total_users_label = tk.Label(
            self.stats_frame,
            text='Пользователи: загрузка...',
            font=('Arial', 11),
            bg=ModernColors.CARD_BG,
            fg=ModernColors.TEXT_SECONDARY
        )
        self.total_users_label.pack(anchor='w', pady=2)
        
        self.total_groups_label = tk.Label(
            self.stats_frame,
            text='Группы: загрузка...',
            font=('Arial', 11),
            bg=ModernColors.CARD_BG,
            fg=ModernColors.TEXT_SECONDARY
        )
        self.total_groups_label.pack(anchor='w', pady=2)
        
        # Быстрые действия
        tk.Label(
            left_panel,
            text='⚡ Быстрые действия',
            font=('Arial', 14, 'bold'),
            bg=ModernColors.CARD_BG,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(15, 10))
        
        quick_actions_frame = tk.Frame(left_panel, bg=ModernColors.CARD_BG)
        quick_actions_frame.pack(fill='x')
        
        ModernButton(
            quick_actions_frame,
            text='📋 Экспорт пользователей',
            command=self.export_users,
            style='secondary'
        ).pack(fill='x', pady=2)
        
        ModernButton(
            quick_actions_frame,
            text='📁 Журнал ошибок',
            command=self.open_error_log,
            style='secondary'
        ).pack(fill='x', pady=2)
        
        # Правая панель - журнал активности
        right_panel = tk.Frame(main_frame, bg=ModernColors.CARD_BG, relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=0, pady=0)
        
        # Заголовок журнала
        log_header = tk.Frame(right_panel, bg=ModernColors.CARD_BG)
        log_header.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(
            log_header,
            text='📝 Журнал активности',
            font=('Arial', 14, 'bold'),
            bg=ModernColors.CARD_BG,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left')
        
        ModernButton(
            log_header,
            text='🗑️ Очистить',
            command=self.clear_log,
            style='secondary'
        ).pack(side='right')
        
        # Текстовое поле журнала
        log_frame = tk.Frame(right_panel, bg=ModernColors.CARD_BG)
        log_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='white',
            fg=ModernColors.TEXT_PRIMARY,
            relief='solid',
            bd=1
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Загружаем начальную статистику
        self.load_statistics()

    def create_status_bar(self):
        """Создание статусной строки"""
        self.status_frame = tk.Frame(self, bg=ModernColors.SECONDARY, height=30)
        self.status_frame.pack(side='bottom', fill='x')
        self.status_frame.pack_propagate(False)
        
        self.status_indicator = StatusIndicator(self.status_frame)
        self.status_indicator.pack(side='left', padx=10, pady=5)
        
        self.status_label = tk.Label(
            self.status_frame,
            text='Готов к работе',
            font=('Arial', 9),
            bg=ModernColors.SECONDARY,
            fg=ModernColors.TEXT_PRIMARY
        )
        self.status_label.pack(side='left', pady=5)

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
        if not self.service:
            return
            
        try:
            # Загружаем пользователей
            users = get_user_list(self.service)
            users_count = len(users)
            self.total_users_label.config(text=f'Пользователи: {users_count}')
            
            # Загружаем группы
            groups = list_groups(self.service)
            groups_count = len(groups)
            self.total_groups_label.config(text=f'Группы: {groups_count}')
            
            self.log_activity(f'Статистика обновлена: {users_count} пользователей, {groups_count} групп')
            
        except Exception as e:
            self.log_activity(f'Ошибка загрузки статистики: {str(e)}', 'ERROR')

    def log_activity(self, message: str, level: str = 'INFO'):
        """Добавляет запись в журнал активности"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f'[{timestamp}] {level}: {message}\n'
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)

    def clear_log(self):
        """Очистка журнала активности"""
        self.log_text.delete(1.0, tk.END)
        self.log_activity('Журнал активности очищен')

    def refresh_data(self):
        """Принудительное обновление всех данных"""
        if not self.service:
            messagebox.showwarning('Предупреждение', 'Нет подключения к Google API')
            return
            
        try:
            self.status_label.config(text='Обновление данных...')
            data_cache.clear_cache()
            self.load_statistics()
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

    def open_add_to_group(self):
        """Открытие окна добавления в группу"""
        if not self.service:
            messagebox.showwarning('Предупреждение', 'Нет подключения к Google API')
            return
            
        try:
            window = AddToGroupWindow(self, self.service)
            self.log_activity('Открыто окно добавления в группу')
        except Exception as e:
            self.log_activity(f'Ошибка открытия окна добавления в группу: {str(e)}', 'ERROR')
            messagebox.showerror('Ошибка', f'Не удалось открыть окно добавления в группу: {str(e)}')

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
