#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенная система логирования для Admin Team Tools.
"""

import logging
import logging.handlers
import os
import sys
import platform
from datetime import datetime
from pathlib import Path

from .file_paths import get_log_path

try:
    import colorama
    COLORAMA_AVAILABLE = True
except Exception:
    COLORAMA_AVAILABLE = False

class ColoredFormatter(logging.Formatter):
    """Цветной форматтер для консольного вывода"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m', # Red background
    }
    RESET = '\033[0m'

    def format(self, record):
        win = platform.system().lower().startswith('win')
        if sys.stdout.isatty() and (not win or COLORAMA_AVAILABLE):
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    """
    Настройка системы логирования с ротацией файлов
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Директория для файлов логов
    
    Returns:
        Настроенный logger
    """
    
    # Создаем директорию для логов
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Основной logger
    logger = logging.getLogger('admin_tools')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Очищаем существующие handlers
    logger.handlers.clear()
    
    # Форматтер для файлов
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Форматтер для консоли
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Ротирующийся файл для всех логов
    main_log_file = get_log_path('admin_tools.log')
    main_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    main_handler.setFormatter(file_formatter)
    main_handler.setLevel(logging.DEBUG)
    
    # Отдельный файл для ошибок
    error_log_file = get_log_path('errors.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5 * 1024 * 1024,   # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Инициализируем colorama на Windows для корректных цветов
    if COLORAMA_AVAILABLE:
        try:
            colorama.just_fix_windows_console()
        except Exception:
            pass
    
    # Добавляем handlers
    logger.addHandler(main_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    # Логируем старт приложения
    logger.info("=" * 50)
    logger.info(f"Admin Tools запущен в {datetime.now()}")
    logger.info(f"Уровень логирования: {log_level.upper()}")
    logger.info(f"Логи сохраняются в: {log_path.absolute()}")
    logger.info("=" * 50)
    
    return logger

def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    Логирование исключения с контекстом
    
    Args:
        logger: Logger для записи
        exception: Исключение для логирования
        context: Дополнительный контекст
    """
    logger.error(
        f"Исключение в {context}: {type(exception).__name__}: {str(exception)}",
        exc_info=True
    )
