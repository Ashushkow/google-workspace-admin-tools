"""
Менеджер горячих клавиш для приложения Admin Team Tools
"""
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Callable, Optional, Any
import json
import os


class HotkeyManager:
    """Менеджер горячих клавиш"""
    
    def __init__(self, root_window: tk.Tk):
        self.root = root_window
        self.hotkeys: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, Callable] = {}
        self._load_default_hotkeys()
        self._bind_hotkeys()
        
    def _load_default_hotkeys(self):
        """Загружает стандартные горячие клавиши"""
        self.hotkeys = {
            # Основные операции
            'refresh': {
                'key': '<Control-r>',
                'description': 'Обновить данные',
                'category': 'Основные'
            },
            'export': {
                'key': '<Control-e>',
                'description': 'Экспорт пользователей',
                'category': 'Основные'
            },
            'search': {
                'key': '<Control-f>',
                'description': 'Поиск',
                'category': 'Основные'
            },
            'settings': {
                'key': '<Control-comma>',
                'description': 'Настройки',
                'category': 'Основные'
            },
            
            # Управление пользователями
            'new_user': {
                'key': '<Control-n>',
                'description': 'Новый пользователь',
                'category': 'Пользователи'
            },
            'edit_user': {
                'key': '<Control-Return>',
                'description': 'Редактировать пользователя',
                'category': 'Пользователи'
            },
            'delete_user': {
                'key': '<Delete>',
                'description': 'Удалить пользователя',
                'category': 'Пользователи'
            },
            'user_list': {
                'key': '<Control-u>',
                'description': 'Список пользователей',
                'category': 'Пользователи'
            },
            
            # Управление группами
            'groups': {
                'key': '<Control-g>',
                'description': 'Управление группами',
                'category': 'Группы'
            },
            'new_group': {
                'key': '<Control-Shift-n>',
                'description': 'Новая группа',
                'category': 'Группы'
            },
            
            # Управление календарями
            'sputnik_calendar': {
                'key': '<Control-Shift-s>',
                'description': 'Календарь SPUTNIK (общий)',
                'category': 'Календари'
            },
            'calendars': {
                'key': '<Control-Shift-c>',
                'description': 'Управление календарями',
                'category': 'Календари'
            },
            
            # Управление документами
            'documents': {
                'key': '<Control-d>',
                'description': 'Управление доступом к документам',
                'category': 'Документы'
            },
            
            # Служебные
            'help': {
                'key': '<F1>',
                'description': 'Справка',
                'category': 'Служебные'
            },
            'about': {
                'key': '<Control-F1>',
                'description': 'О программе',
                'category': 'Служебные'
            },
            'quit': {
                'key': '<Control-q>',
                'description': 'Выход',
                'category': 'Служебные'
            },
            
            # Темы
            'theme_light': {
                'key': '<Control-1>',
                'description': 'Светлая тема',
                'category': 'Темы'
            },
            'theme_dark': {
                'key': '<Control-2>',
                'description': 'Тёмная тема',
                'category': 'Темы'
            },
            'theme_blue': {
                'key': '<Control-3>',
                'description': 'Синяя тема',
                'category': 'Темы'
            }
        }
        
    def register_callback(self, action: str, callback: Callable):
        """Регистрирует callback для действия"""
        self.callbacks[action] = callback
        
    def _bind_hotkeys(self):
        """Привязывает горячие клавиши к окну"""
        for action, config in self.hotkeys.items():
            key = config['key']
            self.root.bind(key, lambda event, act=action: self._handle_hotkey(act))
            
    def _handle_hotkey(self, action: str):
        """Обрабатывает нажатие горячей клавиши"""
        if action in self.callbacks:
            try:
                self.callbacks[action]()
            except Exception as e:
                print(f"Ошибка выполнения горячей клавиши {action}: {e}")
                
    def get_hotkey_description(self, action: str) -> str:
        """Получает описание горячей клавиши"""
        if action in self.hotkeys:
            config = self.hotkeys[action]
            return f"{config['key']} - {config['description']}"
        return ""
        
    def get_hotkeys_by_category(self) -> Dict[str, list]:
        """Группирует горячие клавиши по категориям"""
        categories = {}
        for action, config in self.hotkeys.items():
            category = config.get('category', 'Другие')
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'action': action,
                'key': config['key'],
                'description': config['description']
            })
        return categories
        
    def show_help_dialog(self):
        """Показывает диалог со списком горячих клавиш"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Горячие клавиши")
        help_window.geometry("500x600")
        help_window.resizable(False, False)
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Создаем текстовое поле с прокруткой
        text_frame = tk.Frame(help_window)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        text_widget = tk.Text(
            text_frame,
            wrap='word',
            yscrollcommand=scrollbar.set,
            font=('Consolas', 10),
            state='disabled'
        )
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Заполняем текст
        categories = self.get_hotkeys_by_category()
        content = "ГОРЯЧИЕ КЛАВИШИ ADMIN TEAM TOOLS\n\n"
        
        for category, hotkeys in categories.items():
            content += f"━━━ {category.upper()} ━━━\n"
            for hotkey in hotkeys:
                key = hotkey['key'].replace('<', '').replace('>', '')
                key = key.replace('Control', 'Ctrl').replace('Shift', 'Shift')
                content += f"  {key:<15} {hotkey['description']}\n"
            content += "\n"
            
        text_widget.config(state='normal')
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled')
        
        # Кнопка закрытия
        close_btn = tk.Button(
            help_window,
            text="Закрыть",
            command=help_window.destroy,
            width=15
        )
        close_btn.pack(pady=10)
        
        # Центрируем окно
        help_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
