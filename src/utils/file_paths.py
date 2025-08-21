#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль управления путями файлов для организованной структуры проекта.
Обеспечивает правильное размещение файлов в соответствующих директориях.
"""

import os
from pathlib import Path
from typing import Dict, Union


class FilePathManager:
    """Менеджер путей файлов для организованной структуры проекта"""
    
    def __init__(self, project_root: Union[str, Path] = None):
        """
        Инициализация менеджера путей
        
        Args:
            project_root: Корневая директория проекта
        """
        if project_root is None:
            # Определяем корень проекта автоматически
            current_file = Path(__file__).resolve()
            self.project_root = current_file.parent.parent.parent
        else:
            self.project_root = Path(project_root).resolve()
        
        # Определяем основные директории
        self.directories = {
            'logs': self.project_root / 'logs',
            'data': self.project_root / 'data', 
            'cache': self.project_root / 'cache',
            'temp': self.project_root / 'temp',
            'config': self.project_root / 'config',
            'exports': self.project_root / 'data' / 'exports',
            'reports': self.project_root / 'data' / 'reports',
            'tests': self.project_root / 'tests',
            'test_logs': self.project_root / 'tests' / 'logs',
            'test_data': self.project_root / 'tests' / 'data',
            'docs': self.project_root / 'docs',
            'docs_reports': self.project_root / 'docs' / 'reports',
            'docs_guides': self.project_root / 'docs' / 'guides',
            'themes': self.project_root / 'config' / 'themes',
            'security': self.project_root / 'data' / 'security'
        }
        
        # Автоматически создаем необходимые директории
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        """Создает необходимые директории если они не существуют"""
        for dir_path in self.directories.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_file_path(self, file_type: str, filename: str) -> Path:
        """
        Получить правильный путь для файла в зависимости от его типа
        
        Args:
            file_type: Тип файла (logs, exports, config, etc.)
            filename: Имя файла
            
        Returns:
            Полный путь к файлу
        """
        file_type = file_type.lower()
        
        # Определяем правильную директорию на основе типа файла
        if file_type in self.directories:
            return self.directories[file_type] / filename
        
        # Автоматическое определение на основе расширения и имени файла
        lower_filename = filename.lower()
        
        # Файлы логирования
        if any(keyword in lower_filename for keyword in ['log', 'audit']):
            return self.directories['logs'] / filename
            
        # Файлы экспорта
        elif any(ext in lower_filename for ext in ['.csv', '.xlsx', '.json']):
            if any(keyword in lower_filename for keyword in ['export', 'data', 'user', 'member']):
                return self.directories['exports'] / filename
            else:
                return self.directories['data'] / filename
            
        # Файлы конфигурации
        elif any(keyword in lower_filename for keyword in ['config', 'settings', 'theme']):
            return self.directories['config'] / filename
            
        # Файлы безопасности
        elif any(keyword in lower_filename for keyword in ['credentials', 'token', 'key', 'cert']):
            # Хранение секретов в каталоге безопасности, путь можно переопределить через конфиг
            return self.directories['security'] / filename
            
        # Тестовые файлы
        elif any(keyword in lower_filename for keyword in ['test', 'demo', 'mock']):
            return self.directories['test_data'] / filename
            
        # Временные файлы
        elif any(keyword in lower_filename for keyword in ['temp', 'tmp', 'cache']):
            return self.directories['temp'] / filename
            
        # По умолчанию - в data
        else:
            return self.directories['data'] / filename
    
    def get_export_path(self, filename: str) -> Path:
        """Получить путь для файла экспорта"""
        return self.get_file_path('exports', filename)
    
    def get_log_path(self, filename: str) -> Path:
        """Получить путь для файла логов"""
        return self.get_file_path('logs', filename)
    
    def get_config_path(self, filename: str) -> Path:
        """Получить путь для файла конфигурации"""
        return self.get_file_path('config', filename)
    
    def get_data_path(self, filename: str) -> Path:
        """Получить путь для файла данных"""
        return self.get_file_path('data', filename)
    
    def get_temp_path(self, filename: str) -> Path:
        """Получить путь для временного файла"""
        return self.get_file_path('temp', filename)
    
    def get_test_path(self, filename: str) -> Path:
        """Получить путь для тестового файла"""
        return self.get_file_path('test_data', filename)
    
    def get_theme_config_path(self, filename: str) -> Path:
        """Получить путь для файла конфигурации темы"""
        return self.get_file_path('themes', filename)
    
    def get_security_path(self, filename: str) -> Path:
        """Получить путь для файла безопасности"""
        return self.get_file_path('security', filename)
    
    def suggest_save_location(self, filename: str, file_purpose: str = None) -> Path:
        """
        Предложить местоположение для сохранения файла
        
        Args:
            filename: Имя файла
            file_purpose: Назначение файла (optional)
            
        Returns:
            Рекомендуемый путь для сохранения
        """
        if file_purpose:
            purpose_mapping = {
                'export': 'exports',
                'report': 'reports', 
                'log': 'logs',
                'config': 'config',
                'theme': 'themes',
                'test': 'test_data',
                'temp': 'temp',
                'cache': 'cache',
                'security': 'security'
            }
            
            file_type = purpose_mapping.get(file_purpose.lower(), 'data')
            return self.get_file_path(file_type, filename)
        
        return self.get_file_path('data', filename)
    
    def clean_temp_files(self, max_age_hours: int = 24):
        """
        Очистка временных файлов старше указанного времени
        
        Args:
            max_age_hours: Максимальный возраст файлов в часах
        """
        import time
        
        temp_dirs = [self.directories['temp'], self.directories['cache']]
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                for file_path in temp_dir.iterdir():
                    if file_path.is_file():
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > max_age_seconds:
                            try:
                                file_path.unlink()
                                print(f"Удален старый временный файл: {file_path}")
                            except Exception as e:
                                print(f"Ошибка удаления файла {file_path}: {e}")
    
    def get_directory_info(self) -> Dict[str, Dict]:
        """Получить информацию о директориях проекта"""
        info = {}
        
        for name, path in self.directories.items():
            files_count = 0
            total_size = 0
            
            if path.exists():
                try:
                    for file_path in path.rglob('*'):
                        if file_path.is_file():
                            files_count += 1
                            total_size += file_path.stat().st_size
                except PermissionError:
                    pass
            
            info[name] = {
                'path': str(path),
                'exists': path.exists(),
                'files_count': files_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        
        return info


# Глобальный экземпляр менеджера путей
file_path_manager = FilePathManager()


def get_organized_path(filename: str, file_type: str = None) -> Path:
    """
    Удобная функция для получения организованного пути к файлу
    
    Args:
        filename: Имя файла
        file_type: Тип файла (logs, exports, config, etc.)
        
    Returns:
        Правильный путь к файлу
    """
    return file_path_manager.get_file_path(file_type or 'data', filename)


def get_export_path(filename: str) -> Path:
    """Получить путь для экспорта файла"""
    return file_path_manager.get_export_path(filename)


def get_log_path(filename: str) -> Path:
    """Получить путь для файла логов"""
    return file_path_manager.get_log_path(filename)


def get_config_path(filename: str) -> Path:
    """Получить путь для файла конфигурации"""
    return file_path_manager.get_config_path(filename)


def get_temp_path(filename: str) -> Path:
    """Получить путь для временного файла"""
    return file_path_manager.get_temp_path(filename)
