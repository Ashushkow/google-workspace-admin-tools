#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенная система конфигурации с поддержкой переменных окружения.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class AppSettings(BaseSettings):
    """Настройки приложения с валидацией"""
    
    # Google Workspace
    google_application_credentials: str = "credentials.json"
    google_workspace_domain: str = "yourdomain.com"
    google_workspace_admin: str = "admin@yourdomain.com"
    
    # Application
    app_name: str = "Admin Team Tools"
    app_version: str = "2.0.7"
    app_debug: bool = False
    app_log_level: str = "INFO"
    cli_mode: bool = False
    
    # Database
    database_url: str = "sqlite:///data/admin_tools.db"
    cache_ttl: int = 300
    
    # Security
    secret_key: str = "your-secret-key-here"
    encryption_key: str = "your-encryption-key-here"
    
    # API
    api_rate_limit: int = 100
    api_timeout: int = 30
    api_retry_count: int = 3
    
    # UI
    ui_theme: str = "light"
    ui_language: str = "ru"
    ui_window_size: str = "1200x800"
    
    # Logging
    log_file: str = "logs/admin_tools.log"
    log_max_size: str = "10MB"
    log_backup_count: int = 5
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Development
    dev_mode: bool = False
    debug_sql: bool = False
    profiling_enabled: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @field_validator("google_workspace_domain")
    @classmethod
    def validate_domain(cls, v):
        # В режиме разработки разрешаем тестовые домены
        import os
        is_dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'
        
        if not is_dev_mode and v in ["yourdomain.com", "example.com"]:
            raise ValueError("Необходимо заменить yourdomain.com на ваш домен")
        # Разрешаем тестовые домены для разработки
        return v
    
    @field_validator("google_workspace_admin")
    @classmethod
    def validate_admin_email(cls, v):
        # В режиме разработки разрешаем тестовые email
        import os
        is_dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'
        
        if not is_dev_mode and v in ["admin@yourdomain.com", "admin@example.com"]:
            raise ValueError("Необходимо заменить admin@yourdomain.com на реальный email")
        # Разрешаем тестовые email для разработки
        return v
    
    @field_validator("app_log_level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Неверный уровень логирования. Доступные: {valid_levels}")
        return v.upper()

@dataclass
class GoogleAPIConfig:
    """Конфигурация Google API"""
    scopes: list = field(default_factory=lambda: [
        'https://www.googleapis.com/auth/admin.directory.user',
        'https://www.googleapis.com/auth/admin.directory.group',
        'https://www.googleapis.com/auth/admin.directory.orgunit',
        'https://www.googleapis.com/auth/admin.directory.domain.readonly',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/drive'
    ])
    credentials_file: str = "credentials.json"
    token_file: str = "token.pickle"
    
class ConfigManager:
    """Менеджер конфигурации"""
    
    def __init__(self):
        self._settings: Optional[AppSettings] = None
        self._google_config: Optional[GoogleAPIConfig] = None
        
    @property
    def settings(self) -> AppSettings:
        """Получить настройки приложения"""
        if self._settings is None:
            self._settings = AppSettings()
        return self._settings
    
    @property
    def google(self) -> GoogleAPIConfig:
        """Получить конфигурацию Google API"""
        if self._google_config is None:
            self._google_config = GoogleAPIConfig()
        return self._google_config
    
    def reload(self):
        """Перезагрузить конфигурацию"""
        self._settings = None
        self._google_config = None
        load_dotenv(override=True)
    
    def get_database_path(self) -> Path:
        """Получить путь к базе данных"""
        url = self.settings.database_url
        if url.startswith("sqlite:///"):
            path = Path(url.replace("sqlite:///", ""))
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        raise ValueError(f"Неподдерживаемый тип базы данных: {url}")
    
    def get_log_path(self) -> Path:
        """Получить путь к файлу логов"""
        path = Path(self.settings.log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    def is_development(self) -> bool:
        """Проверить режим разработки"""
        return self.settings.dev_mode or self.settings.app_debug
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Экспортировать настройки в словарь"""
        return self.settings.dict()
    
    def export_to_json(self, file_path: Union[str, Path]) -> None:
        """Экспортировать настройки в JSON файл"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.export_to_dict(), f, indent=2, ensure_ascii=False)

# Глобальный экземпляр менеджера конфигурации
config = ConfigManager()

# Обратная совместимость
SCOPES = config.google.scopes
CREDENTIALS_FILE = config.google.credentials_file
TOKEN_PICKLE = config.google.token_file
DOMAIN_ADMIN_EMAIL = config.settings.google_workspace_admin
settings = config.settings.dict()

def load_settings() -> Dict[str, Any]:
    """Загрузить настройки (для обратной совместимости)"""
    return config.export_to_dict()
