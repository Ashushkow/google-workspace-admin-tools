#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления импортов после реорганизации папок
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Исправляет импорты в указанном файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Определяем папку файла для правильных относительных импортов
    if 'src/ui/' in str(file_path):
        # Для файлов в src/ui/
        content = re.sub(r'^from ui_components import', 'from .ui_components import', content, flags=re.MULTILINE)
        content = re.sub(r'^from user_windows import', 'from .user_windows import', content, flags=re.MULTILINE)
        content = re.sub(r'^from additional_windows import', 'from .additional_windows import', content, flags=re.MULTILINE)
        content = re.sub(r'^from employee_list_window import', 'from .employee_list_window import', content, flags=re.MULTILINE)
        content = re.sub(r'^from group_management import', 'from .group_management import', content, flags=re.MULTILINE)
        content = re.sub(r'^from users_api import', 'from ..api.users_api import', content, flags=re.MULTILINE)
        content = re.sub(r'^from groups_api import', 'from ..api.groups_api import', content, flags=re.MULTILINE)
        content = re.sub(r'^from simple_utils import', 'from ..utils.simple_utils import', content, flags=re.MULTILINE)
        content = re.sub(r'^from data_cache import', 'from ..utils.data_cache import', content, flags=re.MULTILINE)
        
    elif 'src/api/' in str(file_path):
        # Для файлов в src/api/
        content = re.sub(r'^from data_cache import', 'from ..utils.data_cache import', content, flags=re.MULTILINE)
        content = re.sub(r'^from config import', 'from ..config import', content, flags=re.MULTILINE)
        
    elif 'src/utils/' in str(file_path):
        # Для файлов в src/utils/
        content = re.sub(r'^from config import', 'from ..config import', content, flags=re.MULTILINE)
    
    # Сохраняем файл только если были изменения
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Исправлены импорты в: {file_path}")
        return True
    return False

def main():
    """Основная функция"""
    project_root = Path(__file__).parent
    src_dir = project_root / 'src'
    
    fixed_count = 0
    
    # Исправляем импорты во всех Python файлах в src/
    for py_file in src_dir.rglob('*.py'):
        if py_file.name != '__init__.py':
            if fix_imports_in_file(py_file):
                fixed_count += 1
    
    print(f"\nИсправлено файлов: {fixed_count}")
    print("Импорты обновлены для новой структуры папок!")

if __name__ == "__main__":
    main()
