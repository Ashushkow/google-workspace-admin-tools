#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания релиза v2.0.3 в git
"""

import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            if result.stdout.strip():
                print(f"   Результат: {result.stdout.strip()}")
        else:
            print(f"❌ {description} - ошибка")
            print(f"   Ошибка: {result.stderr.strip()}")
            return False
        return True
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False

def main():
    """Основная функция релиза"""
    print("🚀 Подготовка релиза Admin Team Tools v2.0.3")
    print("=" * 50)
    
    # Проверяем наличие git
    if not run_command("git --version", "Проверка git"):
        print("\n❌ Git не установлен. Установите git и попробуйте снова.")
        return False
    
    # Проверяем статус репозитория
    if not run_command("git status", "Проверка статуса репозитория"):
        return False
    
    # Добавляем все файлы
    if not run_command("git add .", "Добавление всех файлов"):
        return False
    
    # Создаем коммит
    commit_message = "feat: Release v2.0.3 - Организованная структура и исправления"
    if not run_command(f'git commit -m "{commit_message}"', "Создание коммита"):
        return False
    
    # Создаем тег
    tag_message = "v2.0.3 - Организованная структура файлов и исправления импортов"
    if not run_command(f'git tag -a v2.0.3 -m "{tag_message}"', "Создание тега"):
        return False
    
    # Пушим изменения
    if not run_command("git push origin main", "Отправка изменений"):
        return False
    
    # Пушим теги
    if not run_command("git push origin --tags", "Отправка тегов"):
        return False
    
    print("\n🎉 Релиз v2.0.3 успешно создан!")
    print("✅ Все изменения отправлены в репозиторий")
    print("✅ Создан тег v2.0.3")
    print("\n📋 Что включено в релиз:")
    print("   • Организованная структура папок")
    print("   • Исправленные импорты модулей")
    print("   • Обновленная документация")
    print("   • Готовая к использованию версия")
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
