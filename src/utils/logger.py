# -*- coding: utf-8 -*-
"""
Утилиты для логирования и журналирования активности приложения.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class Logger:
    """
    Класс для логирования событий приложения.
    """
    
    def __init__(self, log_file: str = 'admin_log.json'):
        self.log_file = log_file
        self.ensure_log_file_exists()
    
    def ensure_log_file_exists(self):
        """Создает файл логов если он не существует"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def log(self, message: str, level: str = 'INFO', category: str = 'GENERAL'):
        """
        Записывает сообщение в лог.
        
        Args:
            message: Текст сообщения
            level: Уровень логирования (INFO, WARNING, ERROR, DEBUG)
            category: Категория события (API, USER, GROUP, SYSTEM, etc.)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'category': category,
            'message': message
        }
        
        try:
            # Читаем существующие логи
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Добавляем новую запись
            logs.append(log_entry)
            
            # Ограничиваем количество записей (последние 1000)
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Сохраняем обновленные логи
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Ошибка записи в лог: {e}")
    
    def get_logs(self, level: Optional[str] = None, 
                 category: Optional[str] = None, 
                 limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Получает записи из лога с фильтрацией.
        
        Args:
            level: Фильтр по уровню логирования
            category: Фильтр по категории
            limit: Ограничение количества записей
            
        Returns:
            Список записей лога
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Фильтрация
            if level:
                logs = [log for log in logs if log.get('level') == level]
            
            if category:
                logs = [log for log in logs if log.get('category') == category]
            
            # Ограничение количества
            if limit:
                logs = logs[-limit:]
            
            return logs
            
        except Exception as e:
            print(f"Ошибка чтения лога: {e}")
            return []
    
    def clear_logs(self):
        """Очищает файл логов"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        except Exception as e:
            print(f"Ошибка очистки лога: {e}")
    
    def info(self, message: str, category: str = 'GENERAL'):
        """Записывает информационное сообщение"""
        self.log(message, 'INFO', category)
    
    def warning(self, message: str, category: str = 'GENERAL'):
        """Записывает предупреждение"""
        self.log(message, 'WARNING', category)
    
    def error(self, message: str, category: str = 'GENERAL'):
        """Записывает ошибку"""
        self.log(message, 'ERROR', category)
    
    def debug(self, message: str, category: str = 'GENERAL'):
        """Записывает отладочное сообщение"""
        self.log(message, 'DEBUG', category)


# Глобальный экземпляр логгера
logger = Logger()


def log_api_call(operation: str, success: bool, details: str = ''):
    """
    Логирует вызов API.
    
    Args:
        operation: Название операции (например, 'create_user', 'list_groups')
        success: Успешность операции
        details: Дополнительные детали
    """
    level = 'INFO' if success else 'ERROR'
    status = 'SUCCESS' if success else 'FAILED'
    message = f"API {operation}: {status}"
    if details:
        message += f" - {details}"
    
    logger.log(message, level, 'API')


def log_user_action(action: str, user_email: str, details: str = ''):
    """
    Логирует действие пользователя.
    
    Args:
        action: Тип действия (например, 'created', 'updated', 'deleted')
        user_email: Email пользователя
        details: Дополнительные детали
    """
    message = f"User {action}: {user_email}"
    if details:
        message += f" - {details}"
    
    logger.log(message, 'INFO', 'USER')


def log_group_action(action: str, group_email: str, details: str = ''):
    """
    Логирует действие с группой.
    
    Args:
        action: Тип действия (например, 'created', 'updated', 'deleted')
        group_email: Email группы
        details: Дополнительные детали
    """
    message = f"Group {action}: {group_email}"
    if details:
        message += f" - {details}"
    
    logger.log(message, 'INFO', 'GROUP')


def log_system_event(event: str, details: str = ''):
    """
    Логирует системное событие.
    
    Args:
        event: Тип события
        details: Дополнительные детали
    """
    message = f"System event: {event}"
    if details:
        message += f" - {details}"
    
    logger.log(message, 'INFO', 'SYSTEM')


def log_error(error_message: str, category: str = 'GENERAL', details: str = ''):
    """
    Логирует ошибку.
    
    Args:
        error_message: Сообщение об ошибке
        category: Категория ошибки
        details: Дополнительные детали
    """
    message = f"Error: {error_message}"
    if details:
        message += f" - {details}"
    
    logger.log(message, 'ERROR', category)
