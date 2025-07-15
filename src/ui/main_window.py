# -*- coding: utf-8 -*-
"""
Основное окно приложения Admin Team Tools.
Рефакторированная версия с разделенными компонентами.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import csv
import logging
from datetime import datetime
from typing import Any, Optional, List, Dict

from .ui_components import ModernColors, ModernButton, StatusIndicator, center_window
from .components import StatisticsPanel, ActivityLog, MainToolbar, ThemeSwitcher
from .user_windows import CreateUserWindow, EditUserWindow
from .employee_list_window import EmployeeListWindow
from .additional_windows import AsanaInviteWindow, ErrorLogWindow
from .group_management import GroupManagementWindow
from .calendar_management import open_calendar_management
from .sputnik_calendar_ui import open_sputnik_calendar_window
from ..api.users_api import get_user_list
from ..api.service_adapter import ServiceAdapter
from ..api.groups_api import list_groups
from ..utils.data_cache import data_cache
from ..utils.simple_utils import async_manager, error_handler, SimpleProgressDialog, show_api_error
from ..utils.ui_decorators import handle_service_errors, handle_ui_errors, log_operation, validate_email, measure_performance
from ..themes.theme_manager import theme_manager
from ..hotkeys.hotkey_manager import HotkeyManager


class AdminToolsMainWindow(tk.Tk):
    """
    Главное окно приложения Admin Team Tools.
    Рефакторированная версия с разделенными компонентами.
    """
    
    def __init__(self, service=None):
        super().__init__()
        self.service = service
        self._ui_initialized = False
        self.logger = logging.getLogger(__name__)
        
        # Компоненты UI
        self.statistics_panel = None
        self.activity_log = None
        self.toolbar = None
        self.theme_switcher = None
        self.status_indicator = None
        self.status_label = None
        self.header_frame = None
        self.title_label = None
        self.status_frame = None
        
        # Инициализация менеджеров
        self.hotkey_manager = HotkeyManager(self)
        self._setup_hotkeys()
        
        # Настройка главного окна
        self.title('Admin Team Tools v2.0.5 - Управление пользователями Google Workspace')
        self.geometry('750x500')
        self.resizable(True, True)
        
        # Центрируем окно
        self.center_window()
        
        # Создаем UI
        self.setup_ui()
        
        # Применяем тему и загружаем настройки
        self.apply_theme()
        self._load_theme_preferences()
        
        # Подписываемся на изменения темы
        theme_manager.add_theme_change_callback(self.on_theme_changed)
        
        # Настройка обработчика закрытия
        self.protocol("WM_DELETE_WINDOW", self.quit_application)
        
        # Отложенная инициализация
        self.after(1000, self._delayed_init)

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
        # Создаем меню
        self.create_menu()
        
        # Заголовок приложения
        self.create_header()
        
        # Панель инструментов
        self.create_toolbar()
        
        # Основная рабочая область
        self.create_main_area()
        
        # Статусная строка
        self.create_status_bar()

    def create_header(self):
        """Создание заголовка приложения"""
        self.header_frame = tk.Frame(self, height=60)
        self.header_frame.pack(fill='x', padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        # Заголовок
        self.title_label = tk.Label(
            self.header_frame, 
            text='Admin Team Tools',
            font=('Arial', 16, 'bold'),
            fg='white'
        )
        self.title_label.pack(side='left', padx=15, pady=15)
        
        # Переключатель тем
        self.theme_switcher = ThemeSwitcher(self.header_frame)
        self.theme_switcher.pack(side='right', padx=(10, 5), pady=15)
        
        # Кнопка обновления данных
        self.refresh_btn = ModernButton(
            self.header_frame, 
            text='🔄 Обновить',
            command=self.refresh_data,
            style='secondary',
            font=('Arial', 9)
        )
        self.refresh_btn.pack(side='right', padx=(5, 10), pady=15)

    def create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(
            label="Экспорт пользователей",
            command=self.export_users,
            accelerator="Ctrl+E"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Выход",
            command=self.quit_application,
            accelerator="Ctrl+Q"
        )
        
        # Меню "Пользователи"
        users_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Пользователи", menu=users_menu)
        users_menu.add_command(
            label="Список пользователей",
            command=self.open_employee_list,
            accelerator="Ctrl+U"
        )
        users_menu.add_command(
            label="Новый пользователь",
            command=self.open_create_user,
            accelerator="Ctrl+N"
        )
        users_menu.add_command(
            label="Редактировать пользователя",
            command=self.open_edit_user,
            accelerator="Ctrl+Enter"
        )
        
        # Меню "Группы"
        groups_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Группы", menu=groups_menu)
        groups_menu.add_command(
            label="Управление группами",
            command=self.open_group_management,
            accelerator="Ctrl+G"
        )
        
        # Меню "Календари"
        calendars_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Календари", menu=calendars_menu)
        calendars_menu.add_command(
            label="🎯 Календарь SPUTNIK (общий)",
            command=self.open_sputnik_calendar,
            accelerator="Ctrl+Shift+S"
        )
        calendars_menu.add_separator()
        calendars_menu.add_command(
            label="Управление календарями",
            command=self.open_calendar_management,
            accelerator="Ctrl+Shift+C"
        )
        
        # Меню "Документы"
        documents_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Документы", menu=documents_menu)
        documents_menu.add_command(
            label="Управление доступом к документам",
            command=self.open_document_management,
            accelerator="Ctrl+D"
        )
        
        # Меню "Вид"
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        # Подменю тем
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Тема", menu=theme_menu)
        theme_menu.add_command(
            label="Светлая",
            command=lambda: theme_manager.set_theme('light'),
            accelerator="Ctrl+1"
        )
        theme_menu.add_command(
            label="Тёмная",
            command=lambda: theme_manager.set_theme('dark'),
            accelerator="Ctrl+2"
        )
        theme_menu.add_command(
            label="Синяя",
            command=lambda: theme_manager.set_theme('blue'),
            accelerator="Ctrl+3"
        )
        
        view_menu.add_separator()
        view_menu.add_command(
            label="Обновить",
            command=self.refresh_data,
            accelerator="Ctrl+R"
        )
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(
            label="Горячие клавиши",
            command=self.hotkey_manager.show_help_dialog,
            accelerator="F1"
        )
        help_menu.add_command(
            label="О программе",
            command=self.show_about,
            accelerator="Ctrl+F1"
        )

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar_callbacks = {
            'employee_list': self.open_employee_list,
            'create_user': self.open_create_user,
            'edit_user': self.open_edit_user,
            'groups': self.open_group_management,
            'sputnik_calendar': self.open_sputnik_calendar,
            'calendars': self.open_calendar_management,
            'documents': self.open_document_management,
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
        # Проверяем, что UI инициализирован
        if not self._ui_initialized or not hasattr(self, 'status_indicator') or not self.status_indicator:
            return
            
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
        if not self._ui_initialized or not self.service or not self.statistics_panel:
            return
            
        try:
            users_count, groups_count = self.statistics_panel.load_statistics()
            self.log_activity(f'Статистика обновлена: {users_count} пользователей, {groups_count} групп')
        except Exception as e:
            self.log_activity(f'Ошибка загрузки статистики: {str(e)}', 'ERROR')

    def log_activity(self, message: str, level: str = 'INFO'):
        """Добавляет запись в журнал активности"""
        if self._ui_initialized and self.activity_log:
            self.activity_log.add_entry(message, level)

    def clear_log(self):
        """Очистка журнала активности"""
        if self.activity_log:
            self.activity_log.clear_log()

    @handle_ui_errors("обновление данных", show_success=True)
    def refresh_data(self):
        """Принудительное обновление всех данных"""
        if not self.service:
            messagebox.showwarning('Предупреждение', 'Нет подключения к Google API')
            return
            
        self.status_label.config(text='Обновление данных...')
        data_cache.clear_cache()
        
        if self.statistics_panel:
            self.statistics_panel.refresh()
            
        self.status_label.config(text='Данные обновлены')
        return "Принудительное обновление данных выполнено"

    def _setup_hotkeys(self):
        """Настройка горячих клавиш"""
        # Основные операции
        self.hotkey_manager.register_callback('refresh', self.refresh_data)
        self.hotkey_manager.register_callback('export', self.export_users)
        self.hotkey_manager.register_callback('settings', self.show_settings)
        
        # Пользователи
        self.hotkey_manager.register_callback('new_user', self.open_create_user)
        self.hotkey_manager.register_callback('user_list', self.open_employee_list)
        self.hotkey_manager.register_callback('edit_user', self.open_edit_user)
        
        # Группы
        self.hotkey_manager.register_callback('groups', self.open_group_management)
        
        # Календари
        self.hotkey_manager.register_callback('sputnik_calendar', self.open_sputnik_calendar)
        self.hotkey_manager.register_callback('calendars', self.open_calendar_management)
        
        # Документы
        self.hotkey_manager.register_callback('documents', self.open_document_management)
        
        # Темы
        self.hotkey_manager.register_callback('theme_light', lambda: theme_manager.set_theme('light'))
        self.hotkey_manager.register_callback('theme_dark', lambda: theme_manager.set_theme('dark'))
        self.hotkey_manager.register_callback('theme_blue', lambda: theme_manager.set_theme('blue'))
        
        # Служебные
        self.hotkey_manager.register_callback('help', self.show_help)
        self.hotkey_manager.register_callback('about', self.show_about)
        self.hotkey_manager.register_callback('quit', self.quit_application)

    # Методы для открытия окон с декораторами обработки ошибок
    @handle_service_errors("открытие списка сотрудников")
    def open_employee_list(self):
        """Открытие окна списка сотрудников"""
        window = EmployeeListWindow(self, self.service)

    @handle_service_errors("открытие окна создания пользователя")
    def open_create_user(self):
        """Открытие окна создания пользователя"""
        window = CreateUserWindow(self, self.service)

    @handle_service_errors("открытие окна редактирования пользователя")
    @validate_email
    def open_edit_user(self):
        """Открытие окна редактирования пользователя"""
        # Запрашиваем email пользователя
        user_email = simpledialog.askstring(
            'Редактирование пользователя',
            'Введите email пользователя для редактирования:'
        )
        
        if user_email:
            window = EditUserWindow(self, self.service, user_email)
            return f"Открыто окно редактирования пользователя: {user_email}"

    @handle_service_errors("открытие окна управления группами")
    def open_group_management(self):
        """Открытие окна управления группами"""
        window = GroupManagementWindow(self, self.service)

    @handle_ui_errors("открытие окна управления календарями")
    def open_calendar_management(self):
        """Открытие окна управления календарями"""
        window = open_calendar_management(self, self.service)

    @handle_ui_errors("открытие окна календаря SPUTНIK")
    def open_sputnik_calendar(self):
        """Открытие окна управления календарем SPUTНIK (общий)"""
        window = open_sputnik_calendar_window(self)
        if window:
            self.activity_log.add_entry("🎯 Открыт календарь SPUTНIK (общий)")
        return window

    @handle_ui_errors("открытие окна управления документами")
    def open_document_management(self):
        """Открытие окна управления доступом к документам"""
        try:
            # Проверяем, что сервис инициализирован
            if not self.service:
                messagebox.showerror("Ошибка", "Google API сервис не инициализирован")
                return
            
            # Получаем credentials из сервиса
            google_client = None
            
            # Попробуем получить клиент через user_service
            if hasattr(self.service, 'user_service') and self.service.user_service:
                user_repo = self.service.user_service.user_repo
                if hasattr(user_repo, 'client'):
                    google_client = user_repo.client
            
            # Если не получилось, попробуем через service adapter
            if not google_client and hasattr(self.service, 'user_repository'):
                if hasattr(self.service.user_repository, 'client'):
                    google_client = self.service.user_repository.client
            
            # Последняя попытка - создаем новый клиент
            if not google_client:
                from src.api.google_api_client import GoogleAPIClient
                from src.config.enhanced_config import config
                google_client = GoogleAPIClient(config.settings.google_application_credentials)
                if not google_client.initialize():
                    messagebox.showerror("Ошибка", "Не удалось инициализировать Google API клиент")
                    return
            
            # Получаем credentials
            credentials = google_client.get_credentials()
            if not credentials:
                messagebox.showerror("Ошибка", "Не удалось получить учетные данные Google API")
                return
            
            # Создаем сервис для документов (используем настоящий DocumentService)
            from src.services.document_service import DocumentService
            
            document_service = DocumentService(credentials)
            
            # Открываем окно с предустановленным URL
            default_url = "https://docs.google.com/document/d/1iXos0bTHv3nwXcYvAjPSIYzQOflcygwjj4LKD5Rftdk/edit#heading=h.mfzrrwzcspx2"
            window = open_document_management(self, document_service, default_url)
            if window:
                self.activity_log.add_entry("📄 Открыто управление документами")
            return window
                
        except Exception as e:
            self.logger.error(f"Ошибка при открытии окна управления документами: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть окно управления документами: {e}")

    @handle_ui_errors("открытие окна приглашения в Asana")
    def open_asana_invite(self):
        """Открытие окна приглашения в Asana"""
        window = AsanaInviteWindow(self)

    @handle_ui_errors("открытие окна журнала ошибок")
    def open_error_log(self):
        """Открытие окна журнала ошибок"""
        window = ErrorLogWindow(self)

    @handle_service_errors("экспорт списка пользователей", True)
    @measure_performance
    def export_users(self):
        """Экспорт списка пользователей в файл"""
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
            
            messagebox.showinfo('Успех', f'Список пользователей сохранен в {filename}')
            return f"Экспорт пользователей завершен: {filename}"

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

    @log_operation("Приложение готово к работе", "SUCCESS")
    def _delayed_init(self):
        """Отложенная инициализация после создания UI"""
        self._ui_initialized = True
        
        # Теперь, когда UI создан, можем проверить статус сервиса
        self.check_service_status()
        
        # Загружаем статистику
        self.load_statistics()

    def apply_theme(self):
        """Применение текущей темы ко всем элементам"""
        if not theme_manager.current_theme:
            return
            
        theme = theme_manager.current_theme
        
        # Применяем к основному окну
        self.config(bg=theme.get_color('background'))
        
        # Применяем к компонентам (если они созданы)
        if hasattr(self, 'header_frame'):
            self.header_frame.config(bg=theme.get_color('accent'))
            
        if hasattr(self, 'title_label'):
            self.title_label.config(
                bg=theme.get_color('accent'),
                fg=theme.get_color('text_accent')
            )
            
        if hasattr(self, 'status_frame'):
            self.status_frame.config(bg=theme.get_color('secondary'))
            
        if hasattr(self, 'status_label'):
            self.status_label.config(
                bg=theme.get_color('secondary'),
                fg=theme.get_color('text_primary')
            )
            
        # Обновляем компоненты
        if hasattr(self, 'statistics_panel') and self.statistics_panel:
            self.statistics_panel.apply_theme()
            
        if hasattr(self, 'activity_log') and self.activity_log:
            self.activity_log.apply_theme()
            
        if hasattr(self, 'toolbar') and self.toolbar:
            # Если есть метод apply_theme у toolbar
            if hasattr(self.toolbar, 'apply_theme'):
                self.toolbar.apply_theme()

    def on_theme_changed(self, theme):
        """Обработчик изменения темы"""
        self.apply_theme()
        self.log_activity(f'Тема изменена на: {theme.name}', 'INFO')

    def _load_theme_preferences(self):
        """Загрузка настроек темы"""
        import os
        config_path = os.path.join(os.path.expanduser('~'), '.admin_tools_config.json')
        theme_manager.load_theme_preference(config_path)

    def _save_theme_preferences(self):
        """Сохранение настроек темы"""
        import os
        config_path = os.path.join(os.path.expanduser('~'), '.admin_tools_config.json')
        theme_manager.save_theme_preference(config_path)

    def refresh_data(self):
        """Обновление всех данных"""
        self.load_statistics()
        self.log_activity('Данные обновлены', 'INFO')

    def show_settings(self):
        """Показать окно настроек"""
        messagebox.showinfo('Настройки', 'Окно настроек в разработке.\n\nИспользуйте:\n• Меню "Вид" → "Тема" для смены темы\n• F1 для справки по горячим клавишам')

    def show_help(self):
        """Показать справку"""
        self.hotkey_manager.show_help_dialog()

    def show_about(self):
        """Показать информацию о программе"""
        about_text = """Admin Team Tools v2.0.5

Приложение для управления пользователями Google Workspace.

🚀 Возможности:
• Управление пользователями и группами
• Экспорт данных в Excel
• Система тем (светлая, тёмная, синяя)
• Горячие клавиши для быстрой работы
• Централизованное логирование

⌨️ Горячие клавиши:
• F1 - справка по всем клавишам
• Ctrl+U - список пользователей
• Ctrl+G - управление группами
• Ctrl+E - экспорт данных
• Ctrl+1/2/3 - смена темы

© 2024 Admin Team Tools"""
        messagebox.showinfo('О программе', about_text)

    def quit_application(self):
        """Корректный выход из приложения"""
        self._save_theme_preferences()
        self.destroy()

def open_document_management(parent, document_service, default_url=None):
    """Функция для открытия окна управления документами (избегаем циклических импортов)"""
    from src.ui.document_management import DocumentManagementWindow
    return DocumentManagementWindow(parent, document_service, default_url)
