"""
Компонент для переключения тем
"""
import tkinter as tk
from tkinter import ttk
from ...themes.theme_manager import theme_manager


class ThemeSwitcher(tk.Frame):
    """Переключатель тем"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.create_widgets()
        self.apply_theme()
        
        # Подписываемся на изменения темы
        theme_manager.add_theme_change_callback(self.on_theme_changed)
        
    def create_widgets(self):
        """Создание виджетов"""
        # Метка
        self.label = tk.Label(
            self,
            text="Тема:",
            font=('Segoe UI', 9)
        )
        self.label.pack(side='left', padx=(0, 5))
        
        # Комбобокс с темами
        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(
            self,
            textvariable=self.theme_var,
            values=theme_manager.get_theme_names(),
            state='readonly',
            width=10,
            font=('Segoe UI', 9)
        )
        self.theme_combo.pack(side='left')
        self.theme_combo.bind('<<ComboboxSelected>>', self.on_theme_selected)
        
        # Устанавливаем текущую тему
        if theme_manager.current_theme:
            self.theme_var.set(theme_manager.current_theme.name)
            
    def on_theme_selected(self, event):
        """Обработчик выбора темы"""
        selected_theme = self.theme_var.get()
        theme_manager.set_theme(selected_theme)
        
    def on_theme_changed(self, theme):
        """Обработчик изменения темы"""
        self.apply_theme()
        
    def apply_theme(self):
        """Применение текущей темы"""
        if not theme_manager.current_theme:
            return
            
        theme = theme_manager.current_theme
        
        # Применяем цвета
        self.config(bg=theme.get_color('secondary'))
        self.label.config(
            bg=theme.get_color('secondary'),
            fg=theme.get_color('text_primary'),
            font=theme.get_font('default')
        )
