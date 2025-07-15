# -*- coding: utf-8 -*-
"""
Улучшенная версия основного окна приложения Admin Team Tools.
Применены принципы SOLID и лучшие практики.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Optional, Any, Callable
from datetime import datetime

from .ui_components import ModernColors, ModernButton, StatusIndicator
from .components.statistics_panel import StatisticsPanel
from .components.activity_log import ActivityLog
from .components.toolbar import MainToolbar
from .user_windows import CreateUserWindow, EditUserWindow
from .employee_list_window import EmployeeListWindow
from .additional_windows import AsanaInviteWindow, ErrorLogWindow
from .group_management import GroupManagementWindow
from ..services.data_service import DataService
from ..services.export_service import ExportService
from ..config.main_window_config import MainWindowConfig
from ..utils.ui_decorators import handle_ui_errors


class AdminToolsMainWindow(tk.Tk):
    """
    Главное окно приложения Admin Team Tools.
    Рефакторированная версия с улучшенной архитектурой.
    """
    
    def __init__(self, service: Optional[Any] = None) -> None:
        super().__init__()
        
        # Инициализация сервисов
        self.service = service
        self.data_service = DataService(service)
        self.export_service = ExportService(service)
        
        # Состояние UI
        self._ui_initialized = False
        
        # Инициализация
        self._setup_window()
        self._setup_ui()
        self._schedule_initialization()

    def _setup_window(self) -> None:
        """Настройка основного окна"""
        self.title(MainWindowConfig.TITLE)
        self.geometry(MainWindowConfig.GEOMETRY)
        self.minsize(MainWindowConfig.MIN_WIDTH, MainWindowConfig.MIN_HEIGHT)
        self.configure(bg=ModernColors.BACKGROUND)
        self.resizable(True, True)
        self._center_window()

    def _center_window(self) -> None:
        """Центрирует окно на экране"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса"""
        self._create_header()
        self.toolbar = MainToolbar(self, self._get_toolbar_callbacks())
        self._create_main_area()
        self._create_status_bar()

    def _create_header(self) -> None:
        """Создание заголовка приложения"""
        header_frame = tk.Frame(
            self, 
            bg=ModernColors.PRIMARY, 
            height=MainWindowConfig.HEADER_HEIGHT
        )
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text='Admin Team Tools',
            font=('Arial', 16, 'bold'),
            bg=ModernColors.PRIMARY,
            fg='white'
        ).pack(side='left', padx=15, pady=15)
        
        ModernButton(
            header_frame,
            text='🔄 Обновить',
            command=self.refresh_data,
            style='secondary',
            font=('Arial', 9)
        ).pack(side='right', padx=15, pady=15)

    def _create_main_area(self) -> None:
        """Создание основной рабочей области"""
        main_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        # Левая панель - статистика и быстрые действия
        self.statistics_panel = StatisticsPanel(
            main_frame, 
            self.data_service,
            self._get_quick_actions_callbacks()
        )
        self.statistics_panel.pack(side='left', fill='y', padx=(0, 8))
        
        # Правая панель - журнал активности
        self.activity_log = ActivityLog(main_frame)
        self.activity_log.pack(side='right', fill='both', expand=True)

    def _create_status_bar(self) -> None:
        """Создание статусной строки"""
        self.status_frame = tk.Frame(
            self, 
            bg=ModernColors.SECONDARY, 
            height=MainWindowConfig.STATUS_BAR_HEIGHT
        )
        self.status_frame.pack(side='bottom', fill='x')
        self.status_frame.pack_propagate(False)
        
        self.status_indicator = StatusIndicator(self.status_frame)
        self.status_indicator.pack(side='left', padx=8, pady=3)
        
        self.status_label = tk.Label(
            self.status_frame,
            text=MainWindowConfig.MESSAGES['ready'],
            font=('Arial', 8),
            bg=ModernColors.SECONDARY,
            fg=ModernColors.TEXT_PRIMARY
        )
        self.status_label.pack(side='left', pady=3)

    def _get_toolbar_callbacks(self) -> dict:
        """Возвращает callbacks для панели инструментов"""
        return {
            'employee_list': self.open_employee_list,
            'create_user': self.open_create_user,
            'edit_user': self.open_edit_user,
            'groups': self.open_group_management,
            'asana': self.open_asana_invite
        }

    def _get_quick_actions_callbacks(self) -> dict:
        """Возвращает callbacks для быстрых действий"""
        return {
            'export': self.export_users,
            'error_log': self.open_error_log
        }

    def _schedule_initialization(self) -> None:
        """Планирует отложенную инициализацию"""
        self.after(MainWindowConfig.DELAYED_INIT_DELAY, self._delayed_init)
        self.check_service_status()

    def _delayed_init(self) -> None:
        """Отложенная инициализация после создания UI"""
        self._ui_initialized = True
        self.log_activity('Приложение готово к работе')
        
        # Загружаем статистику
        self.after(MainWindowConfig.STATISTICS_LOAD_DELAY, self._load_statistics_async)

    def _load_statistics_async(self) -> None:
        """Асинхронная загрузка статистики"""
        if not self._ui_initialized or not self.statistics_panel:
            self.after(MainWindowConfig.RETRY_DELAY, self._load_statistics_async)
            return
        
        self.statistics_panel.load_statistics()

    def check_service_status(self) -> None:
        """Проверка статуса подключения к Google API"""
        if self.service:
            self.status_indicator.set_status('online')
            self.status_label.config(text=MainWindowConfig.MESSAGES['connected'])
            self.log_activity('Успешное подключение к Google Workspace API')
        else:
            self.status_indicator.set_status('offline')
            self.status_label.config(text=MainWindowConfig.MESSAGES['no_connection'])
            self.log_activity('Ошибка: Нет подключения к Google API', 'ERROR')

    def log_activity(self, message: str, level: str = 'INFO') -> None:
        """Добавляет запись в журнал активности"""
        if hasattr(self, 'activity_log'):
            self.activity_log.add_entry(message, level)

    def refresh_data(self) -> None:
        """Принудительное обновление всех данных"""
        if not self.service:
            messagebox.showwarning(
                'Предупреждение', 
                MainWindowConfig.MESSAGES['no_connection']
            )
            return
        
        try:
            self.status_label.config(text=MainWindowConfig.MESSAGES['loading'])
            self.data_service.clear_cache()
            self.statistics_panel.refresh()
            self.status_label.config(text=MainWindowConfig.MESSAGES['updated'])
            self.log_activity('Принудительное обновление данных выполнено')
        except Exception as e:
            self._handle_error(e, 'обновление данных')

    def _handle_error(self, error: Exception, operation: str) -> None:
        """Централизованная обработка ошибок"""
        error_msg = f'Ошибка {operation}: {str(error)}'
        self.log_activity(error_msg, 'ERROR')
        messagebox.showerror('Ошибка', error_msg)

    # Методы для открытия окон с улучшенной обработкой ошибок
    @handle_ui_errors("открытие списка сотрудников")
    def open_employee_list(self) -> None:
        """Открытие окна списка сотрудников"""
        EmployeeListWindow(self, self.service)

    @handle_ui_errors("открытие окна создания пользователя")
    def open_create_user(self) -> None:
        """Открытие окна создания пользователя"""
        CreateUserWindow(self, self.service)

    @handle_ui_errors("открытие окна редактирования пользователя")
    def open_edit_user(self) -> None:
        """Открытие окна редактирования пользователя"""
        EditUserWindow(self, self.service)

    @handle_ui_errors("открытие окна управления группами")
    def open_group_management(self) -> None:
        """Открытие окна управления группами"""
        GroupManagementWindow(self, self.service)

    def open_asana_invite(self) -> None:
        """Открытие окна приглашения в Asana"""
        try:
            AsanaInviteWindow(self)
            self.log_activity('Открыто окно приглашения в Asana')
        except Exception as e:
            self._handle_error(e, 'открытие окна Asana')

    def open_error_log(self) -> None:
        """Открытие окна журнала ошибок"""
        try:
            ErrorLogWindow(self)
            self.log_activity('Открыто окно журнала ошибок')
        except Exception as e:
            self._handle_error(e, 'открытие журнала ошибок')

    @handle_ui_errors("экспорт пользователей")
    def export_users(self) -> None:
        """Экспорт списка пользователей в файл"""
        self.export_service.export_users_to_csv(self.log_activity)
