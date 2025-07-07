# -*- coding: utf-8 -*-
"""
Централизованная система обработки ошибок с автоматическим восстановлением.
"""

import traceback
import functools
import time
from typing import Callable, Any, Optional, Dict
from datetime import datetime
from googleapiclient.errors import HttpError
import tkinter as tk
from tkinter import messagebox


class ErrorHandler:
    """
    Централизованный обработчик ошибок с логированием и уведомлениями.
    """
    
    def __init__(self):
        self.error_log: list = []
        self.retry_configs: Dict[str, Dict] = {
            'api_call': {'max_retries': 3, 'delay': 1, 'backoff': 2},
            'network': {'max_retries': 5, 'delay': 2, 'backoff': 1.5},
            'file_operation': {'max_retries': 2, 'delay': 0.5, 'backoff': 1}
        }
    
    def log_error(self, error: Exception, context: str = "", 
                  severity: str = "ERROR", user_message: str = ""):
        """
        Логирует ошибку с контекстом.
        
        Args:
            error: Исключение
            context: Контекст возникновения ошибки
            severity: Уровень серьезности
            user_message: Сообщение для пользователя
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'severity': severity,
            'traceback': traceback.format_exc(),
            'user_message': user_message
        }
        
        self.error_log.append(error_entry)
        
        # Ограничиваем размер лога
        if len(self.error_log) > 500:
            self.error_log = self.error_log[-500:]
        
        # Выводим в консоль для отладки
        print(f"[{severity}] {context}: {error}")
        
        return error_entry
    
    def handle_api_error(self, error: HttpError, context: str = "") -> str:
        """
        Специальная обработка ошибок Google API.
        
        Args:
            error: HTTP ошибка от Google API
            context: Контекст операции
            
        Returns:
            Пользовательское сообщение об ошибке
        """
        if hasattr(error, 'resp') and error.resp:
            status_code = error.resp.status
            
            if status_code == 403:
                user_msg = "Недостаточно прав для выполнения операции"
            elif status_code == 404:
                user_msg = "Запрашиваемый ресурс не найден"
            elif status_code == 429:
                user_msg = "Превышен лимит запросов к API. Попробуйте позже"
            elif status_code >= 500:
                user_msg = "Внутренняя ошибка сервера Google. Попробуйте позже"
            else:
                user_msg = f"Ошибка API (код {status_code})"
        else:
            user_msg = "Неизвестная ошибка API"
        
        self.log_error(error, context, "ERROR", user_msg)
        return user_msg
    
    def with_retry(self, retry_type: str = 'api_call'):
        """
        Декоратор для автоматического повтора операций при ошибках.
        
        Args:
            retry_type: Тип операции для определения настроек повтора
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                config = self.retry_configs.get(retry_type, self.retry_configs['api_call'])
                max_retries = config['max_retries']
                delay = config['delay']
                backoff = config['backoff']
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries:
                            # Последняя попытка - логируем ошибку
                            self.log_error(
                                e, 
                                f"{func.__name__} (попытка {attempt + 1}/{max_retries + 1})"
                            )
                            raise
                        
                        # Не последняя попытка - ждем и повторяем
                        print(f"Попытка {attempt + 1} неудачна для {func.__name__}: {e}")
                        time.sleep(delay)
                        delay *= backoff
                
            return wrapper
        return decorator
    
    def safe_execute(self, func: Callable, *args, 
                    error_message: str = "Произошла ошибка", **kwargs) -> tuple:
        """
        Безопасное выполнение функции с обработкой ошибок.
        
        Args:
            func: Функция для выполнения
            error_message: Сообщение об ошибке для пользователя
            *args, **kwargs: Аргументы для функции
            
        Returns:
            Tuple (success: bool, result: Any)
        """
        try:
            result = func(*args, **kwargs)
            return True, result
        except Exception as e:
            self.log_error(e, func.__name__, user_message=error_message)
            return False, None
    
    def show_error_dialog(self, parent: tk.Tk, error_entry: Dict, 
                         show_details: bool = False):
        """
        Показывает диалог с информацией об ошибке.
        
        Args:
            parent: Родительское окно
            error_entry: Запись об ошибке
            show_details: Показывать ли технические детали
        """
        if show_details:
            details = f"\nТип: {error_entry['error_type']}\n"
            details += f"Время: {error_entry['timestamp']}\n"
            details += f"Контекст: {error_entry['context']}\n"
            details += f"Детали: {error_entry['error_message']}"
            
            message = error_entry.get('user_message', 'Произошла ошибка') + details
        else:
            message = error_entry.get('user_message', 'Произошла ошибка')
        
        messagebox.showerror("Ошибка", message, parent=parent)
    
    def get_error_statistics(self) -> Dict:
        """Возвращает статистику ошибок"""
        if not self.error_log:
            return {}
        
        total_errors = len(self.error_log)
        error_types = {}
        severities = {}
        
        for entry in self.error_log:
            error_type = entry['error_type']
            severity = entry['severity']
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
            severities[severity] = severities.get(severity, 0) + 1
        
        return {
            'total_errors': total_errors,
            'error_types': error_types,
            'severities': severities,
            'last_error_time': self.error_log[-1]['timestamp']
        }


# Глобальный экземпляр обработчика ошибок
error_handler = ErrorHandler()
