#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания компактного exe-файла Admin Team Tools
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_step(step, message):
    """Печать этапа сборки"""
    print(f"\n{'='*50}")
    print(f"ЭТАП {step}: {message}")
    print(f"{'='*50}")

def get_file_size(file_path):
    """Получение размера файла в MB"""
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb
    return 0

def run_command(command, description):
    """Выполнение команды с обработкой ошибок"""
    print(f"\n🔧 {description}")
    print(f"Команда: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Успешно")
            return True
        else:
            print(f"❌ Ошибка: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

def clean_build_dirs():
    """Очистка директорий сборки"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️  Очищена папка: {dir_name}")

def check_upx():
    """Проверка наличия UPX"""
    try:
        upx_path = os.path.join(os.environ['LOCALAPPDATA'], 
                               'Microsoft', 'WinGet', 'Packages', 
                               'UPX.UPX_Microsoft.Winget.Source_8wekyb3d8bbwe',
                               'upx-5.0.1-win64', 'upx.exe')
        
        if os.path.exists(upx_path):
            result = subprocess.run([upx_path, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ UPX найден")
                return upx_path
    except:
        pass
    
    # Пробуем стандартный upx
    try:
        result = subprocess.run(['upx', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ UPX найден")
            return 'upx'
    except:
        pass
    
    print("❌ UPX не найден")
    return None

def build_exe():
    """Основная функция сборки"""
    print_step(1, "ПОДГОТОВКА")
    
    # Проверяем наличие основных файлов
    if not os.path.exists('main_optimized.py'):
        print("❌ Файл main_optimized.py не найден")
        return False
    
    if not os.path.exists('requirements.txt'):
        print("❌ Файл requirements.txt не найден")
        return False
    
    print("✅ Основные файлы найдены")
    
    # Очистка
    clean_build_dirs()
    
    print_step(2, "СБОРКА БАЗОВОГО EXE")
    
    # Команда PyInstaller с максимальными исключениями
    pyinstaller_cmd = [
        'pyinstaller',
        '--onefile',
        '--noconsole',
        '--clean',
        '--optimize=2',
        '--exclude-module=PIL',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=IPython',
        '--exclude-module=jupyter',
        '--exclude-module=notebook',
        '--exclude-module=PyQt5',
        '--exclude-module=PySide2',
        '--exclude-module=tkinter.test',
        '--exclude-module=test',
        '--exclude-module=unittest',
        '--exclude-module=doctest',
        '--exclude-module=pdb',
        '--exclude-module=pydoc',
        '--exclude-module=xmlrpc',
        '--name=AdminTeamTools',
        'main_optimized.py'
    ]
    
    if not run_command(' '.join(pyinstaller_cmd), "Сборка с PyInstaller"):
        return False
    
    exe_path = 'dist/AdminTeamTools.exe'
    if not os.path.exists(exe_path):
        print("❌ Файл exe не создан")
        return False
    
    original_size = get_file_size(exe_path)
    print(f"📦 Размер до сжатия: {original_size:.1f} MB")
    
    print_step(3, "СЖАТИЕ С UPX")
    
    # UPX сжатие
    upx_path = check_upx()
    if upx_path:
        upx_cmd = f'"{upx_path}" --best --force "{exe_path}"'
        if run_command(upx_cmd, "Сжатие с UPX"):
            compressed_size = get_file_size(exe_path)
            compression_ratio = (original_size - compressed_size) / original_size * 100
            print(f"📦 Размер после сжатия: {compressed_size:.1f} MB")
            print(f"💾 Экономия: {compression_ratio:.1f}%")
        else:
            print("⚠️  Сжатие не удалось, но exe работает")
    else:
        print("⚠️  UPX недоступен, сжатие пропущено")
        print("💡 Для установки UPX:")
        print("   1. Скачайте с https://upx.github.io/")
        print("   2. Распакуйте и добавьте в PATH")
    
    print_step(4, "ФИНАЛИЗАЦИЯ")
    
    final_size = get_file_size(exe_path)
    print(f"🎉 Готовый файл: {exe_path}")
    print(f"📦 Финальный размер: {final_size:.1f} MB")
    
    # Копируем в корень для удобства
    final_exe = 'AdminTeamTools.exe'
    if os.path.exists(final_exe):
        os.remove(final_exe)
    shutil.copy2(exe_path, final_exe)
    print(f"📁 Копия создана: {final_exe}")
    
    print_step("✅", "СБОРКА ЗАВЕРШЕНА")
    print(f"🚀 Запускайте: {final_exe}")
    print(f"📦 Размер: {final_size:.1f} MB")
    
    return True

if __name__ == "__main__":
    success = build_exe()
    if success:
        print("\n🎉 Сборка успешна!")
    else:
        print("\n❌ Сборка не удалась!")
        sys.exit(1)