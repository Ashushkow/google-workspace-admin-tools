# -*- coding: utf-8 -*-
"""
Панель статистики для главного окна приложения.
"""

import tkinter as tk
from typing import Optional, Any, Callable

from ..ui_components import ModernColors, ModernButton
from ...api.users_api import get_user_list
from ...api.groups_api import list_groups


class StatisticsPanel(tk.Frame):
    """
    Панель статистики и быстрых действий.
    """
    
    def __init__(self, parent: tk.Widget, service: Optional[Any] = None, 
                 quick_actions_callbacks: Optional[dict] = None):
        super().__init__(parent, bg=ModernColors.CARD_BG, relief='solid', bd=1)
        
        self.service = service
        self.callbacks = quick_actions_callbacks or {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Настройка пользовательского интерфейса панели"""
        self.pack(side='left', fill='y', padx=(0, 8), pady=0, ipadx=10, ipady=10)
        
        self._create_statistics_section()
        self._create_quick_actions_section()
        
    def _create_statistics_section(self):
        """Создание секции статистики"""
        # Заголовок панели
        tk.Label(
            self,
            text='📊 Статистика',
            font=('Arial', 12, 'bold'),
            bg=ModernColors.CARD_BG,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 10))
        
        # Статистические карточки
        self.stats_frame = tk.Frame(self, bg=ModernColors.CARD_BG)
        self.stats_frame.pack(fill='x', pady=(0, 15))
        
        self.total_users_label = tk.Label(
            self.stats_frame,
            text='Пользователи: загрузка...',
            font=('Arial', 10),
            bg=ModernColors.CARD_BG,
            fg=ModernColors.TEXT_SECONDARY
        )
        self.total_users_label.pack(anchor='w', pady=1)
        
        self.total_groups_label = tk.Label(
            self.stats_frame,
            text='Группы: загрузка...',
            font=('Arial', 10),
            bg=ModernColors.CARD_BG,
            fg=ModernColors.TEXT_SECONDARY
        )
        self.total_groups_label.pack(anchor='w', pady=1)
        
    def _create_quick_actions_section(self):
        """Создание секции быстрых действий"""
        # Быстрые действия
        tk.Label(
            self,
            text='⚡ Действия',
            font=('Arial', 12, 'bold'),
            bg=ModernColors.CARD_BG,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(10, 8))
        
        quick_actions_frame = tk.Frame(self, bg=ModernColors.CARD_BG)
        quick_actions_frame.pack(fill='x')
        
        ModernButton(
            quick_actions_frame,
            text='📋 Экспорт',
            command=self.callbacks.get('export', self._no_callback),
            style='secondary',
            font=('Arial', 9)
        ).pack(fill='x', pady=1)
        
        ModernButton(
            quick_actions_frame,
            text='📁 Журнал',
            command=self.callbacks.get('error_log', self._no_callback),
            style='secondary',
            font=('Arial', 9)
        ).pack(fill='x', pady=1)
        
    def _no_callback(self):
        """Заглушка для отсутствующих callback'ов"""
        pass
        
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
            
            return users_count, groups_count
            
        except Exception as e:
            self.total_users_label.config(text='Пользователи: ошибка')
            self.total_groups_label.config(text='Группы: ошибка')
            raise e
            
    def update_statistics(self, users_count: int, groups_count: int):
        """Обновление отображаемой статистики"""
        self.total_users_label.config(text=f'Пользователи: {users_count}')
        self.total_groups_label.config(text=f'Группы: {groups_count}')
        
    def refresh(self):
        """Принудительное обновление статистики"""
        return self.load_statistics()
