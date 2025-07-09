# -*- coding: utf-8 -*-
"""
Панель инструментов для главного окна приложения.
"""

import tkinter as tk
from typing import Optional, Dict, Callable

from ..ui_components import ModernColors, ModernButton


class MainToolbar(tk.Frame):
    """
    Панель инструментов с кнопками основных действий.
    """
    
    def __init__(self, parent: tk.Widget, callbacks: Optional[Dict[str, Callable]] = None):
        super().__init__(parent, bg=ModernColors.BACKGROUND, height=80)
        
        self.callbacks = callbacks or {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Настройка пользовательского интерфейса панели инструментов"""
        self.pack(fill='x', padx=15, pady=(5, 0))
        self.pack_propagate(False)
        
        self._create_top_buttons()
        self._create_bottom_buttons()
        
    def _create_top_buttons(self):
        """Создание верхней строки кнопок"""
        top_buttons_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        top_buttons_frame.pack(fill='x', pady=(0, 5))
        
        # Основные действия
        ModernButton(
            top_buttons_frame,
            text='👥 Сотрудники',
            command=self.callbacks.get('employee_list', self._no_callback),
            style='primary',
            font=('Arial', 9)
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            top_buttons_frame,
            text='➕ Создать',
            command=self.callbacks.get('create_user', self._no_callback),
            style='success',
            font=('Arial', 9)
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            top_buttons_frame,
            text='✏️ Редактировать',
            command=self.callbacks.get('edit_user', self._no_callback),
            style='secondary',
            font=('Arial', 9)
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            top_buttons_frame,
            text='📧 Asana',
            command=self.callbacks.get('asana', self._no_callback),
            style='warning',
            font=('Arial', 9)
        ).pack(side='right', padx=(8, 0))
        
    def _create_bottom_buttons(self):
        """Создание нижней строки кнопок"""
        bottom_buttons_frame = tk.Frame(self, bg=ModernColors.BACKGROUND)
        bottom_buttons_frame.pack(fill='x')
        
        # Группы
        ModernButton(
            bottom_buttons_frame,
            text='👥 Группы',
            command=self.callbacks.get('groups', self._no_callback),
            style='info',
            font=('Arial', 9)
        ).pack(side='left', padx=(0, 8))
        
    def _no_callback(self):
        """Заглушка для отсутствующих callback'ов"""
        pass
        
    def update_callbacks(self, new_callbacks: Dict[str, Callable]):
        """Обновление callbacks"""
        self.callbacks.update(new_callbacks)
        
    def enable_button(self, button_key: str, enabled: bool = True):
        """Включение/отключение кнопки"""
        # Можно расширить для управления состоянием кнопок
        pass
        
    def get_button_by_key(self, button_key: str):
        """Получение кнопки по ключу"""
        # Можно расширить для получения конкретных кнопок
        pass
