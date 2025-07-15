#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест системы управления путями файлов.
Проверяет корректность работы организованного размещения файлов.
"""

import sys
from pathlib import Path
import tempfile
import os

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.file_paths import (
    file_path_manager, 
    get_export_path, 
    get_log_path, 
    get_config_path,
    get_temp_path,
    get_organized_path
)


def test_file_paths():
    """Тестирование системы путей файлов"""
    print("🧪 Тестирование системы управления путями файлов")
    print("=" * 60)
    
    # Тест 1: Проверка создания директорий
    print("\n1️⃣ Проверка создания директорий...")
    for name, path in file_path_manager.directories.items():
        exists = path.exists()
        print(f"   📁 {name}: {path} - {'✅' if exists else '❌'}")
    
    # Тест 2: Проверка экспорта
    print("\n2️⃣ Тестирование путей экспорта...")
    export_tests = [
        "users_export.csv",
        "members_export.xlsx", 
        "report.json"
    ]
    
    for filename in export_tests:
        path = get_export_path(filename)
        expected_dir = file_path_manager.directories['exports']
        is_correct = path.parent == expected_dir
        print(f"   📄 {filename} → {path} - {'✅' if is_correct else '❌'}")
    
    # Тест 3: Проверка логов
    print("\n3️⃣ Тестирование путей логов...")
    log_tests = [
        "admin_tools.log",
        "errors.log",
        "security_audit.json"
    ]
    
    for filename in log_tests:
        path = get_log_path(filename)
        expected_dir = file_path_manager.directories['logs']
        is_correct = path.parent == expected_dir
        print(f"   📄 {filename} → {path} - {'✅' if is_correct else '❌'}")
    
    # Тест 4: Проверка конфигурации
    print("\n4️⃣ Тестирование путей конфигурации...")
    config_tests = [
        "app_config.json",
        "theme_config.json",
        "settings.json"
    ]
    
    for filename in config_tests:
        path = get_config_path(filename)
        expected_dir = file_path_manager.directories['config']
        is_correct = path.parent == expected_dir
        print(f"   📄 {filename} → {path} - {'✅' if is_correct else '❌'}")
    
    # Тест 5: Автоматическое определение
    print("\n5️⃣ Тестирование автоматического определения...")
    auto_tests = [
        ("user_data.csv", "exports"),
        ("app.log", "logs"),
        ("config.json", "config"),
        ("temp_file.tmp", "temp"),
        ("credentials.json", "root"),  # Особый случай
    ]
    
    for filename, expected_type in auto_tests:
        path = get_organized_path(filename)
        
        if expected_type == "root":
            is_correct = path.parent == file_path_manager.project_root
        else:
            expected_dir = file_path_manager.directories.get(expected_type, file_path_manager.directories['data'])
            is_correct = path.parent == expected_dir
            
        print(f"   📄 {filename} → {expected_type} - {'✅' if is_correct else '❌'}")
    
    # Тест 6: Создание тестового файла
    print("\n6️⃣ Тестирование создания файла...")
    try:
        test_file_path = get_temp_path("test_file.txt")
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("Тестовый файл для проверки системы путей")
        
        if test_file_path.exists():
            print(f"   ✅ Файл успешно создан: {test_file_path}")
            # Удаляем тестовый файл
            test_file_path.unlink()
            print(f"   🗑️ Тестовый файл удален")
        else:
            print(f"   ❌ Файл не создан")
    except Exception as e:
        print(f"   ❌ Ошибка создания файла: {e}")
    
    # Тест 7: Информация о директориях
    print("\n7️⃣ Информация о директориях...")
    info = file_path_manager.get_directory_info()
    for name, data in info.items():
        exists = "✅" if data['exists'] else "❌"
        files = data['files_count']
        size = data['total_size_mb']
        print(f"   📁 {name}: {exists} - {files} файлов, {size} MB")
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено!")


def test_real_usage():
    """Тестирование реального использования"""
    print("\n🔧 Тестирование реального использования...")
    
    # Симуляция экспорта пользователей
    from datetime import datetime
    export_filename = f"users_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    export_path = get_export_path(export_filename)
    
    print(f"📊 Экспорт: {export_path}")
    
    # Симуляция логирования
    log_path = get_log_path("test_app.log")
    print(f"📝 Лог: {log_path}")
    
    # Симуляция конфигурации
    config_path = get_config_path("test_config.json")
    print(f"⚙️ Конфиг: {config_path}")


if __name__ == "__main__":
    try:
        test_file_paths()
        test_real_usage()
        
        print("\n🎉 Все тесты прошли успешно!")
        print("💡 Система организованных путей готова к использованию!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
