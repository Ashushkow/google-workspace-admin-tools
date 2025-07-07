# -*- coding: utf-8 -*-
"""
Улучшенная система конфигурации с валидацией и безопасностью.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    """
    Конфигурация приложения с типизацией и валидацией.
    """
    # Основные настройки
    window_width: int = 750
    window_height: int = 500
    theme: str = "light"
    language: str = "ru"
    
    # API настройки
    api_timeout: int = 30
    max_retries: int = 3
    cache_duration: int = 300
    
    # Пагинация
    users_per_page: int = 100
    groups_per_page: int = 100
    
    # Безопасность
    auto_logout_minutes: int = 60
    require_confirmation: bool = True
    log_sensitive_data: bool = False
    
    # Производительность
    max_concurrent_requests: int = 5
    ui_update_interval: int = 100
    
    # Интеграции
    asana_workspace: str = ""
    smtp_enabled: bool = False
    
    def validate(self) -> bool:
        """Валидация конфигурации"""
        if self.window_width < 600 or self.window_height < 400:
            return False
        if self.api_timeout < 5 or self.api_timeout > 120:
            return False
        if self.cache_duration < 60 or self.cache_duration > 3600:
            return False
        return True


class ConfigManager:
    """
    Менеджер конфигурации с автоматической миграцией и валидацией.
    """
    
    def __init__(self, config_file: str = "app_config.json"):
        self.config_file = Path(config_file)
        self.config = AppConfig()
        self.load_config()
    
    def load_config(self):
        """Загружает конфигурацию из файла"""
        if not self.config_file.exists():
            self.save_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Обновляем конфигурацию из файла
            for key, value in data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            # Валидируем конфигурацию
            if not self.config.validate():
                print("Предупреждение: Некорректная конфигурация, используются значения по умолчанию")
                self.config = AppConfig()
                self.save_config()
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            self.config = AppConfig()
            self.save_config()
    
    def save_config(self):
        """Сохраняет конфигурацию в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.__dict__, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получает значение конфигурации"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """Устанавливает значение конфигурации"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_config()
    
    def reset_to_defaults(self):
        """Сбрасывает конфигурацию к значениям по умолчанию"""
        self.config = AppConfig()
        self.save_config()


# Глобальный экземпляр конфигурации
config_manager = ConfigManager()
