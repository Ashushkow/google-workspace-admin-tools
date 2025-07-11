#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Централизованный обработчик ошибок для Admin Team Tools.
"""

import logging
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Any
import traceback
import sys
from pathlib import Path

from .exceptions import (
    AdminToolsError, ConfigurationError, CredentialsError, 
    GoogleAPIError, NetworkError, PermissionError, 
    ServiceAccountError, DomainDelegationError
)
from .enhanced_logger import log_exception

class ErrorHandler:
    """Централизованный обработчик ошибок"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_count = 0
        self.max_errors = 10  # Максимум ошибок перед аварийным выходом
        
    def handle_exception(self, exception: Exception, context: str = "", 
                        show_dialog: bool = True, exit_on_critical: bool = True) -> bool:
        """
        Обработка исключения с логированием и пользовательским интерфейсом
        
        Args:
            exception: Исключение для обработки
            context: Контекст, где произошла ошибка
            show_dialog: Показывать ли диалог пользователю
            exit_on_critical: Выходить ли при критических ошибках
            
        Returns:
            True если ошибка обработана успешно, False если нужно прервать выполнение
        """
        
        self.error_count += 1
        
        # Логируем исключение
        log_exception(self.logger, exception, context)
        
        # Определяем тип ошибки и соответствующую реакцию
        if isinstance(exception, CredentialsError):
            return self._handle_credentials_error(exception, show_dialog)
        elif isinstance(exception, ServiceAccountError):
            return self._handle_service_account_error(exception, show_dialog)
        elif isinstance(exception, DomainDelegationError):
            return self._handle_domain_delegation_error(exception, show_dialog)
        elif isinstance(exception, GoogleAPIError):
            return self._handle_google_api_error(exception, show_dialog)
        elif isinstance(exception, NetworkError):
            return self._handle_network_error(exception, show_dialog)
        elif isinstance(exception, ConfigurationError):
            return self._handle_configuration_error(exception, show_dialog)
        elif isinstance(exception, PermissionError):
            return self._handle_permission_error(exception, show_dialog)
        elif isinstance(exception, FileNotFoundError):
            return self._handle_file_not_found_error(exception, show_dialog)
        elif isinstance(exception, ImportError):
            return self._handle_import_error(exception, show_dialog)
        else:
            return self._handle_generic_error(exception, context, show_dialog, exit_on_critical)
    
    def _handle_credentials_error(self, exception: CredentialsError, show_dialog: bool) -> bool:
        """Обработка ошибок аутентификации"""
        self.logger.error(f"Ошибка аутентификации: {exception}")
        
        if show_dialog:
            messagebox.showerror(
                "Ошибка аутентификации",
                f"Проблема с файлом credentials.json:\n{exception.message}\n\n"
                "Решение:\n"
                "1. Проверьте наличие файла credentials.json\n"
                "2. Убедитесь в правильности его содержимого\n"
                "3. Следуйте инструкции: docs/API_SETUP.md\n\n"
                f"Код ошибки: {exception.error_code or 'CRED_001'}"
            )
        return False
    
    def _handle_service_account_error(self, exception: ServiceAccountError, show_dialog: bool) -> bool:
        """Обработка ошибок Service Account"""
        self.logger.error(f"Ошибка Service Account: {exception}")
        
        if show_dialog:
            messagebox.showerror(
                "Ошибка Service Account",
                f"{exception.message}\n\n"
                "Возможные причины:\n"
                "• Неправильно настроен DOMAIN_ADMIN_EMAIL\n"
                "• Service Account не имеет необходимых прав\n"
                "• Не настроена Domain-wide delegation\n\n"
                "Инструкция: docs/SERVICE_ACCOUNT_SETUP.md\n\n"
                f"Код ошибки: {exception.error_code or 'SA_001'}"
            )
        return False
    
    def _handle_domain_delegation_error(self, exception: DomainDelegationError, show_dialog: bool) -> bool:
        """Обработка ошибок Domain-wide delegation"""
        self.logger.error(f"Ошибка Domain-wide delegation: {exception}")
        
        if show_dialog:
            messagebox.showerror(
                "Ошибка Domain-wide delegation",
                f"Проблема с правами Service Account:\n{exception.message}\n\n"
                "Необходимо:\n"
                "1. Включить Domain-wide delegation в Google Cloud Console\n"
                "2. Добавить необходимые OAuth scopes в Admin Console\n"
                "3. Убедиться, что DOMAIN_ADMIN_EMAIL корректен\n\n"
                "Подробная инструкция: docs/SERVICE_ACCOUNT_SETUP.md\n\n"
                f"Код ошибки: {exception.error_code or 'DD_001'}"
            )
        return False
    
    def _handle_google_api_error(self, exception: GoogleAPIError, show_dialog: bool) -> bool:
        """Обработка ошибок Google API"""
        self.logger.error(f"Ошибка Google API: {exception}")
        
        if show_dialog:
            messagebox.showerror(
                "Ошибка Google API",
                f"Проблема при вызове Google API:\n{exception.message}\n\n"
                "Возможные причины:\n"
                "• Превышен лимит запросов (quota)\n"
                "• Недостаточно прав доступа\n"
                "• Временная недоступность сервиса\n"
                "• Неправильные параметры запроса\n\n"
                f"Код ошибки: {exception.error_code or 'API_001'}"
            )
        return True  # Можно продолжить работу
    
    def _handle_network_error(self, exception: NetworkError, show_dialog: bool) -> bool:
        """Обработка сетевых ошибок"""
        self.logger.error(f"Сетевая ошибка: {exception}")
        
        if show_dialog:
            messagebox.showerror(
                "Сетевая ошибка",
                f"Проблема с подключением:\n{exception.message}\n\n"
                "Проверьте:\n"
                "• Интернет-соединение\n"
                "• Настройки прокси/файрволла\n"
                "• Доступность сервисов Google\n\n"
                f"Код ошибки: {exception.error_code or 'NET_001'}"
            )
        return True  # Можно попробовать повторить операцию
    
    def _handle_configuration_error(self, exception: ConfigurationError, show_dialog: bool) -> bool:
        """Обработка ошибок конфигурации"""
        self.logger.error(f"Ошибка конфигурации: {exception}")
        
        if show_dialog:
            messagebox.showerror(
                "Ошибка конфигурации",
                f"Проблема с настройками:\n{exception.message}\n\n"
                "Проверьте:\n"
                "• Файлы конфигурации\n"
                "• Переменные окружения\n"
                "• Структуру проекта\n\n"
                f"Код ошибки: {exception.error_code or 'CONF_001'}"
            )
        return False
    
    def _handle_permission_error(self, exception: PermissionError, show_dialog: bool) -> bool:
        """Обработка ошибок прав доступа"""
        self.logger.error(f"Ошибка прав доступа: {exception}")
        
        if show_dialog:
            messagebox.showerror(
                "Ошибка прав доступа",
                f"Недостаточно прав:\n{exception}\n\n"
                "Решение:\n"
                "• Запустите приложение от имени администратора\n"
                "• Проверьте права доступа к файлам\n"
                "• Убедитесь в корректности настроек Google API"
            )
        return False
    
    def _handle_file_not_found_error(self, exception: FileNotFoundError, show_dialog: bool) -> bool:
        """Обработка ошибок отсутствующих файлов"""
        self.logger.error(f"Файл не найден: {exception}")
        
        if show_dialog:
            filename = str(exception).split("'")[1] if "'" in str(exception) else "неизвестный файл"
            messagebox.showerror(
                "Файл не найден",
                f"Не найден файл: {filename}\n\n"
                "Возможные причины:\n"
                "• Файл не был создан или удален\n"
                "• Неправильный путь к файлу\n"
                "• Недостаточно прав доступа\n\n"
                "Если это credentials.json, следуйте: docs/API_SETUP.md"
            )
        return False
    
    def _handle_import_error(self, exception: ImportError, show_dialog: bool) -> bool:
        """Обработка ошибок импорта модулей"""
        self.logger.error(f"Ошибка импорта: {exception}")
        
        if show_dialog:
            module_name = str(exception).split("'")[1] if "'" in str(exception) else "неизвестный модуль"
            messagebox.showerror(
                "Ошибка импорта модулей",
                f"Не удалось импортировать: {module_name}\n\n"
                "Возможные причины:\n"
                "• Не установлены зависимости (pip install -r requirements.txt)\n"
                "• Поврежден файл модуля\n"
                "• Неправильная структура проекта\n\n"
                "Попробуйте переустановить зависимости."
            )
        return False
    
    def _handle_generic_error(self, exception: Exception, context: str, 
                            show_dialog: bool, exit_on_critical: bool) -> bool:
        """Обработка общих ошибок"""
        self.logger.critical(f"Необработанная ошибка в {context}: {exception}")
        
        if show_dialog:
            messagebox.showerror(
                "Критическая ошибка",
                f"Произошла непредвиденная ошибка:\n{str(exception)}\n\n"
                f"Контекст: {context}\n"
                f"Тип: {type(exception).__name__}\n\n"
                "Информация сохранена в logs/errors.log\n"
                "Пожалуйста, сообщите об этой ошибке разработчикам."
            )
        
        # Проверяем количество ошибок
        if self.error_count >= self.max_errors:
            self.logger.critical(f"Достигнуто максимальное количество ошибок ({self.max_errors})")
            if show_dialog:
                messagebox.showerror(
                    "Критическая ситуация",
                    f"Приложение столкнулось с {self.error_count} ошибками.\n"
                    "Для безопасности выполнение будет прервано.\n\n"
                    "Проверьте логи и конфигурацию перед повторным запуском."
                )
            return False
        
        return not exit_on_critical
    
    def create_error_report(self, exception: Exception, context: str) -> str:
        """Создание детального отчета об ошибке"""
        report = [
            "=" * 60,
            "ОТЧЕТ ОБ ОШИБКЕ",
            "=" * 60,
            f"Время: {self.logger.handlers[0].formatter.formatTime(None)}",
            f"Контекст: {context}",
            f"Тип исключения: {type(exception).__name__}",
            f"Сообщение: {str(exception)}",
            "",
            "ТРАССИРОВКА:",
            traceback.format_exc(),
            "",
            "ИНФОРМАЦИЯ О СИСТЕМЕ:",
            f"Python: {sys.version}",
            f"Платформа: {sys.platform}",
            f"Рабочая директория: {Path.cwd()}",
            "=" * 60
        ]
        
        return "\n".join(report)
