#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Кастомные исключения для Admin Team Tools.
"""

class AdminToolsError(Exception):
    """Базовое исключение для Admin Team Tools"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ConfigurationError(AdminToolsError):
    """Ошибки конфигурации приложения"""
    pass

class CredentialsError(AdminToolsError):
    """Ошибки аутентификации и credentials"""
    pass

class GoogleAPIError(AdminToolsError):
    """Ошибки Google API"""
    pass

class NetworkError(AdminToolsError):
    """Сетевые ошибки"""
    pass

class PermissionError(AdminToolsError):
    """Ошибки прав доступа"""
    pass

class ValidationError(AdminToolsError):
    """Ошибки валидации данных"""
    pass

class ServiceAccountError(CredentialsError):
    """Ошибки Service Account"""
    pass

class DomainDelegationError(ServiceAccountError):
    """Ошибки Domain-wide delegation"""
    pass

class UserNotFoundError(AdminToolsError):
    """Пользователь не найден"""
    pass

class GroupNotFoundError(AdminToolsError):
    """Группа не найдена"""
    pass

class HealthCheckError(AdminToolsError):
    """Ошибки проверки здоровья системы"""
    pass
