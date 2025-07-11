#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка с Nuitka для минимального размера
"""

import os
import sys
import subprocess
import shutil

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

def build_with_nuitka():
    """Сборка с Nuitka"""
    print("🚀 Сборка с Nuitka для минимального размера")
    print("="*50)
    
    # Очистка
    if os.path.exists('AdminTeamTools.exe'):
        os.remove('AdminTeamTools.exe')
    if os.path.exists('AdminTeamTools.dist'):
        shutil.rmtree('AdminTeamTools.dist')
    
    # Команда Nuitka
    nuitka_cmd = [
        'python', '-m', 'nuitka',
        '--onefile',
        '--windows-disable-console',
        '--assume-yes-for-downloads',
        '--output-filename=AdminTeamTools.exe',
        'main_optimized.py'
    ]
    
    if run_command(' '.join(nuitka_cmd), "Сборка с Nuitka"):
        if os.path.exists('AdminTeamTools.exe'):
            size = get_file_size('AdminTeamTools.exe')
            print(f"📦 Размер Nuitka: {size:.1f} MB")
            
            # Попробуем сжать UPX
            upx_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 
                                   'Microsoft', 'WinGet', 'Packages', 
                                   'UPX.UPX_Microsoft.Winget.Source_8wekyb3d8bbwe',
                                   'upx-5.0.1-win64', 'upx.exe')
            
            if os.path.exists(upx_path):
                print("\n🔧 Применяем UPX сжатие...")
                upx_cmd = f'"{upx_path}" --best --force "AdminTeamTools.exe"'
                if run_command(upx_cmd, "Сжатие с UPX"):
                    compressed_size = get_file_size('AdminTeamTools.exe')
                    compression_ratio = (size - compressed_size) / size * 100
                    print(f"📦 Размер после UPX: {compressed_size:.1f} MB")
                    print(f"💾 Экономия: {compression_ratio:.1f}%")
                    print(f"🎉 Финальный размер: {compressed_size:.1f} MB")
                else:
                    print(f"🎉 Финальный размер: {size:.1f} MB")
            else:
                print(f"🎉 Финальный размер: {size:.1f} MB")
                
            return True
        else:
            print("❌ Файл exe не создан")
            return False
    else:
        print("❌ Сборка с Nuitka не удалась")
        return False

if __name__ == "__main__":
    success = build_with_nuitka()
    if success:
        print("\n🎉 Сборка с Nuitka успешна!")
    else:
        print("\n❌ Сборка с Nuitka не удалась!")
        sys.exit(1)
