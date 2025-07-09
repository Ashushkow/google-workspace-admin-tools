"""
Декораторы для централизованной обработки ошибок UI
"""
from functools import wraps
from tkinter import messagebox
from typing import Callable, Any, Optional
import re
import time
from functools import lru_cache


def handle_service_errors(operation_name: str, require_service: bool = True):
    """
    Декоратор для обработки ошибок операций, требующих подключения к сервису
    
    Args:
        operation_name: Название операции для логирования
        require_service: Требуется ли подключение к сервису
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Проверка подключения к сервису
            if require_service and not self.service:
                messagebox.showwarning(
                    'Предупреждение', 
                    'Нет подключения к Google API'
                )
                self.log_activity(f'Отклонено {operation_name}: нет подключения к API', 'WARNING')
                return None
                
            try:
                result = func(self, *args, **kwargs)
                self.log_activity(f'{operation_name} выполнено успешно', 'SUCCESS')
                return result
                
            except Exception as e:
                error_msg = f'Ошибка {operation_name.lower()}: {str(e)}'
                self.log_activity(error_msg, 'ERROR')
                messagebox.showerror(
                    'Ошибка', 
                    f'Не удалось {operation_name.lower()}:\n{str(e)}'
                )
                return None
                
        return wrapper
    return decorator


def handle_ui_errors(operation_name: str, show_success: bool = False):
    """
    Декоратор для обработки ошибок UI операций (не требующих сервиса)
    
    Args:
        operation_name: Название операции для логирования
        show_success: Показывать ли сообщение об успехе
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            try:
                result = func(self, *args, **kwargs)
                
                if show_success:
                    self.log_activity(f'{operation_name} выполнено успешно', 'SUCCESS')
                    
                return result
                
            except Exception as e:
                error_msg = f'Ошибка {operation_name.lower()}: {str(e)}'
                self.log_activity(error_msg, 'ERROR')
                messagebox.showerror(
                    'Ошибка', 
                    f'Не удалось {operation_name.lower()}:\n{str(e)}'
                )
                return None
                
        return wrapper
    return decorator


def log_operation(operation_name: str, level: str = 'INFO'):
    """
    Декоратор для простого логирования операций
    
    Args:
        operation_name: Название операции
        level: Уровень логирования
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            result = func(self, *args, **kwargs)
            self.log_activity(operation_name, level)
            return result
        return wrapper
    return decorator


def validate_input(validator: Callable[[Any], bool], error_message: str):
    """
    Декоратор для валидации входных данных
    
    Args:
        validator: Функция валидации
        error_message: Сообщение об ошибке
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Валидируем первый аргумент (обычно это данные для обработки)
            if args and not validator(args[0]):
                messagebox.showwarning('Валидация', error_message)
                self.log_activity(f'Валидация не прошла: {error_message}', 'WARNING')
                return None
                
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def validate_email(func: Callable) -> Callable:
    """
    Декоратор для валидации email адресов
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        # Ищем email в аргументах
        email = None
        if args and isinstance(args[0], str) and '@' in args[0]:
            email = args[0]
        elif 'email' in kwargs:
            email = kwargs['email']
            
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                messagebox.showerror('Ошибка валидации', f'Некорректный email адрес: {email}')
                self.log_activity(f'Некорректный email: {email}', 'WARNING')
                return None
                
        return func(self, *args, **kwargs)
    return wrapper


def require_confirmation(message: str = "Вы уверены, что хотите выполнить эту операцию?"):
    """
    Декоратор для запроса подтверждения операции
    
    Args:
        message: Сообщение для подтверждения
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            if not messagebox.askyesno('Подтверждение', message):
                self.log_activity('Операция отменена пользователем', 'INFO')
                return None
                
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def measure_performance(func: Callable) -> Callable:
    """
    Декоратор для измерения времени выполнения операции
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        self.log_activity(
            f'Операция {func.__name__} выполнена за {execution_time:.2f} сек', 
            'PERFORMANCE'
        )
        
        return result
    return wrapper


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """
    Декоратор для повторных попыток при ошибках
    
    Args:
        max_attempts: Максимальное количество попыток
        delay: Задержка между попытками в секундах
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    self.log_activity(
                        f'Попытка {attempt + 1}/{max_attempts} неудачна: {str(e)}', 
                        'WARNING'
                    )
                    
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    
            # Если все попытки неудачны
            self.log_activity(
                f'Все {max_attempts} попыток неудачны для {func.__name__}', 
                'ERROR'
            )
            messagebox.showerror(
                'Ошибка', 
                f'Операция не выполнена после {max_attempts} попыток:\n{str(last_exception)}'
            )
            return None
            
        return wrapper
    return decorator


def cache_result(maxsize: int = 128):
    """
    Декоратор для кэширования результатов операций
    
    Args:
        maxsize: Максимальный размер кэша
    """
    def decorator(func: Callable) -> Callable:
        @lru_cache(maxsize=maxsize)
        def cached_func(*args, **kwargs):
            return func(*args, **kwargs)
            
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            # Создаем ключ для кэша (исключаем self)
            cache_key = (args, tuple(sorted(kwargs.items())))
            
            try:
                result = cached_func(*args, **kwargs)
                self.log_activity(f'Результат {func.__name__} взят из кэша', 'CACHE')
                return result
            except TypeError:
                # Если аргументы не хэшируемы, выполняем без кэширования
                self.log_activity(f'Кэширование недоступно для {func.__name__}', 'INFO')
                return func(self, *args, **kwargs)
                
        return wrapper
    return decorator
