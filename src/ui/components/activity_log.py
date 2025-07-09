# -*- coding: utf-8 -*-
"""
Журнал активности для главного окна приложения.
"""

import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
from typing import Optional

from ..ui_components import ModernColors, ModernButton


class ActivityLog(tk.Frame):
    """
    Панель журнала активности.
    """
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg=ModernColors.CARD_BG, relief='solid', bd=1)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Настройка пользовательского интерфейса журнала"""
        self.pack(side='right', fill='both', expand=True, padx=0, pady=0)
        
        self._create_header()
        self._create_log_area()
        
    def _create_header(self):
        """Создание заголовка журнала"""
        log_header = tk.Frame(self, bg=ModernColors.CARD_BG)
        log_header.pack(fill='x', padx=10, pady=(10, 8))
        
        tk.Label(
            log_header,
            text='📝 Журнал активности',
            font=('Arial', 12, 'bold'),
            bg=ModernColors.CARD_BG,
            fg=ModernColors.TEXT_PRIMARY
        ).pack(side='left')
        
        ModernButton(
            log_header,
            text='🗑️ Очистить',
            command=self.clear_log,
            style='secondary',
            font=('Arial', 9)
        ).pack(side='right')
        
    def _create_log_area(self):
        """Создание области журнала"""
        log_frame = tk.Frame(self, bg=ModernColors.CARD_BG)
        log_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='white',
            fg=ModernColors.TEXT_PRIMARY,
            relief='solid',
            bd=1
        )
        self.log_text.pack(fill='both', expand=True)
        
    def add_entry(self, message: str, level: str = 'INFO'):
        """Добавляет запись в журнал активности"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Определяем цвет для разных уровней
        color_map = {
            'INFO': 'black',
            'WARNING': 'orange',
            'ERROR': 'red',
            'SUCCESS': 'green'
        }
        
        log_entry = f'[{timestamp}] {level}: {message}\n'
        
        # Вставляем текст
        self.log_text.insert(tk.END, log_entry)
        
        # Применяем цвет к последней строке
        start_line = self.log_text.index(tk.END + "-2l linestart")
        end_line = self.log_text.index(tk.END + "-1l lineend")
        
        tag_name = f"level_{level}"
        self.log_text.tag_add(tag_name, start_line, end_line)
        self.log_text.tag_config(tag_name, foreground=color_map.get(level, 'black'))
        
        # Прокручиваем к концу
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """Очистка журнала активности"""
        self.log_text.delete(1.0, tk.END)
        self.add_entry('Журнал активности очищен')
        
    def get_log_content(self) -> str:
        """Получение содержимого журнала"""
        return self.log_text.get(1.0, tk.END)
        
    def save_log_to_file(self, filename: str):
        """Сохранение журнала в файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.get_log_content())
            return True
        except Exception:
            return False
