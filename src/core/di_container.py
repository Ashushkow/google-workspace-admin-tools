#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система внедрения зависимостей для Admin Team Tools.
"""

from typing import Dict, Any, Type, TypeVar, Callable, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
import inspect

T = TypeVar('T')

class ServiceNotFoundError(Exception):
    """Исключение, когда сервис не найден в контейнере"""
    pass

class CircularDependencyError(Exception):
    """Исключение при циклических зависимостях"""
    pass

@dataclass
class ServiceDescriptor:
    """Описание сервиса в контейнере"""
    service_type: Type
    implementation: Type
    singleton: bool = True
    factory: Optional[Callable] = None
    instance: Optional[Any] = None

class DIContainer:
    """Контейнер для внедрения зависимостей"""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._resolving: set = set()
    
    def register(self, service_type: Type[T], implementation: Type[T] = None, 
                singleton: bool = True, factory: Callable = None) -> 'DIContainer':
        """
        Регистрирует сервис в контейнере
        
        Args:
            service_type: Тип сервиса (обычно интерфейс)
            implementation: Реализация сервиса
            singleton: Использовать singleton паттерн
            factory: Фабрика для создания экземпляра
        """
        if implementation is None:
            implementation = service_type
        
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            singleton=singleton,
            factory=factory
        )
        
        self._services[service_type] = descriptor
        return self
    
    def register_instance(self, service_type: Type[T], instance: T) -> 'DIContainer':
        """Регистрирует готовый экземпляр сервиса"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=type(instance),
            singleton=True,
            instance=instance
        )
        
        self._services[service_type] = descriptor
        return self
    
    def resolve(self, service_type: Type[T]) -> T:
        """
        Разрешает зависимость и возвращает экземпляр сервиса
        
        Args:
            service_type: Тип сервиса для разрешения
            
        Returns:
            Экземпляр сервиса
        """
        if service_type in self._resolving:
            raise CircularDependencyError(f"Циклическая зависимость для {service_type}")
        
        if service_type not in self._services:
            raise ServiceNotFoundError(f"Сервис {service_type} не зарегистрирован")
        
        descriptor = self._services[service_type]
        
        # Если уже есть экземпляр singleton
        if descriptor.singleton and descriptor.instance is not None:
            return descriptor.instance
        
        # Создаем новый экземпляр
        self._resolving.add(service_type)
        try:
            instance = self._create_instance(descriptor)
            
            if descriptor.singleton:
                descriptor.instance = instance
            
            return instance
        finally:
            self._resolving.discard(service_type)
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Создает экземпляр сервиса"""
        if descriptor.factory:
            return descriptor.factory()
        
        # Анализируем конструктор
        constructor = descriptor.implementation.__init__
        sig = inspect.signature(constructor)
        
        # Подготавливаем аргументы
        args = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = param.annotation
            if param_type != inspect.Parameter.empty:
                args[param_name] = self.resolve(param_type)
        
        return descriptor.implementation(**args)
    
    def is_registered(self, service_type: Type) -> bool:
        """Проверяет, зарегистрирован ли сервис"""
        return service_type in self._services

# Глобальный контейнер
container = DIContainer()

def inject(service_type: Type[T]) -> T:
    """
    Декоратор для внедрения зависимостей
    
    Args:
        service_type: Тип сервиса для внедрения
        
    Returns:
        Экземпляр сервиса
    """
    return container.resolve(service_type)

def injectable(cls: Type[T]) -> Type[T]:
    """
    Декоратор для классов, которые могут быть внедрены
    
    Args:
        cls: Класс для регистрации
        
    Returns:
        Тот же класс (для совместимости)
    """
    container.register(cls)
    return cls

def service(service_type: Type = None, singleton: bool = True):
    """
    Декоратор для регистрации сервисов
    
    Args:
        service_type: Тип сервиса (интерфейс)
        singleton: Использовать singleton паттерн
    """
    def decorator(cls: Type[T]) -> Type[T]:
        target_type = service_type or cls
        container.register(target_type, cls, singleton=singleton)
        return cls
    
    return decorator

# Интерфейсы для основных сервисов
class ILogger(ABC):
    """Интерфейс для логгера"""
    
    @abstractmethod
    def info(self, message: str): pass
    
    @abstractmethod
    def error(self, message: str): pass
    
    @abstractmethod
    def warning(self, message: str): pass
    
    @abstractmethod
    def debug(self, message: str): pass

class IConfigService(ABC):
    """Интерфейс для сервиса конфигурации"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any: pass
    
    @abstractmethod
    def set(self, key: str, value: Any): pass

class IGoogleAPIService(ABC):
    """Интерфейс для Google API сервиса"""
    
    @abstractmethod
    def get_users(self) -> list: pass
    
    @abstractmethod
    def get_groups(self) -> list: pass
    
    @abstractmethod
    def create_user(self, user_data: dict) -> dict: pass

class ICacheService(ABC):
    """Интерфейс для сервиса кэширования"""
    
    @abstractmethod
    def get(self, key: str) -> Any: pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = None): pass
    
    @abstractmethod
    def delete(self, key: str): pass

# Пример регистрации сервисов
def setup_services():
    """Настройка сервисов в контейнере"""
    from .utils.enhanced_logger import EnhancedLogger
    from .config.enhanced_config import ConfigManager
    from .api.google_api_service import GoogleAPIService
    from .utils.cache import CacheService
    
    container.register(ILogger, EnhancedLogger)
    container.register(IConfigService, ConfigManager)
    container.register(IGoogleAPIService, GoogleAPIService)
    container.register(ICacheService, CacheService)
