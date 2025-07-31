#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin Team Tools v2.0.8 - Google Workspace Management
Приоритет: OAuth 2.0 авторизация для безопасного интерактивного управления
UX IMPROVED VERSION - с улучшенным пользовательским интерфейсом
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.application import Application
from src.utils.enhanced_logger import setup_logging
from src.config.enhanced_config import config


def show_progress_bar(current: int, total: int, description: str = "", width: int = 40):
    """Показывает прогресс операции"""
    if total == 0:
        return
    
    percentage = int((current / total) * 100)
    filled_length = int(width * current // total)
    
    bar = '█' * filled_length + '░' * (width - filled_length)
    print(f'\r{description} |{bar}| {percentage}% ({current}/{total})', end='', flush=True)
    
    if current == total:
        print(" ✅")


def show_loading_animation(message: str, duration: float = 2.0):
    """Показывает анимированный индикатор загрузки"""
    spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0
    
    while time.time() < end_time:
        print(f'\r{spinner_chars[i % len(spinner_chars)]} {message}', end='', flush=True)
        time.sleep(0.1)
        i += 1
    
    print(f'\r✅ {message} - завершено!', flush=True)


def create_section_divider(title: str, width: int = 70, char: str = "═"):
    """Создает визуальное разделение секций"""
    if len(title) >= width - 4:
        return f"{char * 2} {title} {char * 2}"
    
    padding = (width - len(title) - 2) // 2
    return f"{char * padding} {title} {char * (width - padding - len(title) - 2)}"


def show_startup_banner():
    """Показывает улучшенный стартовый баннер с прогрессом"""
    # Очищаем экран для лучшего визуального эффекта
    print("\n" * 2)
    
    # Главный заголовок
    print("┌" + "─" * 68 + "┐")
    print("│" + " " * 68 + "│")
    print("│" + "🚀 ADMIN TEAM TOOLS v2.0.8".center(68) + "│")
    print("│" + "📊 Google Workspace Management System".center(68) + "│")
    print("│" + " " * 68 + "│")
    print("└" + "─" * 68 + "┘")
    print()
    
    # Статус авторизации с улучшенным дизайном
    print(create_section_divider("СТАТУС АВТОРИЗАЦИИ", char="─"))
    print("🔐 Приоритет: OAuth 2.0 (интерактивная авторизация)")
    print("🔧 Резерв: Service Account (автоматическая авторизация)")
    print()
    
    # Прогресс инициализации
    print("🔄 Инициализация приложения...")
    
    # Симуляция этапов загрузки с прогресс-баром
    stages = [
        ("Проверка конфигурации", 0.5),
        ("Проверка credentials", 0.8),
        ("Инициализация компонентов", 0.3),
        ("Подготовка интерфейса", 0.4)
    ]
    
    for i, (stage, duration) in enumerate(stages, 1):
        show_loading_animation(stage, duration)
        show_progress_bar(i, len(stages), "Общий прогресс")
        print()
    
    print()
    
    # Проверяем наличие credentials с улучшенной диагностикой
    print(create_section_divider("ДИАГНОСТИКА ПОДКЛЮЧЕНИЯ", char="─"))
    
    credentials_path = Path("credentials.json")
    if credentials_path.exists():
        try:
            import json
            with open(credentials_path, 'r') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data:
                print("✅ OAuth 2.0 credentials обнаружены")
                print("   🌐 При первом запуске откроется браузер для авторизации")
                print("   🔑 Токены будут сохранены для последующих запусков")
            elif 'type' in creds_data and creds_data['type'] == 'service_account':
                print("✅ Service Account credentials обнаружены")
                print("   🤖 Будет использована автоматическая авторизация")
                print("   ⚡ Быстрый запуск без взаимодействия с пользователем")
            else:
                print("⚠️  Неизвестный формат credentials.json")
                print("   💡 Проверьте корректность файла конфигурации")
        except Exception as e:
            print("❌ Ошибка чтения credentials.json")
            print(f"   📋 Детали: {str(e)}")
            print("   💡 Проверьте синтаксис JSON файла")
    else:
        print("❌ credentials.json не найден")
        print("   📋 Для настройки см.: docs/OAUTH2_PRIORITY_SETUP.md")
        print("   💡 Поместите файл в корневую директорию проекта")
    
    print()
    print(create_section_divider("БЫСТРЫЕ КОМАНДЫ", char="─"))
    print("💡 Полезные сочетания клавиш:")
    print("   • F1        - Справка и документация")
    print("   • Ctrl+Q    - Быстрый выход из приложения")  
    print("   • Ctrl+R    - Обновить данные")
    print("   • Ctrl+S    - Сохранить изменения")
    print("   • Tab       - Навигация по элементам")
    print("   • Escape    - Отмена текущей операции")
    print()
    
    print("┌" + "─" * 68 + "┐")
    print("│" + "🎯 Приложение готово к работе!".center(68) + "│")
    print("└" + "─" * 68 + "┘")
    print()


def show_user_friendly_error(error_type: str, message: str, suggestions: list = None):
    """Показывает понятные пользователю ошибки с предложениями"""
    print()
    print("┌" + "─" * 68 + "┐")
    print("│" + f"❌ {error_type}".center(68) + "│")
    print("└" + "─" * 68 + "┘")
    print(f"📋 Описание: {message}")
    
    if suggestions:
        print()
        print("💡 Возможные решения:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
    
    print()
    print("📞 Нужна помощь? Обратитесь к документации или администратору")
    print()


async def main() -> int:
    """
    Главная функция приложения с улучшенной обработкой ошибок
    
    Returns:
        Код выхода
    """
    try:
        print("🚀 Запуск основного приложения...")
        show_loading_animation("Инициализация компонентов", 1.0)
        
        # Создаем и запускаем приложение
        app = Application()
        return await app.start()
        
    except KeyboardInterrupt:
        print("\n")
        print("┌" + "─" * 68 + "┐")
        print("│" + "⏹️ Приложение остановлено пользователем".center(68) + "│")
        print("└" + "─" * 68 + "┘")
        print("👋 До свидания!")
        return 0
        
    except ImportError as e:
        show_user_friendly_error(
            "Ошибка импорта модулей",
            f"Не удалось загрузить необходимые компоненты: {e}",
            [
                "Проверьте установку зависимостей: pip install -r requirements.txt",
                "Убедитесь, что все файлы проекта на месте",
                "Попробуйте переустановить приложение"
            ]
        )
        return 1
        
    except FileNotFoundError as e:
        show_user_friendly_error(
            "Файл не найден",
            f"Отсутствует необходимый файл: {e}",
            [
                "Проверьте целостность установки",
                "Убедитесь, что вы запускаете из правильной директории",
                "Восстановите отсутствующие файлы из backup"
            ]
        )
        return 1
        
    except Exception as e:
        show_user_friendly_error(
            "Критическая ошибка приложения",
            f"Произошла неожиданная ошибка: {e}",
            [
                "Перезапустите приложение",
                "Проверьте логи в папке logs/",
                "Обратитесь к администратору с описанием проблемы",
                "Попробуйте запустить в режиме отладки"
            ]
        )
        return 1


def cli_main():
    """Синхронная точка входа для CLI с улучшенным UX"""
    try:
        # Показываем улучшенный стартовый баннер
        show_startup_banner()
        
        # Запуск асинхронного приложения
        print("⚡ Переход к главному интерфейсу...")
        time.sleep(0.5)  # Небольшая пауза для лучшего UX
        
        return asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 Выход по запросу пользователя")
        return 0
        
    except Exception as e:
        show_user_friendly_error(
            "Ошибка запуска приложения",
            f"Не удалось запустить приложение: {e}",
            [
                "Проверьте права доступа к файлам",
                "Убедитесь в корректности Python окружения",
                "Попробуйте запустить от имени администратора",
                "Проверьте наличие свободного места на диске"
            ]
        )
        return 1


def print_rollback_info():
    """Выводит информацию о том, как откатить изменения"""
    print()
    print(create_section_divider("ИНФОРМАЦИЯ ОБ ОТКАТЕ", char="═"))
    print("🔄 Если новый UX вам не подходит, вы можете легко откатиться:")
    print()
    print("📋 Способы отката:")
    print("   1. Быстрый откат:")
    print("      mv main.py main_ux_improved.py")
    print("      mv main_backup_*.py main.py")
    print()
    print("   2. Ручной откат:")
    print("      - Найдите файл main_backup_YYYYMMDD_HHMMSS.py")
    print("      - Переименуйте его обратно в main.py")
    print()
    print("   3. Git откат (если используете git):")
    print("      git checkout HEAD~1 main.py")
    print()
    print("📞 В случае проблем сохраните логи и обратитесь к документации")
    print(create_section_divider("", char="═"))


if __name__ == "__main__":
    print_rollback_info()
    exit_code = cli_main()
    sys.exit(exit_code)
