#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилита для работы с путями ресурсов в PyInstaller bundle.
"""

import sys
import os
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """
    Получить абсолютный путь к ресурсу, работает как в dev, так и в PyInstaller bundle.
    
    Для конфиденциальных файлов (credentials.json, token.pickle, .env)
    приоритет отдается файлам рядом с exe, а не внутри bundle.
    
    Args:
        relative_path: Относительный путь к ресурсу
        
    Returns:
        Абсолютный путь к ресурсу
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Запущен из PyInstaller bundle
        exe_dir = Path(sys.executable).parent
        
        # Список конфиденциальных файлов, которые должны быть рядом с exe
        confidential_files = [
            'credentials.json',
            'token.pickle', 
            '.env',
            'config/credentials.json',
            'config/token.pickle'
        ]
        
        # Для конфиденциальных файлов всегда используем папку рядом с exe
        if any(conf_file in relative_path for conf_file in confidential_files):
            return exe_dir / relative_path
        
        # Для остальных файлов - стандартная логика
        bundle_dir = Path(sys._MEIPASS)
        
        # Проверяем сначала рядом с exe
        resource_path = exe_dir / relative_path
        if resource_path.exists():
            return resource_path
            
        # Затем в bundle
        resource_path = bundle_dir / relative_path
        if resource_path.exists():
            return resource_path
            
        # Если не найден, возвращаем путь рядом с exe (для создания)
        return exe_dir / relative_path
    else:
        # Обычный запуск из исходников
        # Определяем корень проекта (3 уровня вверх от текущего файла)
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        return project_root / relative_path


def get_base_dir() -> Path:
    """
    Получить базовую директорию приложения.
    
    Returns:
        Базовая директория (папка с exe для bundle, корень проекта для dev)
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller bundle - папка с exe
        return Path(sys.executable).parent
    else:
        # Обычный запуск - корень проекта
        current_file = Path(__file__).resolve()
        return current_file.parent.parent.parent


def is_bundled() -> bool:
    """
    Проверить, запущено ли приложение из PyInstaller bundle.
    
    Returns:
        True если запущено из bundle
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def ensure_resource_dir(relative_path: str) -> Path:
    """
    Убедиться, что директория для ресурса существует, и создать её если нужно.
    
    Args:
        relative_path: Относительный путь к директории
        
    Returns:
        Абсолютный путь к директории
    """
    resource_path = get_resource_path(relative_path)
    if resource_path.is_file():
        # Если это файл, берем его родительскую директорию
        resource_path = resource_path.parent
    
    resource_path.mkdir(parents=True, exist_ok=True)
    return resource_path


def copy_resource_if_missing(relative_path: str, default_content: str = None) -> Path:
    """
    Скопировать ресурс рядом с exe, если его там нет.
    
    Args:
        relative_path: Относительный путь к ресурсу
        default_content: Содержимое по умолчанию, если файл нужно создать
        
    Returns:
        Абсолютный путь к ресурсу
    """
    resource_path = get_resource_path(relative_path)
    
    if not resource_path.exists() and default_content is not None:
        # Создаем директорию если нужно
        resource_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Создаем файл с содержимым по умолчанию
        with open(resource_path, 'w', encoding='utf-8') as f:
            f.write(default_content)
    
    return resource_path
