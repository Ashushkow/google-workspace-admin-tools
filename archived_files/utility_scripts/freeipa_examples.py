#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Примеры использования FreeIPA интеграции
"""

import asyncio
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / 'src'))


async def example_freeipa_usage():
    """Пример использования FreeIPA интеграции"""
    
    print("🔗 Примеры использования FreeIPA интеграции")
    print("=" * 60)
    
    # Пример 1: Проверка зависимостей
    print("\n1️⃣ Проверка зависимостей:")
    print("   python test_cli.py check-dependencies")
    
    # Пример 2: Создание конфигурации
    print("\n2️⃣ Создание конфигурации:")
    print("   python test_cli.py create-config")
    print("   # Отредактируйте config/freeipa_config.json")
    
    # Пример 3: Тестирование подключения
    print("\n3️⃣ Тестирование подключения:")
    print("   python test_cli.py test-connection")
    
    # Пример 4: Программное использование (после установки зависимостей)
    print("\n4️⃣ Программное использование:")
    print("""
# Простое подключение
from src.services.freeipa_client import FreeIPAConfig, FreeIPAService

config = FreeIPAConfig.from_file('config/freeipa_config.json')
service = FreeIPAService(config)

if service.connect():
    users = service.list_users(limit=10)
    print(f"Найдено пользователей: {len(users)}")
    service.disconnect()
""")
    
    # Пример 5: Интеграция с Google Workspace
    print("\n5️⃣ Интеграция с Google Workspace:")
    print("""
# Синхронизация пользователя
from src.integrations.freeipa_integration import setup_freeipa_integration

integration = await setup_freeipa_integration(user_service, group_service)
if integration:
    await integration.sync_user_to_freeipa('user@example.com', ['employees'])
    await integration.disconnect()
""")
    
    # Пример 6: CLI команды (после установки)
    print("\n6️⃣ CLI команды (после установки python-freeipa):")
    print("   python main.py freeipa stats")
    print("   python main.py freeipa sync-user user@example.com --groups employees")
    print("   python main.py freeipa sync-all-users --domain example.com")
    print("   python main.py freeipa create-group developers")
    print("   python main.py freeipa compare-users")
    
    # Пример 7: Массовая синхронизация
    print("\n7️⃣ Массовая синхронизация:")
    print("""
# Полная синхронизация организации
1. python main.py freeipa sync-groups --domain example.com
2. python main.py freeipa sync-all-users --domain example.com --groups employees
3. python main.py freeipa compare-users --domain example.com
""")
    
    print("\n📖 Дополнительная информация:")
    print("   docs/FREEIPA_INTEGRATION_GUIDE.md - Полное руководство")
    print("   FREEIPA_QUICKSTART.md - Быстрый старт")
    print("   FREEIPA_IMPLEMENTATION_REPORT.md - Отчет о реализации")


def show_current_status():
    """Показать текущий статус интеграции"""
    
    print("\n📊 Текущий статус FreeIPA интеграции:")
    print("=" * 50)
    
    # Проверка файлов
    files_to_check = [
        "src/services/freeipa_client.py",
        "src/integrations/freeipa_integration.py", 
        "src/cli/freeipa_simple.py",
        "config/freeipa_config.json",
        "docs/FREEIPA_INTEGRATION_GUIDE.md",
        "test_freeipa_integration.py"
    ]
    
    print("\n✅ Реализованные файлы:")
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
    
    # Проверка зависимостей
    print("\n📦 Зависимости:")
    
    try:
        import click
        print("   ✅ click - установлен")
    except ImportError:
        print("   ❌ click - не установлен")
    
    try:
        import requests
        print("   ✅ requests - установлен")
    except ImportError:
        print("   ❌ requests - не установлен")
        
    try:
        import python_freeipa
        print("   ✅ python-freeipa - установлен")
    except ImportError:
        print("   ⚠️  python-freeipa - не установлен (требуется для полной функциональности)")
        
    try:
        import requests_kerberos
        print("   ✅ requests-kerberos - установлен")
    except ImportError:
        print("   ⚠️  requests-kerberos - не установлен (требуется для Kerberos)")
    
    # Проверка конфигурации
    print("\n⚙️ Конфигурация:")
    config_path = Path("config/freeipa_config.json")
    if config_path.exists():
        print("   ✅ Конфигурация создана")
        print("   📝 Отредактируйте config/freeipa_config.json с вашими данными")
    else:
        print("   ❌ Конфигурация не создана")
        print("   📝 Запустите: python test_cli.py create-config")
    
    print("\n🚀 Следующие шаги:")
    if not config_path.exists():
        print("   1. Создайте конфигурацию: python test_cli.py create-config")
        print("   2. Отредактируйте config/freeipa_config.json")
        print("   3. Установите зависимости: pip install python-freeipa requests-kerberos")
        print("   4. Протестируйте: python test_cli.py test-connection")
    else:
        print("   1. Отредактируйте config/freeipa_config.json с реальными данными")
        print("   2. Установите зависимости: pip install python-freeipa requests-kerberos")
        print("   3. Протестируйте: python test_cli.py test-connection")
        print("   4. Используйте: python main.py freeipa --help")


async def main():
    """Главная функция"""
    print("🚀 FreeIPA Integration Examples")
    print("=" * 60)
    
    await example_freeipa_usage()
    show_current_status()
    
    print("\n" + "=" * 60)
    print("✨ FreeIPA интеграция готова к использованию!")


if __name__ == "__main__":
    asyncio.run(main())
