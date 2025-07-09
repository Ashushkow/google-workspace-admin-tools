# -*- coding: utf-8 -*-
"""
Журнал активности для главного окна приложения.
"""

import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
from typing import Optional

from ..ui_components import ModernColors, ModernButton
from ...themes.theme_manager import theme_manager


class ActivityLog(tk.Frame):
    """
    Панель журнала активности.
    """
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, relief='solid', bd=1)
        
        self._setup_ui()
        self.apply_theme()
        
        # Подписываемся на изменения темы
        theme_manager.add_theme_change_callback(self.on_theme_changed)
        
    def _setup_ui(self):
        """Настройка пользовательского интерфейса журнала"""
        self.pack(side='right', fill='both', expand=True, padx=0, pady=0)
        
        self._create_header()
        self._create_log_area()
        
    def _create_header(self):
        """Создание заголовка журнала"""
        self.log_header = tk.Frame(self)
        self.log_header.pack(fill='x', padx=10, pady=(10, 8))
        
        self.header_label = tk.Label(
            self.log_header,
            text='📝 Журнал активности',
            font=('Arial', 12, 'bold')
        )
        self.header_label.pack(side='left')
        
        self.clear_button = ModernButton(
            self.log_header,
            text='🗑️ Очистить',
            command=self.clear_log,
            style='secondary',
            font=('Arial', 9)
        )
        self.clear_button.pack(side='right')
        
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
        
    def apply_theme(self):
        """Применение текущей темы"""
        if not theme_manager.current_theme:
            return
            
        theme = theme_manager.current_theme
        
        # Применяем цвета к основному фрейму
        self.config(bg=theme.get_color('secondary'))
        
        # Обновляем все дочерние элементы
        for widget in self.winfo_children():
            self._apply_theme_to_widget(widget, theme)
            
    def _apply_theme_to_widget(self, widget, theme):
        """Применение темы к виджету"""
        try:
            if isinstance(widget, tk.Label):
                widget.config(
                    bg=theme.get_color('secondary'),
                    fg=theme.get_color('text_primary')
                )
            elif isinstance(widget, tk.Frame):
                widget.config(bg=theme.get_color('secondary'))
                # Рекурсивно применяем к дочерним элементам
                for child in widget.winfo_children():
                    self._apply_theme_to_widget(child, theme)
            elif isinstance(widget, scrolledtext.ScrolledText):
                widget.config(
                    bg=theme.get_color('background'),
                    fg=theme.get_color('text_primary'),
                    insertbackground=theme.get_color('text_primary')
                )
        except tk.TclError:
            # Игнорируем ошибки для виджетов, которые не поддерживают эти опции
            pass
            
    def on_theme_changed(self, theme):
        """Обработчик изменения темы"""
        self.apply_theme()
