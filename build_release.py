#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сборки exe файла Admin Team Tools
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def clean_build():
    """Очистка предыдущих сборок"""
    print("🧹 Очистка предыдущих сборок...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✅ Удалена папка: {dir_name}")

def build_exe():
    """Сборка exe файла"""
    print("🔨 Начинаем сборку exe файла...")
    
    try:
        # Запускаем PyInstaller с нашей спецификацией
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller', 
            '--clean', 
            'AdminTeamTools.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Сборка завершена успешно!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def create_release_folder():
    """Создание папки релиза"""
    print("📦 Создание релизной папки...")
    
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # Копируем exe файл
    exe_source = Path("dist/AdminTeamTools.exe")
    if exe_source.exists():
        shutil.copy2(exe_source, release_dir / "AdminTeamTools.exe")
        print("   ✅ Скопирован AdminTeamTools.exe")
    else:
        print("   ❌ Файл AdminTeamTools.exe не найден!")
        return False
    
    # Копируем важные файлы
    files_to_copy = [
        "README.md",
        "LICENSE", 
        "CHANGELOG.md",
        "credentials_oauth2_template.json"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, release_dir / file_name)
            print(f"   ✅ Скопирован {file_name}")
    
    # Копируем документацию
    docs_source = Path("docs")
    docs_dest = release_dir / "docs"
    if docs_source.exists():
        shutil.copytree(docs_source, docs_dest)
        print("   ✅ Скопирована папка docs")
    
    # Создаем README для релиза
    create_release_readme(release_dir)
    
    print(f"📁 Релиз создан в папке: {release_dir.absolute()}")
    return True

def create_release_readme(release_dir):
    """Создание README для релиза"""
    readme_content = """# 🚀 Admin Team Tools v2.0.6 - Release

## 📋 Что включено в релиз

- **AdminTeamTools.exe** - Готовое к использованию приложение
- **docs/** - Полная документация
- **README.md** - Описание проекта
- **LICENSE** - Лицензия MIT
- **CHANGELOG.md** - История изменений
- **credentials_oauth2_template.json** - Шаблон для настройки

## 🚀 Быстрый старт

### 1. Настройка Google API

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект или выберите существующий
3. Включите Admin SDK API и Calendar API
4. Создайте OAuth 2.0 Client ID (Desktop application)
5. Скачайте credentials.json и поместите рядом с AdminTeamTools.exe

### 2. Запуск приложения

1. Поместите credentials.json в папку с AdminTeamTools.exe
2. Запустите AdminTeamTools.exe
3. При первом запуске откроется браузер для авторизации
4. Войдите под администраторским аккаунтом Google Workspace
5. Разрешите доступ к API
6. Приложение запустится автоматически

## 📖 Подробная документация

- **docs/OAUTH2_SETUP.md** - Настройка Google API
- **docs/USER_GUIDE.md** - Руководство пользователя
- **docs/API_SETUP.md** - Подробная настройка API

## ✨ Возможности

- 👥 Управление пользователями Google Workspace
- 🔒 Управление группами и правами
- 📅 Управление календарями
- 🎨 3 темы оформления
- ⌨️ Горячие клавиши
- 📊 Экспорт в Excel/CSV

## 🆘 Поддержка

Если возникли проблемы:

1. Проверьте настройки Google API (docs/OAUTH2_SETUP.md)
2. Убедитесь, что ваш аккаунт имеет права администратора
3. Проверьте интернет-соединение
4. Создайте issue в GitHub репозитории

---

**Admin Team Tools v2.0.6** | MIT License | Создано с ❤️
"""
    
    with open(release_dir / "README_RELEASE.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✅ Создан README_RELEASE.md")

def main():
    """Основная функция сборки"""
    print("🎯 Сборка Admin Team Tools v2.0.6")
    print("=" * 50)
    
    # Проверяем, что мы в правильной папке
    if not os.path.exists("main.py"):
        print("❌ Ошибка: main.py не найден. Запустите скрипт из корневой папки проекта.")
        sys.exit(1)
    
    # Этапы сборки
    clean_build()
    
    if not build_exe():
        print("❌ Сборка не удалась!")
        sys.exit(1)
    
    if not create_release_folder():
        print("❌ Создание релиза не удалось!")
        sys.exit(1)
    
    print("\n🎉 Релиз готов!")
    print("📁 Файлы находятся в папке: release/")
    print("🚀 Можно публиковать на GitHub!")

if __name__ == "__main__":
    main()
