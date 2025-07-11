#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления импортов в ручных тестах после реорганизации
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Исправляет импорты в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем есть ли уже правильный путь
        if 'sys.path.insert(0, str(Path(__file__).parent.parent.parent))' in content:
            print(f"✅ {file_path.name} - импорты уже исправлены")
            return True
            
        # Ищем паттерн для добавления пути
        pattern = r'sys\.path\.insert\(0, str\(Path\(__file__\)\.parent\)\)'
        if re.search(pattern, content):
            # Заменяем неправильный путь на правильный
            content = re.sub(
                pattern, 
                'sys.path.insert(0, str(Path(__file__).parent.parent.parent))', 
                content
            )
        else:
            # Добавляем путь после импортов sys и os
            insert_pos = content.find('from pathlib import Path')
            if insert_pos == -1:
                insert_pos = content.find('import os')
                if insert_pos == -1:
                    print(f"❌ {file_path.name} - не найдено место для вставки пути")
                    return False
            
            # Находим конец строки
            end_pos = content.find('\n', insert_pos)
            if end_pos == -1:
                end_pos = len(content)
            
            # Вставляем код добавления пути
            path_code = '\n\n# Добавляем корневую папку в путь для импорта\nsys.path.insert(0, str(Path(__file__).parent.parent.parent))\n'
            content = content[:end_pos] + path_code + content[end_pos:]
        
        # Записываем обратно
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ {file_path.name} - импорты исправлены")
        return True
        
    except Exception as e:
        print(f"❌ {file_path.name} - ошибка: {e}")
        return False

def main():
    """Основная функция"""
    print("🔧 Исправление импортов в ручных тестах...")
    print("=" * 50)
    
    manual_tests_dir = Path(__file__).parent.parent / 'tests' / 'manual'
    
    if not manual_tests_dir.exists():
        print("❌ Папка tests/manual не найдена")
        return
    
    # Находим все Python файлы тестов
    test_files = list(manual_tests_dir.glob('test_*.py'))
    
    if not test_files:
        print("❌ Не найдено тестовых файлов")
        return
    
    print(f"📁 Найдено {len(test_files)} тестовых файлов")
    print()
    
    success_count = 0
    for test_file in test_files:
        if fix_imports_in_file(test_file):
            success_count += 1
    
    print()
    print("=" * 50)
    print(f"✅ Обработано: {success_count}/{len(test_files)} файлов")
    print("🎉 Исправление импортов завершено!")

if __name__ == "__main__":
    main()
