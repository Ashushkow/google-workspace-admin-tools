"""
Менеджер тем для приложения Admin Team Tools
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path


class Theme:
    """Класс для хранения настроек темы"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.colors = config.get('colors', {})
        self.fonts = config.get('fonts', {})
        self.styles = config.get('styles', {})
        
    def get_color(self, key: str, default: str = '#000000') -> str:
        """Получить цвет по ключу"""
        return self.colors.get(key, default)
        
    def get_font(self, key: str, default: tuple = ('Arial', 10)) -> tuple:
        """Получить шрифт по ключу"""
        font_config = self.fonts.get(key, default)
        if isinstance(font_config, list):
            return tuple(font_config)
        return font_config


class ThemeManager:
    """Менеджер тем приложения"""
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        self.theme_change_callbacks = []
        self._load_default_themes()
        
    def _load_default_themes(self):
        """Загружает встроенные темы"""
        # Светлая тема
        light_theme = {
            'colors': {
                'background': '#FFFFFF',
                'secondary': '#F5F5F5',
                'accent': '#007ACC',
                'accent_hover': '#005A9E',
                'text_primary': '#333333',
                'text_secondary': '#666666',
                'text_accent': '#FFFFFF',
                'border': '#CCCCCC',
                'success': '#28A745',
                'warning': '#FFC107',
                'error': '#DC3545',
                'info': '#17A2B8'
            },
            'fonts': {
                'default': ['Segoe UI', 10],
                'heading': ['Segoe UI', 12, 'bold'],
                'small': ['Segoe UI', 8],
                'monospace': ['Consolas', 9]
            }
        }
        
        # Тёмная тема
        dark_theme = {
            'colors': {
                'background': '#2B2B2B',
                'secondary': '#3C3C3C',
                'accent': '#0078D4',
                'accent_hover': '#106EBE',
                'text_primary': '#FFFFFF',
                'text_secondary': '#CCCCCC',
                'text_accent': '#FFFFFF',
                'border': '#555555',
                'success': '#28A745',
                'warning': '#FFC107',
                'error': '#DC3545',
                'info': '#17A2B8'
            },
            'fonts': {
                'default': ['Segoe UI', 10],
                'heading': ['Segoe UI', 12, 'bold'],
                'small': ['Segoe UI', 8],
                'monospace': ['Consolas', 9]
            }
        }
        
        # Синяя тема
        blue_theme = {
            'colors': {
                'background': '#F0F8FF',
                'secondary': '#E6F3FF',
                'accent': '#0066CC',
                'accent_hover': '#004499',
                'text_primary': '#1A1A1A',
                'text_secondary': '#4A4A4A',
                'text_accent': '#FFFFFF',
                'border': '#B3D9FF',
                'success': '#28A745',
                'warning': '#FF8C00',
                'error': '#DC3545',
                'info': '#0066CC'
            },
            'fonts': {
                'default': ['Segoe UI', 10],
                'heading': ['Segoe UI', 12, 'bold'],
                'small': ['Segoe UI', 8],
                'monospace': ['Consolas', 9]
            }
        }
        
        self.add_theme('light', light_theme)
        self.add_theme('dark', dark_theme)
        self.add_theme('blue', blue_theme)
        
        # Устанавливаем светлую тему по умолчанию
        self.set_theme('light')
        
    def add_theme(self, name: str, config: Dict[str, Any]):
        """Добавить новую тему"""
        self.themes[name] = Theme(name, config)
        
    def set_theme(self, name: str) -> bool:
        """Установить текущую тему"""
        if name in self.themes:
            self.current_theme = self.themes[name]
            self._notify_theme_change()
            return True
        return False
        
    def get_theme_names(self) -> list:
        """Получить список доступных тем"""
        return list(self.themes.keys())
        
    def add_theme_change_callback(self, callback):
        """Добавить callback для изменения темы"""
        self.theme_change_callbacks.append(callback)
        
    def _notify_theme_change(self):
        """Уведомить о смене темы"""
        for callback in self.theme_change_callbacks:
            try:
                callback(self.current_theme)
            except Exception as e:
                print(f"Ошибка в callback смены темы: {e}")
                
    def save_theme_preference(self, config_path: str):
        """Сохранить предпочтение темы"""
        try:
            config = {'current_theme': self.current_theme.name}
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек темы: {e}")
            
    def load_theme_preference(self, config_path: str):
        """Загрузить предпочтение темы"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    theme_name = config.get('current_theme', 'light')
                    self.set_theme(theme_name)
        except Exception as e:
            print(f"Ошибка загрузки настроек темы: {e}")


# Глобальный экземпляр менеджера тем
theme_manager = ThemeManager()
