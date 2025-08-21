#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Валидатор окружения для Admin Team Tools.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from .exceptions import ConfigurationError, CredentialsError

class EnvironmentValidator:
    """Валидатор окружения и конфигурации"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Полная валидация окружения
        
        Returns:
            Tuple[bool, List[str], List[str]]: (успех, ошибки, предупреждения)
        """
        self.errors.clear()
        self.warnings.clear()
        
        self.logger.info("Начинаем валидацию окружения...")
        
        # Валидация Python
        self._validate_python_version()
        
        # Валидация структуры проекта
        self._validate_project_structure()
        
        # Валидация зависимостей
        self._validate_dependencies()
        
        # Валидация credentials
        self._validate_credentials()
        
        # Валидация конфигурации
        self._validate_configuration()
        
        # Валидация прав доступа
        self._validate_permissions()
        
        success = len(self.errors) == 0
        
        if success:
            self.logger.info("✅ Валидация окружения прошла успешно")
        else:
            self.logger.error(f"❌ Валидация окружения не пройдена. Ошибок: {len(self.errors)}")
            
        if self.warnings:
            self.logger.warning(f"⚠️ Предупреждений: {len(self.warnings)}")
            
        return success, self.errors, self.warnings
    
    def _validate_python_version(self):
        """Валидация версии Python"""
        min_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version < min_version:
            self.errors.append(
                f"Требуется Python {'.'.join(map(str, min_version))} или выше. "
                f"Текущая версия: {'.'.join(map(str, current_version))}"
            )
        else:
            self.logger.debug(f"✅ Python версия: {'.'.join(map(str, current_version))}")
    
    def _validate_project_structure(self):
        """Валидация структуры проекта"""
        required_dirs = [
            'src',
            'src/api',
            'src/ui',
            'src/utils',
            'docs',
            'config'
        ]
        
        required_files = [
            'main.py',
            'requirements.txt',
            'README.md',
            'src/__init__.py',
            'src/auth.py',
            'src/config.py'
        ]
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                self.errors.append(f"Отсутствует обязательная директория: {dir_path}")
            else:
                self.logger.debug(f"✅ Директория найдена: {dir_path}")
        
        for file_path in required_files:
            if not Path(file_path).exists():
                self.errors.append(f"Отсутствует обязательный файл: {file_path}")
            else:
                self.logger.debug(f"✅ Файл найден: {file_path}")
    
    def _validate_dependencies(self):
        """Валидация зависимостей"""
        requirements_file = Path('requirements.txt')
        
        if not requirements_file.exists():
            self.errors.append("Отсутствует файл requirements.txt")
            return
        
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                requirements = f.read().strip().split('\n')
            
            required_packages = [
                'google-api-python-client',
                'google-auth',
                'google-auth-oauthlib',
                'google-auth-httplib2'
            ]
            
            for package in required_packages:
                if not any(package in req for req in requirements):
                    self.warnings.append(f"Не найден пакет в requirements.txt: {package}")
                else:
                    self.logger.debug(f"✅ Пакет найден в requirements: {package}")
                    
        except Exception as e:
            self.errors.append(f"Ошибка при чтении requirements.txt: {e}")
    
    def _validate_credentials(self):
        """Валидация файла credentials"""
        credentials_path = Path('config/credentials.json')
        
        if not credentials_path.exists():
            self.warnings.append(
                "Файл config/credentials.json не найден. "
                "Он необходим для работы с Google API. "
                "См. docs/API_SETUP.md"
            )
            return
        
        try:
            with open(credentials_path, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
            
            # Проверяем тип credentials
            if 'type' in credentials:
                if credentials['type'] == 'service_account':
                    self._validate_service_account_credentials(credentials)
                else:
                    self.warnings.append(f"Неизвестный тип credentials: {credentials['type']}")
            elif 'client_id' in credentials:
                self._validate_oauth_credentials(credentials)
            else:
                self.errors.append("Неопознанный формат credentials.json")
                
        except json.JSONDecodeError as e:
            self.errors.append(f"Некорректный JSON в credentials.json: {e}")
        except Exception as e:
            self.errors.append(f"Ошибка при чтении credentials.json: {e}")
    
    def _validate_service_account_credentials(self, credentials: Dict):
        """Валидация Service Account credentials"""
        required_fields = [
            'type', 'project_id', 'private_key_id', 'private_key',
            'client_email', 'client_id', 'auth_uri', 'token_uri'
        ]
        
        missing_fields = [field for field in required_fields if field not in credentials]
        
        if missing_fields:
            self.errors.append(
                f"Отсутствуют обязательные поля в Service Account credentials: {missing_fields}"
            )
        else:
            self.logger.debug("✅ Service Account credentials корректны")
            
        # Проверяем DOMAIN_ADMIN_EMAIL
        domain_admin_email = os.getenv('DOMAIN_ADMIN_EMAIL')
        if not domain_admin_email:
            self.warnings.append(
                "Не установлена переменная окружения DOMAIN_ADMIN_EMAIL. "
                "Она необходима для Domain-wide delegation."
            )
    
    def _validate_oauth_credentials(self, credentials: Dict):
        """Валидация OAuth2 credentials"""
        if 'installed' in credentials:
            oauth_creds = credentials['installed']
        elif 'web' in credentials:
            oauth_creds = credentials['web']
        else:
            self.errors.append("Некорректная структура OAuth2 credentials")
            return
        
        required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
        missing_fields = [field for field in required_fields if field not in oauth_creds]
        
        if missing_fields:
            self.errors.append(
                f"Отсутствуют обязательные поля в OAuth2 credentials: {missing_fields}"
            )
        else:
            self.logger.debug("✅ OAuth2 credentials корректны")
    
    def _validate_configuration(self):
        """Валидация конфигурационных файлов"""
        config_files = [
            'config/settings.json.template',
            'config/credentials.json.template'
        ]
        
        for config_file in config_files:
            if not Path(config_file).exists():
                self.warnings.append(f"Отсутствует шаблон конфигурации: {config_file}")
    
    def _validate_permissions(self):
        """Валидация прав доступа"""
        # Проверяем права на запись в текущую директорию
        try:
            test_file = Path('.test_write_permission')
            test_file.write_text('test')
            test_file.unlink()
            self.logger.debug("✅ Права на запись в рабочую директорию")
        except Exception:
            self.errors.append("Недостаточно прав для записи в рабочую директорию")
        
        # Проверяем возможность создания директории logs
        logs_dir = Path('logs')
        try:
            logs_dir.mkdir(exist_ok=True)
            self.logger.debug("✅ Права на создание директории logs")
        except Exception:
            self.warnings.append("Невозможно создать директорию logs")
    
    def get_validation_report(self) -> str:
        """Получение отчета о валидации"""
        report_lines = [
            "=" * 60,
            "ОТЧЕТ О ВАЛИДАЦИИ ОКРУЖЕНИЯ",
            "=" * 60,
            ""
        ]
        
        if not self.errors and not self.warnings:
            report_lines.extend([
                "✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО",
                "",
                "Окружение готово для работы приложения."
            ])
        else:
            if self.errors:
                report_lines.extend([
                    f"❌ КРИТИЧЕСКИЕ ОШИБКИ ({len(self.errors)}):",
                    ""
                ])
                for i, error in enumerate(self.errors, 1):
                    report_lines.append(f"{i}. {error}")
                report_lines.append("")
            
            if self.warnings:
                report_lines.extend([
                    f"⚠️ ПРЕДУПРЕЖДЕНИЯ ({len(self.warnings)}):",
                    ""
                ])
                for i, warning in enumerate(self.warnings, 1):
                    report_lines.append(f"{i}. {warning}")
                report_lines.append("")
            
            if self.errors:
                report_lines.extend([
                    "РЕКОМЕНДАЦИИ:",
                    "• Устраните критические ошибки перед запуском",
                    "• Проверьте структуру проекта и зависимости",
                    "• Следуйте инструкциям в docs/API_SETUP.md",
                    ""
                ])
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
