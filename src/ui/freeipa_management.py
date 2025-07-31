# -*- coding: utf-8 -*-
"""
Окно управления FreeIPA интеграцией.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path

from .ui_components import ModernColors, ModernButton, center_window

# Условный импорт FreeIPA модулей
try:
    from ..services.freeipa_client import FreeIPAConfig, FreeIPAService, create_freeipa_config_template
    from ..integrations.freeipa_integration import FreeIPAIntegration, setup_freeipa_integration
    FREEIPA_MODULES_AVAILABLE = True
except ImportError as e:
    # Заглушки для случая, когда FreeIPA недоступен
    FreeIPAConfig = object
    FreeIPAService = object
    FreeIPAIntegration = object
    create_freeipa_config_template = lambda: None
    setup_freeipa_integration = lambda: None
    FREEIPA_MODULES_AVAILABLE = False
    FREEIPA_IMPORT_ERROR = str(e)

from ..utils.simple_utils import async_manager, error_handler, SimpleProgressDialog
from .modern_styles import (ModernWindowConfig, CompactFrame, CompactLabel, 
                           CompactEntry, CompactButton, apply_modern_window_style, 
                           create_title_section, center_window_modern)


logger = logging.getLogger(__name__)


class FreeIPAManagementWindow(tk.Toplevel):
    """Окно управления FreeIPA интеграцией"""
    
    def __init__(self, parent, user_service=None, group_service=None):
        super().__init__(parent)
        
        self.user_service = user_service
        self.group_service = group_service
        self.freeipa_integration: Optional[FreeIPAIntegration] = None
        self.config: Optional[FreeIPAConfig] = None
        
        self._setup_window()
        self._create_ui()
        self._load_config()
        
    def _setup_window(self):
        """Настройка окна с компактным дизайном"""
        self.title("🔗 FreeIPA Интеграция")
        apply_modern_window_style(self, 'freeipa_management')
        
        # Центрирование окна
        center_window_modern(self, self.master if hasattr(self, 'master') else None)
        
        # Установка модальности
        self.transient(self.master)
        self.grab_set()
        
    def _create_ui(self):
        """Создание пользовательского интерфейса с компактным дизайном"""
        # Заголовок
        title_frame = create_title_section(self, "🔗 FreeIPA Интеграция")
        title_frame.pack(fill='x', **ModernWindowConfig.PADDING['window'])
        
        # Основной контейнер (компактный)
        main_frame = CompactFrame(self, padding_type='section')
        main_frame.pack(fill='both', expand=True, **ModernWindowConfig.PADDING['window'])
        
        # Notebook для вкладок (компактный)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(5, 0))
        
        # Вкладки
        self._create_connection_tab()
        self._create_sync_tab()
        self._create_stats_tab()
        self._create_settings_tab()
        
    def _create_header(self, parent):
        """Создание заголовка"""
        header_frame = tk.Frame(parent, bg=ModernColors.BACKGROUND)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Заголовок
        title_label = tk.Label(
            header_frame,
            text="🔗 FreeIPA Интеграция",
            font=('Arial', 16, 'bold'),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        )
        title_label.pack(side='left')
        
        # Статус подключения
        self.connection_status = tk.Label(
            header_frame,
            text="❌ Не подключен",
            font=('Arial', 10),
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.ERROR
        )
        self.connection_status.pack(side='right')
        
    def _create_connection_tab(self):
        """Вкладка подключения"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🔌 Подключение")
        
        # Скроллируемый фрейм
        canvas = tk.Canvas(tab_frame, bg=ModernColors.BACKGROUND)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernColors.BACKGROUND)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Конфигурация сервера
        config_frame = tk.LabelFrame(
            scrollable_frame,
            text="Конфигурация сервера",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        )
        config_frame.pack(fill='x', padx=10, pady=10)
        
        # Поля конфигурации
        tk.Label(config_frame, text="URL сервера:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.server_url_var = tk.StringVar()
        self.server_url_entry = tk.Entry(config_frame, textvariable=self.server_url_var, width=50)
        self.server_url_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Label(config_frame, text="Домен:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.domain_var = tk.StringVar()
        self.domain_entry = tk.Entry(config_frame, textvariable=self.domain_var, width=50)
        self.domain_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Label(config_frame, text="Пользователь:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(config_frame, textvariable=self.username_var, width=50)
        self.username_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Label(config_frame, text="Пароль:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(config_frame, textvariable=self.password_var, width=50, show='*')
        self.password_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        config_frame.columnconfigure(1, weight=1)
        
        # Дополнительные настройки
        advanced_frame = tk.LabelFrame(
            scrollable_frame,
            text="Дополнительные настройки",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        )
        advanced_frame.pack(fill='x', padx=10, pady=10)
        
        self.use_kerberos_var = tk.BooleanVar()
        tk.Checkbutton(
            advanced_frame,
            text="Использовать Kerberos аутентификацию",
            variable=self.use_kerberos_var,
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w', padx=5, pady=5)
        
        self.verify_ssl_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            advanced_frame,
            text="Проверять SSL сертификаты",
            variable=self.verify_ssl_var,
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w', padx=5, pady=5)
        
        # Кнопки управления
        buttons_frame = tk.Frame(scrollable_frame, bg=ModernColors.BACKGROUND)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        ModernButton(
            buttons_frame,
            text="💾 Сохранить конфигурацию",
            command=self._save_config,
            style='success'
        ).pack(side='left', padx=(0, 5))
        
        ModernButton(
            buttons_frame,
            text="📁 Загрузить конфигурацию",
            command=self._load_config_from_file,
            style='secondary'
        ).pack(side='left', padx=5)
        
        ModernButton(
            buttons_frame,
            text="🧪 Тестировать подключение",
            command=self._test_connection,
            style='primary'
        ).pack(side='left', padx=5)
        
        ModernButton(
            buttons_frame,
            text="🔌 Подключиться",
            command=self._connect_to_freeipa,
            style='success'
        ).pack(side='right')
        
    def _create_sync_tab(self):
        """Вкладка управления группами"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="👥 Пользователи и группы")
        
        main_sync_frame = tk.Frame(tab_frame, bg=ModernColors.BACKGROUND)
        main_sync_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Информационное сообщение
        info_frame = tk.Frame(main_sync_frame, bg=ModernColors.INFO, relief='raised', bd=1)
        info_frame.pack(fill='x', pady=(0, 10))
        
        info_label = tk.Label(
            info_frame,
            text="ℹ️ Этот модуль предназначен для управления пользователями и групп FreeIPA.",
            bg=ModernColors.INFO,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 9),
            justify='left'
        )
        info_label.pack(padx=10, pady=8)
        
        # Управление пользователями
        users_frame = tk.LabelFrame(
            main_sync_frame,
            text="Управление пользователями",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        )
        users_frame.pack(fill='x', pady=10)
        
        # Создание нового пользователя
        create_user_frame = tk.Frame(users_frame, bg=ModernColors.BACKGROUND)
        create_user_frame.pack(fill='x', padx=10, pady=10)
        
        # Первая строка: Основная информация
        user_main_frame = tk.Frame(create_user_frame, bg=ModernColors.BACKGROUND)
        user_main_frame.pack(fill='x', pady=(0, 5))
        
        tk.Label(user_main_frame, text="Логин:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(side='left')
        self.new_user_uid_var = tk.StringVar()
        user_uid_entry = tk.Entry(user_main_frame, textvariable=self.new_user_uid_var, width=15)
        user_uid_entry.pack(side='left', padx=(10, 0))
        
        tk.Label(user_main_frame, text="Имя:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(side='left', padx=(20, 0))
        self.new_user_givenname_var = tk.StringVar()
        user_givenname_entry = tk.Entry(user_main_frame, textvariable=self.new_user_givenname_var, width=15)
        user_givenname_entry.pack(side='left', padx=(10, 0))
        
        tk.Label(user_main_frame, text="Фамилия:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(side='left', padx=(20, 0))
        self.new_user_sn_var = tk.StringVar()
        user_sn_entry = tk.Entry(user_main_frame, textvariable=self.new_user_sn_var, width=15)
        user_sn_entry.pack(side='left', padx=(10, 0))
        
        # Вторая строка: Email и пароль
        user_details_frame = tk.Frame(create_user_frame, bg=ModernColors.BACKGROUND)
        user_details_frame.pack(fill='x', pady=(0, 5))
        
        tk.Label(user_details_frame, text="Email:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(side='left')
        self.new_user_email_var = tk.StringVar()
        user_email_entry = tk.Entry(user_details_frame, textvariable=self.new_user_email_var, width=25)
        user_email_entry.pack(side='left', padx=(10, 0))
        
        tk.Label(user_details_frame, text="Пароль:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(side='left', padx=(20, 0))
        self.new_user_password_var = tk.StringVar()
        user_password_entry = tk.Entry(user_details_frame, textvariable=self.new_user_password_var, width=20, show='*')
        user_password_entry.pack(side='left', padx=(10, 0))
        
        # Третья строка: Дополнительная информация
        user_extra_frame = tk.Frame(create_user_frame, bg=ModernColors.BACKGROUND)
        user_extra_frame.pack(fill='x', pady=(0, 5))
        
        tk.Label(user_extra_frame, text="Должность:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(side='left')
        self.new_user_title_var = tk.StringVar()
        user_title_entry = tk.Entry(user_extra_frame, textvariable=self.new_user_title_var, width=20)
        user_title_entry.pack(side='left', padx=(10, 0))
        
        tk.Label(user_extra_frame, text="Отдел:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(side='left', padx=(20, 0))
        self.new_user_department_var = tk.StringVar()
        user_department_entry = tk.Entry(user_extra_frame, textvariable=self.new_user_department_var, width=20)
        user_department_entry.pack(side='left', padx=(10, 0))
        
        # Кнопка создания пользователя
        user_button_frame = tk.Frame(create_user_frame, bg=ModernColors.BACKGROUND)
        user_button_frame.pack(fill='x', pady=(5, 0))
        
        ModernButton(
            user_button_frame,
            text="👤 Создать пользователя",
            command=self._create_user,
            style='success'
        ).pack(side='right')
        
        ModernButton(
            user_button_frame,
            text="🔄 Очистить поля",
            command=self._clear_user_fields,
            style='secondary'
        ).pack(side='right', padx=(0, 10))

        # Управление группами
        groups_frame = tk.LabelFrame(
            main_sync_frame,
            text="Управление группами",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        )
        groups_frame.pack(fill='x', pady=10)
        
        # Создание новой группы
        create_group_frame = tk.Frame(groups_frame, bg=ModernColors.BACKGROUND)
        create_group_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(create_group_frame, text="Название группы:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(side='left')
        self.new_group_name_var = tk.StringVar()
        group_name_entry = tk.Entry(create_group_frame, textvariable=self.new_group_name_var, width=20)
        group_name_entry.pack(side='left', padx=(10, 0))
        
        tk.Label(create_group_frame, text="Описание:", bg=ModernColors.BACKGROUND, fg=ModernColors.TEXT_PRIMARY).pack(side='left', padx=(20, 0))
        self.new_group_desc_var = tk.StringVar()
        group_desc_entry = tk.Entry(create_group_frame, textvariable=self.new_group_desc_var, width=30)
        group_desc_entry.pack(side='left', padx=(10, 0))
        
        ModernButton(
            create_group_frame,
            text="✨ Создать группу",
            command=self._create_group,
            style='success'
        ).pack(side='right')
        
        # Операции с группами
        groups_buttons_frame = tk.Frame(groups_frame, bg=ModernColors.BACKGROUND)
        groups_buttons_frame.pack(fill='x', padx=10, pady=10)
        
        ModernButton(
            groups_buttons_frame,
            text=" Получить группы FreeIPA",
            command=self._get_freeipa_groups,
            style='info'
        ).pack(side='left')
        
        ModernButton(
            groups_buttons_frame,
            text="🆕 Создать группу",
            command=self._create_group,
            style='success'
        ).pack(side='left', padx=(10, 0))
        
        # Список групп FreeIPA
        groups_list_frame = tk.LabelFrame(
            main_sync_frame,
            text="Группы FreeIPA",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        )
        groups_list_frame.pack(fill='both', expand=True, pady=10)
        
        # Фрейм для кнопок управления списком групп
        groups_controls_frame = tk.Frame(groups_list_frame, bg=ModernColors.BACKGROUND)
        groups_controls_frame.pack(fill='x', padx=10, pady=(5, 0))
        
        ModernButton(
            groups_controls_frame,
            text="🔄 Обновить список",
            command=self._refresh_groups_list,
            style='primary'
        ).pack(side='left')
        
        tk.Label(
            groups_controls_frame,
            text="Всего групп: ",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 9)
        ).pack(side='right')
        
        self.groups_count_label = tk.Label(
            groups_controls_frame,
            text="0",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 9, 'bold')
        )
        self.groups_count_label.pack(side='right')
        
        # Создаем фрейм для Treeview и скроллбара
        groups_tree_frame = tk.Frame(groups_list_frame, bg=ModernColors.BACKGROUND)
        groups_tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Настраиваем стиль для Treeview
        style = ttk.Style()
        style.configure("Groups.Treeview", background=ModernColors.SURFACE, 
                       foreground=ModernColors.TEXT_PRIMARY, fieldbackground=ModernColors.SURFACE)
        style.configure("Groups.Treeview.Heading", background=ModernColors.PRIMARY, 
                       foreground="white", font=('Arial', 9, 'bold'))
        
        # Создаем Treeview для отображения групп
        columns = ('name', 'description', 'members_count')
        self.groups_tree = ttk.Treeview(
            groups_tree_frame,
            columns=columns,
            show='headings',
            style="Groups.Treeview",
            height=8
        )
        
        # Настраиваем заголовки столбцов
        self.groups_tree.heading('name', text='Название группы')
        self.groups_tree.heading('description', text='Описание')
        self.groups_tree.heading('members_count', text='Участников')
        
        # Настраиваем ширину столбцов
        self.groups_tree.column('name', width=200, minwidth=150)
        self.groups_tree.column('description', width=300, minwidth=200)
        self.groups_tree.column('members_count', width=100, minwidth=80)
        
        # Добавляем Treeview в фрейм
        self.groups_tree.pack(side='left', fill='both', expand=True)
        
        # Добавляем скроллбар для Treeview
        groups_scrollbar = ttk.Scrollbar(groups_tree_frame, orient="vertical", command=self.groups_tree.yview)
        self.groups_tree.configure(yscrollcommand=groups_scrollbar.set)
        groups_scrollbar.pack(side="right", fill="y")
        
        # Привязываем обработчик двойного клика для детальной информации о группе
        self.groups_tree.bind('<Double-1>', self._on_group_double_click)
        
        # Результаты синхронизации
        results_frame = tk.LabelFrame(
            main_sync_frame,
            text="Результаты синхронизации",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        )
        results_frame.pack(fill='both', expand=True, pady=10)
        
        # Текстовое поле для результатов
        self.results_text = tk.Text(
            results_frame,
            height=10,
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Consolas', 9)
        )
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Скроллбар для результатов
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        results_scrollbar.pack(side="right", fill="y")
        
    def _create_stats_tab(self):
        """Вкладка статистики"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📊 Статистика")
        
        stats_frame = tk.Frame(tab_frame, bg=ModernColors.BACKGROUND)
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Кнопки управления
        controls_frame = tk.Frame(stats_frame, bg=ModernColors.BACKGROUND)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        ModernButton(
            controls_frame,
            text="🔄 Обновить статистику",
            command=self._refresh_stats,
            style='primary'
        ).pack(side='left')
        
        ModernButton(
            controls_frame,
            text="� Сравнить группы",
            command=self._compare_groups,
            style='info'
        ).pack(side='left', padx=(10, 0))
        
        # Статистика
        self.stats_text = tk.Text(
            stats_frame,
            bg=ModernColors.SURFACE,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Consolas', 10)
        )
        self.stats_text.pack(fill='both', expand=True)
        
        # Скроллбар для статистики
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        stats_scrollbar.pack(side="right", fill="y")
        
    def _create_settings_tab(self):
        """Вкладка настроек"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="⚙️ Настройки")
        
        settings_frame = tk.Frame(tab_frame, bg=ModernColors.BACKGROUND)
        settings_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Логирование
        logging_frame = tk.LabelFrame(
            settings_frame,
            text="Настройки логирования",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        )
        logging_frame.pack(fill='x', pady=10)
        
        self.detailed_logging_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            logging_frame,
            text="Подробное логирование операций FreeIPA",
            variable=self.detailed_logging_var,
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w', padx=10, pady=5)
        
        # Управление данными
        data_frame = tk.LabelFrame(
            settings_frame,
            text="Управление данными",
            bg=ModernColors.BACKGROUND,
            fg=ModernColors.TEXT_PRIMARY,
            font=('Arial', 10, 'bold')
        )
        data_frame.pack(fill='x', pady=10)
        
        data_buttons_frame = tk.Frame(data_frame, bg=ModernColors.BACKGROUND)
        data_buttons_frame.pack(fill='x', padx=10, pady=10)
        
        ModernButton(
            data_buttons_frame,
            text="📤 Экспорт настроек",
            command=self._export_settings,
            style='secondary'
        ).pack(side='left')
        
        ModernButton(
            data_buttons_frame,
            text="📥 Импорт настроек",
            command=self._import_settings,
            style='secondary'
        ).pack(side='left', padx=(10, 0))
        
        ModernButton(
            data_buttons_frame,
            text="🗑️ Сброс настроек",
            command=self._reset_settings,
            style='danger'
        ).pack(side='right')
        
    # === Методы обработки событий ===
    
    def _load_config(self):
        """Загрузка конфигурации из файла"""
        config_path = Path("config/freeipa_config.json")
        template_path = Path("config/freeipa_config_template.json")
        
        if config_path.exists():
            try:
                self.config = FreeIPAConfig.from_file(str(config_path))
                self._update_ui_from_config()
                self._log_result("✅ Конфигурация загружена из файла")
                return
            except Exception as e:
                self._log_result(f"❌ Ошибка загрузки конфигурации: {e}")
        
        # Если основного файла нет, попробуем шаблон
        if template_path.exists():
            try:
                self.config = FreeIPAConfig.from_file(str(template_path))
                self._update_ui_from_config()
                self._log_result("ℹ️ Загружен шаблон конфигурации")
                return
            except Exception as e:
                self._log_result(f"❌ Ошибка загрузки шаблона: {e}")
        
        # Если ничего нет, устанавливаем значения по умолчанию
        self._update_ui_from_config()
        self._log_result("ℹ️ Установлены значения по умолчанию для sputnik8")
    
    def _update_ui_from_config(self):
        """Обновление UI из конфигурации"""
        if self.config:
            self.server_url_var.set(self.config.server_url)
            self.domain_var.set(self.config.domain)
            self.username_var.set(self.config.username or "")
            self.password_var.set(self.config.password or "")
            self.use_kerberos_var.set(self.config.use_kerberos)
            self.verify_ssl_var.set(self.config.verify_ssl)
        else:
            # Устанавливаем значения по умолчанию для sputnik8
            self.server_url_var.set("https://ipa001.infra.int.sputnik8.com/")
            self.domain_var.set("infra.int.sputnik8.com")
            self.use_kerberos_var.set(False)
            self.verify_ssl_var.set(False)
    
    def _save_config(self):
        """Сохранение конфигурации"""
        try:
            config = FreeIPAConfig(
                server_url=self.server_url_var.get().strip(),
                domain=self.domain_var.get().strip(),
                username=self.username_var.get().strip() or None,
                password=self.password_var.get().strip() or None,
                use_kerberos=self.use_kerberos_var.get(),
                verify_ssl=self.verify_ssl_var.get()
            )
            
            # Создаем директорию если не существует
            config_path = Path("config/freeipa_config.json")
            config_path.parent.mkdir(exist_ok=True)
            
            config.to_file(str(config_path))
            self.config = config
            self._log_result("✅ Конфигурация сохранена")
            
        except Exception as e:
            self._log_result(f"❌ Ошибка сохранения конфигурации: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить конфигурацию: {e}")
    
    def _load_config_from_file(self):
        """Загрузка конфигурации из выбранного файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл конфигурации",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.config = FreeIPAConfig.from_file(file_path)
                self._update_ui_from_config()
                self._log_result(f"✅ Конфигурация загружена из {file_path}")
            except Exception as e:
                self._log_result(f"❌ Ошибка загрузки конфигурации: {e}")
                messagebox.showerror("Ошибка", f"Не удалось загрузить конфигурацию: {e}")
    
    def _test_connection(self):
        """Тестирование подключения"""
        if not self._validate_config():
            return
        
        self._save_config()  # Сохраняем перед тестированием
        
        async def test_async():
            try:
                service = FreeIPAService(self.config)
                if service.connect():
                    self._log_result("✅ Подключение к FreeIPA успешно")
                    self.connection_status.config(text="✅ Подключен", fg=ModernColors.SUCCESS)
                    service.disconnect()
                    return True
                else:
                    self._log_result("❌ Ошибка подключения к FreeIPA")
                    self.connection_status.config(text="❌ Ошибка подключения", fg=ModernColors.ERROR)
                    return False
            except Exception as e:
                self._log_result(f"❌ Ошибка тестирования: {e}")
                self.connection_status.config(text="❌ Ошибка", fg=ModernColors.ERROR)
                return False
        
        # Запускаем асинхронно
        async_manager.run_async(test_async)
    
    def _connect_to_freeipa(self):
        """Подключение к FreeIPA"""
        if not self._validate_config():
            return
        
        self._save_config()
        
        async def connect_async():
            try:
                if self.user_service and self.group_service:
                    self.freeipa_integration = FreeIPAIntegration(self.user_service, self.group_service)
                    
                    if self.freeipa_integration.load_config():
                        if await self.freeipa_integration.connect():
                            self._log_result("✅ Подключение к FreeIPA установлено")
                            self.connection_status.config(text="✅ Подключен", fg=ModernColors.SUCCESS)
                            
                            # Автоматически загружаем список групп при успешном подключении
                            self._log_result("🔄 Загрузка списка групп...")
                            self._refresh_groups_list()
                            
                            return True
                        else:
                            self._log_result("❌ Не удалось подключиться к FreeIPA")
                            self.connection_status.config(text="❌ Не подключен", fg=ModernColors.ERROR)
                    else:
                        self._log_result("❌ Ошибка загрузки конфигурации")
                else:
                    self._log_result("❌ Сервисы Google Workspace не доступны")
                    
            except Exception as e:
                self._log_result(f"❌ Ошибка подключения: {e}")
                self.connection_status.config(text="❌ Ошибка", fg=ModernColors.ERROR)
        
        async_manager.run_async(connect_async)
    
    def _validate_config(self):
        """Валидация конфигурации"""
        if not self.server_url_var.get().strip():
            messagebox.showerror("Ошибка", "Укажите URL сервера")
            return False
        
        if not self.domain_var.get().strip():
            messagebox.showerror("Ошибка", "Укажите домен")
            return False
        
        if not self.use_kerberos_var.get():
            if not self.username_var.get().strip():
                messagebox.showerror("Ошибка", "Укажите имя пользователя")
                return False
            
            if not self.password_var.get().strip():
                messagebox.showerror("Ошибка", "Укажите пароль")
                return False
        
        return True
    
    def _create_group(self):
        """Создание новой группы в FreeIPA"""
        group_name = self.new_group_name_var.get().strip()
        if not group_name:
            messagebox.showerror("Ошибка", "Укажите название группы")
            return
        
        if not self.freeipa_integration:
            messagebox.showerror("Ошибка", "Сначала подключитесь к FreeIPA")
            return
        
        async def create_group_async():
            try:
                description = self.new_group_desc_var.get().strip() or f"Группа {group_name}"
                self._log_result(f"✨ Создание группы {group_name}...")
                
                # Создаем группу через FreeIPA клиент
                result = await self.freeipa_integration.freeipa_client.create_group(group_name, description)
                
                if result:
                    self._log_result(f"✅ Группа {group_name} создана")
                    # Очищаем поля
                    self.new_group_name_var.set("")
                    self.new_group_desc_var.set("")
                else:
                    self._log_result(f"❌ Ошибка создания группы {group_name}")
                    
            except Exception as e:
                self._log_result(f"❌ Ошибка создания группы: {e}")
        
        async_manager.run_async(create_group_async)
    
    def _create_user(self):
        """Создание нового пользователя в FreeIPA"""
        # Проверяем обязательные поля
        uid = self.new_user_uid_var.get().strip()
        givenname = self.new_user_givenname_var.get().strip()
        sn = self.new_user_sn_var.get().strip()
        
        if not uid:
            messagebox.showerror("Ошибка", "Укажите логин пользователя")
            return
        
        if not givenname:
            messagebox.showerror("Ошибка", "Укажите имя пользователя")
            return
            
        if not sn:
            messagebox.showerror("Ошибка", "Укажите фамилию пользователя")
            return
        
        # Проверяем email если указан
        email = self.new_user_email_var.get().strip()
        if email and '@' not in email:
            messagebox.showerror("Ошибка", "Укажите корректный email адрес")
            return
        
        if not self.freeipa_integration:
            messagebox.showerror("Ошибка", "Сначала подключитесь к FreeIPA")
            return
        
        # Подтверждение создания
        if not messagebox.askyesno("Подтверждение", 
                                  f"Создать пользователя '{uid}' ({givenname} {sn})?"):
            return
        
        async def create_user_async():
            try:
                # Получаем данные из полей
                password = self.new_user_password_var.get().strip()
                title = self.new_user_title_var.get().strip()
                department = self.new_user_department_var.get().strip()
                
                self._log_result(f"👤 Создание пользователя {uid}...")
                
                # Создаем объект пользователя FreeIPA
                from ..services.freeipa_client import FreeIPAUser
                
                freeipa_user = FreeIPAUser(
                    uid=uid,
                    givenname=givenname,
                    sn=sn,
                    mail=email if email else None,
                    userpassword=password if password else None,
                    title=title if title else None,
                    department=department if department else None
                )
                
                # Создаем пользователя через FreeIPA сервис
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self.freeipa_integration.freeipa_service.create_user,
                    freeipa_user
                )
                
                if result:
                    self._log_result(f"✅ Пользователь {uid} создан")
                    if email:
                        self._log_result(f"📧 Email: {email}")
                    if title:
                        self._log_result(f"💼 Должность: {title}")
                    if department:
                        self._log_result(f"🏢 Отдел: {department}")
                    
                    # Очищаем поля после успешного создания
                    self._clear_user_fields()
                    
                    messagebox.showinfo("Успех", f"Пользователь {uid} успешно создан в FreeIPA")
                else:
                    self._log_result(f"❌ Ошибка создания пользователя {uid}")
                    messagebox.showerror("Ошибка", f"Не удалось создать пользователя {uid}")
                    
            except Exception as e:
                self._log_result(f"❌ Ошибка создания пользователя: {e}")
                logger.error(f"Ошибка создания пользователя: {e}")
                messagebox.showerror("Ошибка", f"Ошибка при создании пользователя: {e}")
        
        async_manager.run_async(create_user_async)
    
    def _clear_user_fields(self):
        """Очистка полей создания пользователя"""
        self.new_user_uid_var.set("")
        self.new_user_givenname_var.set("")
        self.new_user_sn_var.set("")
        self.new_user_email_var.set("")
        self.new_user_password_var.set("")
        self.new_user_title_var.set("")
        self.new_user_department_var.set("")
    
    def _get_freeipa_groups(self):
        """Получение списка групп из FreeIPA и отображение их в результатах"""
        if not self.freeipa_integration:
            self._log_result("❌ Сначала подключитесь к FreeIPA")
            return
        
        # Сначала обновляем список групп в таблице
        self._refresh_groups_list()
            
        async def get_freeipa_groups_async():
            try:
                self._log_result("🔗 Получение групп из FreeIPA...")
                groups = await self.freeipa_integration.freeipa_client.get_groups()
                self._log_result(f"✅ Получено {len(groups)} групп из FreeIPA")
                
                # Показываем все пользовательские группы
                user_groups = []
                for group in groups:
                    if isinstance(group, dict):
                        group_name = group.get('cn', [group.get('group_name', 'Unknown')])[0] if isinstance(group.get('cn'), list) else group.get('cn', 'Unknown')
                    else:
                        group_name = str(group)
                    
                    # Исключаем только системные группы
                    system_groups = ['admins', 'editors', 'ipausers', 'trust admins', 'default smb group', 'domain admins', 'domain users']
                    if group_name.lower() not in [name.lower() for name in system_groups]:
                        user_groups.append(group_name)
                        self._log_result(f"  🔗 {group_name}")
                
                if not user_groups:
                    self._log_result("⚠️ Пользовательские группы не найдены")
                    self._log_result("� Убедитесь, что группы существуют в FreeIPA")
                    
            except Exception as e:
                self._log_result(f"❌ Ошибка получения групп FreeIPA: {e}")
        
        async_manager.run_async(get_freeipa_groups_async)
    
    def _refresh_stats(self):
        """Обновление статистики"""
        if not self.freeipa_integration:
            messagebox.showerror("Ошибка", "Сначала подключитесь к FreeIPA")
            return
        
        async def refresh_async():
            try:
                stats = await self.freeipa_integration.get_freeipa_stats()
                
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(tk.END, "📊 Статистика FreeIPA:\n")
                self.stats_text.insert(tk.END, "=" * 40 + "\n\n")
                
                if 'error' in stats:
                    self.stats_text.insert(tk.END, f"❌ Ошибка: {stats['error']}\n")
                else:
                    self.stats_text.insert(tk.END, f"🌐 Сервер: {stats['server_url']}\n")
                    self.stats_text.insert(tk.END, f"🏠 Домен: {stats['domain']}\n")
                    self.stats_text.insert(tk.END, f"🔗 Подключен: {'✅' if stats['connected'] else '❌'}\n")
                    # Убрано отображение пользователей - только группы
                    self.stats_text.insert(tk.END, f"📁 Групп: {stats['groups_count']}\n")
                
                self.stats_text.insert(tk.END, f"\n🕐 Обновлено: {datetime.now().strftime('%H:%M:%S')}\n")
                
            except Exception as e:
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(tk.END, f"❌ Ошибка получения статистики: {e}\n")
        
        async_manager.run_async(refresh_async)
    
    def _compare_groups(self):
        """Сравнение групп между Google Workspace и FreeIPA"""
        if not self.freeipa_integration:
            messagebox.showerror("Ошибка", "Сначала подключитесь к FreeIPA")
            return
        
        async def compare_async():
            try:
                self._log_result("🔍 Сравнение групп между Google Workspace и FreeIPA...")
                
                # Получаем группы из Google Workspace
                google_groups = []
                if self.group_service and hasattr(self.group_service, 'get_all_groups'):
                    google_groups = await self.group_service.get_all_groups()
                
                # Получаем группы из FreeIPA
                freeipa_groups = await self.freeipa_integration.freeipa_client.get_groups()
                
                # Создаем списки имен групп для сравнения
                google_group_names = set()
                for group in google_groups:
                    if isinstance(group, dict):
                        name = group.get('name', group.get('email', ''))
                        if name:
                            google_group_names.add(name.lower())
                
                freeipa_group_names = set()
                for group in freeipa_groups:
                    if isinstance(group, dict):
                        name = group.get('cn', [group.get('group_name', '')])[0]
                        if name:
                            freeipa_group_names.add(name.lower())
                    else:
                        freeipa_group_names.add(str(group).lower())
                
                # Анализ различий
                in_both = google_group_names & freeipa_group_names
                only_in_google = google_group_names - freeipa_group_names
                only_in_freeipa = freeipa_group_names - google_group_names
                
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(tk.END, "🔍 Сравнение групп:\n")
                self.stats_text.insert(tk.END, "=" * 40 + "\n\n")
                
                self.stats_text.insert(tk.END, f"📊 Google Workspace: {len(google_group_names)} групп\n")
                self.stats_text.insert(tk.END, f"📊 FreeIPA: {len(freeipa_group_names)} групп\n")
                self.stats_text.insert(tk.END, f"🔗 В обеих системах: {len(in_both)}\n")
                self.stats_text.insert(tk.END, f"🟢 Только в Google: {len(only_in_google)}\n")
                self.stats_text.insert(tk.END, f"🟡 Только в FreeIPA: {len(only_in_freeipa)}\n\n")
                
                if only_in_google:
                    self.stats_text.insert(tk.END, "� Группы только в Google (можно создать в FreeIPA):\n")
                    for group_name in sorted(list(only_in_google))[:15]:
                        self.stats_text.insert(tk.END, f"  📁 {group_name}\n")
                    if len(only_in_google) > 15:
                        self.stats_text.insert(tk.END, f"  ... и еще {len(only_in_google) - 15}\n")
                
                if only_in_freeipa:
                    self.stats_text.insert(tk.END, "\n� Группы только в FreeIPA:\n")
                    for group_name in sorted(list(only_in_freeipa))[:10]:
                        self.stats_text.insert(tk.END, f"  🔗 {group_name}\n")
                    if len(only_in_freeipa) > 10:
                        self.stats_text.insert(tk.END, f"  ... и еще {len(only_in_freeipa) - 10}\n")
                        
                self.stats_text.insert(tk.END, f"\n🕐 Обновлено: {datetime.now().strftime('%H:%M:%S')}\n")
                
            except Exception as e:
                self.stats_text.insert(tk.END, f"❌ Ошибка сравнения: {e}\n")
        
        async_manager.run_async(compare_async)
    
    def _export_settings(self):
        """Экспорт настроек"""
        file_path = filedialog.asksaveasfilename(
            title="Сохранить настройки",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path and self.config:
            try:
                self.config.to_file(file_path)
                self._log_result(f"✅ Настройки экспортированы в {file_path}")
            except Exception as e:
                self._log_result(f"❌ Ошибка экспорта: {e}")
                messagebox.showerror("Ошибка", f"Не удалось экспортировать настройки: {e}")
    
    def _import_settings(self):
        """Импорт настроек"""
        self._load_config_from_file()
    
    def _reset_settings(self):
        """Сброс настроек"""
        if messagebox.askyesno("Подтверждение", "Сбросить все настройки к значениям по умолчанию?"):
            self.server_url_var.set("")
            self.domain_var.set("")
            self.username_var.set("")
            self.password_var.set("")
            self.use_kerberos_var.set(False)
            self.verify_ssl_var.set(True)
            
            self._log_result("🔄 Настройки сброшены")
    
    def _refresh_groups_list(self):
        """Обновление списка групп FreeIPA"""
        if not self.freeipa_integration:
            self._log_result("❌ Сначала подключитесь к FreeIPA")
            messagebox.showwarning("Предупреждение", "Сначала подключитесь к FreeIPA")
            return
            
        async def refresh_groups_async():
            try:
                self._log_result("🔄 Обновление списка групп FreeIPA...")
                
                # Очищаем существующий список
                for item in self.groups_tree.get_children():
                    self.groups_tree.delete(item)
                
                # Получаем группы из FreeIPA
                groups = await self.freeipa_integration.freeipa_client.get_groups()
                
                if not groups:
                    self._log_result("⚠️ Группы не найдены")
                    self.groups_count_label.config(text="0")
                    return
                
                # Список системных групп, которые нужно исключить
                system_groups = [
                    'admins', 'editors', 'ipausers', 'trust admins',
                    'default smb group', 'domain admins', 'domain users'
                ]
                actual_groups = []
                
                # Заполняем список всеми пользовательскими группами
                for group in groups:
                    if isinstance(group, dict):
                        # Обрабатываем полную информацию о группе
                        group_name = group.get('cn', ['Неизвестно'])[0] if isinstance(group.get('cn'), list) else group.get('cn', 'Неизвестно')
                        description = group.get('description', [''])[0] if isinstance(group.get('description'), list) else group.get('description', '')
                        members = group.get('member', [])
                        members_count = len(members) if isinstance(members, list) else 0
                    else:
                        # Если это просто строка с именем группы
                        group_name = str(group)
                        description = ""
                        members_count = 0
                    
                    # Исключаем только системные группы
                    if group_name.lower() not in [name.lower() for name in system_groups]:
                        actual_groups.append(group)
                        # Добавляем в Treeview
                        self.groups_tree.insert('', 'end', values=(
                            group_name,
                            description,
                            members_count
                        ))
                
                # Обновляем счетчик групп
                self.groups_count_label.config(text=str(len(actual_groups)))
                if actual_groups:
                    self._log_result(f"✅ Загружено {len(actual_groups)} пользовательских групп из FreeIPA")
                    for group in actual_groups[:5]:  # Показываем первые 5 групп в логе
                        if isinstance(group, dict):
                            name = group.get('cn', ['Unknown'])[0] if isinstance(group.get('cn'), list) else group.get('cn', 'Unknown')
                        else:
                            name = str(group)
                        self._log_result(f"  🔗 {name}")
                    if len(actual_groups) > 5:
                        self._log_result(f"  ... и еще {len(actual_groups) - 5} групп")
                else:
                    self._log_result("⚠️ Пользовательские группы не найдены в FreeIPA")
                
            except Exception as e:
                self._log_result(f"❌ Ошибка обновления списка групп: {e}")
                self.groups_count_label.config(text="0")
        
        async_manager.run_async(refresh_groups_async)
    
    def _on_group_double_click(self, event):
        """Обработка двойного клика по группе"""
        selection = self.groups_tree.selection()
        if not selection:
            return
        
        item = self.groups_tree.item(selection[0])
        group_name = item['values'][0]
        
        # Показываем контекстное меню или детальную информацию
        self._show_group_context_menu(event, group_name)
    
    def _show_group_context_menu(self, event, group_name: str):
        """Показ контекстного меню для группы"""
        # Создаем контекстное меню
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(
            label="📋 Показать детали группы",
            command=lambda: self._show_group_details(group_name)
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="👥 Управление участниками",
            command=lambda: self._manage_group_members(group_name)
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="🔄 Обновить информацию",
            command=self._refresh_groups_list
        )
        
        # Показываем меню
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _manage_group_members(self, group_name: str):
        """Открытие окна управления участниками группы"""
        try:
            from .group_members_management import show_group_members_management
            
            # Получаем FreeIPA сервис
            freeipa_service = None
            if self.freeipa_integration and hasattr(self.freeipa_integration, 'freeipa_client'):
                freeipa_service = self.freeipa_integration.freeipa_client
            
            # Открываем окно управления участниками
            members_window = show_group_members_management(
                master=self,
                group_id=group_name,
                group_name=group_name,
                google_service=self.group_service,
                freeipa_service=freeipa_service
            )
            
            # Обновляем список групп после закрытия окна
            self.wait_window(members_window)
            self._refresh_groups_list()
            
        except Exception as e:
            self._log_result(f"❌ Ошибка открытия окна управления участниками: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть окно управления участниками: {e}")
    
    def _show_group_details(self, group_name: str):
        """Показ детальной информации о группе"""
        if not self.freeipa_integration:
            return
        
        async def get_group_details_async():
            try:
                self._log_result(f"🔍 Получение детальной информации о группе '{group_name}'...")
                
                # Получаем детальную информацию о группе
                group_info = await self.freeipa_integration.freeipa_client.get_group(group_name)
                
                if group_info:
                    details = f"""
📁 Группа: {group_name}
📄 Описание: {group_info.get('description', [''])[0] if isinstance(group_info.get('description'), list) else group_info.get('description', '')}
👥 Участников: {len(group_info.get('member', []))}
🏷️ GID: {group_info.get('gidnumber', [''])[0] if isinstance(group_info.get('gidnumber'), list) else group_info.get('gidnumber', '')}
📅 Создана: {group_info.get('ipauniqueid', [''])[0] if isinstance(group_info.get('ipauniqueid'), list) else group_info.get('ipauniqueid', '')}

👥 Участники:"""
                    
                    members = group_info.get('member', [])
                    if members:
                        for member in members[:10]:  # Показываем только первые 10
                            # Извлекаем имя пользователя из DN
                            if isinstance(member, str) and 'uid=' in member:
                                username = member.split('uid=')[1].split(',')[0]
                                details += f"\n  • {username}"
                            else:
                                details += f"\n  • {member}"
                        
                        if len(members) > 10:
                            details += f"\n  ... и еще {len(members) - 10} участников"
                    else:
                        details += "\n  (группа пуста)"
                    
                    # Показываем в отдельном окне
                    detail_window = tk.Toplevel(self)
                    detail_window.title(f"Детали группы: {group_name}")
                    detail_window.geometry("500x400")
                    detail_window.configure(bg=ModernColors.BACKGROUND)
                    
                    text_widget = tk.Text(
                        detail_window,
                        bg=ModernColors.SURFACE,
                        fg=ModernColors.TEXT_PRIMARY,
                        font=('Consolas', 10),
                        wrap='word'
                    )
                    text_widget.pack(fill='both', expand=True, padx=10, pady=10)
                    text_widget.insert('1.0', details)
                    text_widget.config(state='disabled')
                    
                    self._log_result(f"✅ Информация о группе '{group_name}' получена")
                else:
                    self._log_result(f"⚠️ Информация о группе '{group_name}' недоступна")
                    
            except Exception as e:
                self._log_result(f"❌ Ошибка получения информации о группе '{group_name}': {e}")
        
        async_manager.run_async(get_group_details_async)
    
    def _log_result(self, message: str):
        """Логирование результата в текстовое поле"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Проверяем, что виджет существует и не разрушен
        try:
            if hasattr(self, 'results_text') and self.results_text.winfo_exists():
                self.results_text.insert(tk.END, log_message)
                self.results_text.see(tk.END)
        except tk.TclError:
            # Виджет уже разрушен, просто игнорируем
            pass
        
        # Логируем также в logger
        logger.info(message)
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if self.freeipa_integration:
            async def disconnect_async():
                await self.freeipa_integration.disconnect()
            
            try:
                async_manager.run_async(disconnect_async)
            except:
                pass
        
        self.destroy()


def open_freeipa_management(parent, user_service=None, group_service=None):
    """Открытие окна управления FreeIPA"""
    # Проверяем доступность FreeIPA модулей
    if not FREEIPA_MODULES_AVAILABLE:
        from tkinter import messagebox
        
        error_msg = (
            "❌ FreeIPA модули недоступны\n\n"
            f"Ошибка импорта: {FREEIPA_IMPORT_ERROR}\n\n"
            "🔧 РЕШЕНИЯ:\n\n"
            "1️⃣ Если ошибка связана с Kerberos:\n"
            "   • Это нормально для Windows\n"
            "   • FreeIPA будет работать с логин/пароль\n"
            "   • Перезапустите приложение\n\n"
            "2️⃣ Если ошибка с зависимостями:\n"
            "   • pip install python-freeipa requests-kerberos\n\n"
            "💡 Проверьте: test_freeipa_connection.py"
        )
        
        messagebox.showerror("FreeIPA недоступен", error_msg)
        return None
    
    try:
        window = FreeIPAManagementWindow(parent, user_service, group_service)
        
        # Обработка закрытия окна
        window.protocol("WM_DELETE_WINDOW", window.on_closing)
        
        return window
    except Exception as e:
        logger.error(f"Ошибка открытия окна FreeIPA: {e}")
        
        # Специальная обработка ошибок Kerberos
        if "kerberos" in str(e).lower() or "kfw" in str(e).lower():
            from tkinter import messagebox
            messagebox.showwarning(
                "FreeIPA - Проблема с Kerberos",
                "❌ Ошибка инициализации Kerberos\n\n"
                "🔧 РЕШЕНИЕ:\n"
                "FreeIPA настроен для работы БЕЗ Kerberos\n"
                "Используйте обычную аутентификацию логин/пароль\n\n"
                "💡 Сервер готов: https://ipa001.infra.int.sputnik8.com/"
            )
        else:
            from tkinter import messagebox
            messagebox.showerror("Ошибка", f"Не удалось открыть окно FreeIPA: {e}")
        
        return None
