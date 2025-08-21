#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенная система конфигурации с поддержкой переменных окружения.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Импорт утилиты для работы с ресурсами в bundle
from ..utils.resource_path import get_resource_path, ensure_resource_dir

# Загружаем переменные окружения
load_dotenv()

class AppSettings(BaseSettings):
    """Настройки приложения с валидацией"""
    
    # Google Workspace
    google_application_credentials: str = "config/credentials.json"
    google_workspace_domain: str = "yourdomain.com"
    google_workspace_admin: str = "admin@yourdomain.com"
    
    def get_credentials_path(self) -> Path:
        """Получить путь к credentials с поддержкой bundle"""
        return get_resource_path(self.google_application_credentials)
    
    # Application
    app_name: str = "Admin Team Tools"
    app_version: str = "2.2.0"
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
    ui_window_size: str = "600x400"
    
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
        extra = "allow"  # Разрешаем дополнительные поля из переменных окружения
        
    @field_validator("google_workspace_domain")
    @classmethod
    def validate_domain(cls, v):
        # Разрешаем любые домены, включая тестовые
        # Валидация будет проверяться при реальном использовании API
        return v
    
    @field_validator("google_workspace_admin")
    @classmethod
    def validate_admin_email(cls, v):
        # Разрешаем любые email, включая тестовые
        # Валидация будет проверяться при реальном использовании API
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
        'https://www.googleapis.com/auth/admin.directory.group.member',
        'https://www.googleapis.com/auth/admin.directory.orgunit',
        'https://www.googleapis.com/auth/admin.directory.domain.readonly',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/gmail.send'  # Для отправки приветственных писем
    ])
    credentials_file: str = "config/credentials.json"
    token_file: str = "config/token.pickle"
    
    def get_credentials_path(self) -> Path:
        """Получить путь к файлу credentials с поддержкой bundle"""
        return get_resource_path(self.credentials_file)
    
    def get_token_path(self) -> Path:
        """Получить путь к файлу token с поддержкой bundle"""
        return get_resource_path(self.token_file)
    
class ConfigManager:
    """Менеджер конфигурации"""
    
    def __init__(self):
        self._settings: Optional[AppSettings] = None
        self._google_config: Optional[GoogleAPIConfig] = None
        self._first_run_checked = False
        
    def _check_first_run(self) -> bool:
        """Проверить, является ли это первым запуском"""
        
        # 1. Сначала проверяем переменную окружения FIRST_RUN
        if os.getenv('FIRST_RUN', '').lower() == 'false':
            return False
        
        # 2. Специальная проверка для exe: если это bundled приложение,
        # проверяем файлы рядом с exe, а не внутри bundle
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent
            print(f"🔍 Проверка первого запуска для exe в папке: {exe_dir}")
            
            # Для exe приложения проверяем ТОЛЬКО файлы рядом с exe
            # (не внутри bundle, где могут быть файлы разработчика)
            
            # Проверяем .env рядом с exe
            env_file = exe_dir / ".env"
            env_configured = False
            if env_file.exists():
                try:
                    env_content = env_file.read_text(encoding='utf-8')
                    if ('GOOGLE_WORKSPACE_DOMAIN=' in env_content and 
                        'yourdomain.com' not in env_content and 
                        'example.com' not in env_content):
                        env_configured = True
                except:
                    pass
            
            # Проверяем credentials рядом с exe
            credentials_paths = [
                exe_dir / "config" / "credentials.json",
                exe_dir / "credentials.json"
            ]
            
            credentials_found = False
            for cred_path in credentials_paths:
                if cred_path.exists() and cred_path.stat().st_size > 100:
                    credentials_found = True
                    break
            
            # Проверяем token рядом с exe
            token_paths = [
                exe_dir / "config" / "token.pickle",
                exe_dir / "token.pickle"
            ]
            
            token_found = False
            for token_path in token_paths:
                if token_path.exists():
                    token_found = True
                    break
            
            # Для exe: первый запуск если НЕТ настроек рядом с exe
            is_first = not env_configured and not credentials_found and not token_found
            
            print(f"🔍 Статус проверки для exe:")
            print(f"  📁 .env рядом с exe: {'✅' if env_file.exists() else '❌'}")
            print(f"  ⚙️ .env настроен: {'✅' if env_configured else '❌'}")
            print(f"  🔑 credentials рядом с exe: {'✅' if credentials_found else '❌'}")
            print(f"  🎫 token рядом с exe: {'✅' if token_found else '❌'}")
            print(f"  🚨 Первый запуск: {'✅' if is_first else '❌'}")
            
            return is_first
        
        # 3. Стандартная проверка для режима разработки
        env_file = Path(".env")
        if env_file.exists():
            try:
                env_content = env_file.read_text(encoding='utf-8')
                # Если домен настроен (не тестовый), то не первый запуск
                if ('GOOGLE_WORKSPACE_DOMAIN=' in env_content and 
                    'yourdomain.com' not in env_content and 
                    'example.com' not in env_content):
                    return False
            except:
                pass
        
        # 4. Проверяем наличие настроенных credentials в dev режиме
        credentials_paths = [
            Path("config/credentials.json"),
            Path("credentials.json")
        ]
        
        credentials_found = False
        for cred_path in credentials_paths:
            if cred_path.exists() and cred_path.stat().st_size > 100:  # Не пустой файл
                credentials_found = True
                break
        
        # 5. Проверяем token файл (признак настроенной авторизации)
        token_paths = [
            Path("config/token.pickle"),
            Path("token.pickle")
        ]
        
        token_found = False
        for token_path in token_paths:
            if token_path.exists():
                token_found = True
                break
        
        # 6. Первый запуск, если НЕТ файла .env с настройками И НЕТ credentials
        is_first = not credentials_found and not (env_file.exists() and 'GOOGLE_WORKSPACE_DOMAIN=' in env_file.read_text(encoding='utf-8'))
        
        if is_first:
            print(f"🔍 Определён первый запуск (dev режим):")
            print(f"  📁 .env с настройками: {'✅' if env_file.exists() else '❌'}")
            print(f"  🔑 credentials.json: {'✅' if credentials_found else '❌'}")  
            print(f"  🎫 token.pickle: {'✅' if token_found else '❌'}")
            
        return is_first
    
    def _set_first_run_environment(self):
        """Установить переменные окружения для первого запуска"""
        os.environ['FIRST_RUN'] = 'True'
        os.environ['SKIP_CONFIG_VALIDATION'] = 'True'
        os.environ['GOOGLE_WORKSPACE_DOMAIN'] = 'yourdomain.com'  # Временно
        os.environ['GOOGLE_WORKSPACE_ADMIN'] = 'admin@yourdomain.com'  # Временно
    
    @property
    def settings(self) -> AppSettings:
        """Получить настройки приложения"""
        if self._settings is None:
            # Проверяем первый запуск только один раз
            if not self._first_run_checked:
                if self._check_first_run():
                    # Устанавливаем переменные окружения для первого запуска
                    self._set_first_run_environment()
                self._first_run_checked = True
                
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
            relative_path = url.replace("sqlite:///", "")
            path = get_resource_path(relative_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        raise ValueError(f"Неподдерживаемый тип базы данных: {url}")
    
    def get_log_path(self) -> Path:
        """Получить путь к файлу логов"""
        path = get_resource_path(self.settings.log_file)
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
    
    def is_first_run(self) -> bool:
        """Проверить, является ли это первым запуском"""
        return self._check_first_run()
    
    def create_initial_config(self, domain: str, admin_email: str) -> None:
        """Создать начальную конфигурацию"""
        env_content = f"""# Google Workspace Configuration
GOOGLE_WORKSPACE_DOMAIN={domain}
GOOGLE_WORKSPACE_ADMIN={admin_email}

# Application Settings
APP_NAME=Admin Team Tools
APP_VERSION=2.2.0
APP_DEBUG=false

# Disable validation for setup
SKIP_CONFIG_VALIDATION=false
FIRST_RUN=false
"""
        
        # Определяем путь к .env файлу в зависимости от режима запуска
        if getattr(sys, 'frozen', False):
            # Для exe - создаем .env рядом с exe файлом
            app_dir = Path(sys.executable).parent
            env_file = app_dir / ".env"
        else:
            # Для разработки - в рабочей папке
            env_file = Path(".env")
            
        try:
            env_file.write_text(env_content, encoding='utf-8')
            print(f"✅ Создан файл конфигурации: {env_file.absolute()}")
        except Exception as e:
            print(f"❌ Ошибка создания .env: {e}")
            # Попытка создать в текущей папке как fallback
            try:
                Path(".env").write_text(env_content, encoding='utf-8')
                print("✅ .env создан в текущей папке как запасной вариант")
            except:
                pass
        
        # Обновляем переменные окружения
        os.environ['GOOGLE_WORKSPACE_DOMAIN'] = domain
        os.environ['GOOGLE_WORKSPACE_ADMIN'] = admin_email
        os.environ['FIRST_RUN'] = 'false'
        os.environ['SKIP_CONFIG_VALIDATION'] = 'false'
        
        print(f"✅ Конфигурация сохранена: домен={domain}, админ={admin_email}")
        os.environ['GOOGLE_WORKSPACE_DOMAIN'] = domain
        os.environ['GOOGLE_WORKSPACE_ADMIN'] = admin_email
        os.environ['SKIP_CONFIG_VALIDATION'] = 'false'
        os.environ['FIRST_RUN'] = 'false'
        
        # Перезагружаем настройки
        self.reload()

# Глобальный экземпляр менеджера конфигурации
config = ConfigManager()

# Функции для динамического получения значений конфигурации
def get_scopes():
    """Получить scopes"""
    return config.google.scopes

def get_credentials_file():
    """Получить путь к credentials файлу"""
    return config.google.get_credentials_path()

def get_token_pickle():
    """Получить путь к token файлу"""
    return config.google.get_token_path()

def get_domain_admin_email():
    """Получить email администратора домена"""
    return config.settings.google_workspace_admin

def get_workspace_domain():
    """Получить домен workspace"""
    return config.settings.google_workspace_domain

def get_settings():
    """Получить все настройки"""
    return config.settings.dict()

def load_settings() -> Dict[str, Any]:
    """Загрузить настройки (для обратной совместимости)"""
    return config.export_to_dict()
