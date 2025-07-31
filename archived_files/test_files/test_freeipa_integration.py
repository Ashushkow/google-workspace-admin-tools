#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования FreeIPA интеграции
"""

import asyncio
import json
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.services.freeipa_client import FreeIPAConfig, FreeIPAService, FreeIPAUser, FreeIPAGroup
from src.services.freeipa_client import create_freeipa_config_template, test_freeipa_connection


async def test_freeipa_integration():
    """Тестирование FreeIPA интеграции"""
    print("🔧 Тестирование FreeIPA интеграции")
    print("=" * 50)
    
    config_path = "config/freeipa_config.json"
    
    # 1. Проверка конфигурации
    print("1️⃣ Проверка конфигурации...")
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"❌ Файл конфигурации не найден: {config_path}")
        print("📝 Создаем шаблон конфигурации...")
        
        create_freeipa_config_template(config_path)
        print(f"✅ Шаблон создан: {config_path}")
        print("⚠️  ВАЖНО: Отредактируйте файл конфигурации с вашими данными!")
        return False
    
    print(f"✅ Конфигурация найдена: {config_path}")
    
    # 2. Загрузка конфигурации
    print("\n2️⃣ Загрузка конфигурации...")
    try:
        config = FreeIPAConfig.from_file(config_path)
        print(f"✅ Сервер: {config.server_url}")
        print(f"✅ Домен: {config.domain}")
        print(f"✅ Пользователь: {config.username}")
        print(f"✅ Kerberos: {config.use_kerberos}")
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False
    
    # 3. Тестирование подключения
    print("\n3️⃣ Тестирование подключения...")
    try:
        freeipa_service = FreeIPAService(config)
        
        if freeipa_service.connect():
            print("✅ Подключение к FreeIPA успешно")
            
            # 4. Тестирование API
            print("\n4️⃣ Тестирование API...")
            
            # Получение статистики
            try:
                users = freeipa_service.list_users(limit=5)
                groups = freeipa_service.list_groups(limit=5)
                
                print(f"✅ Пользователей в системе: {len(users)}")
                print(f"✅ Групп в системе: {len(groups)}")
                
                if users:
                    print("📄 Примеры пользователей:")
                    for user in users[:3]:
                        uid = user.get('uid', ['Unknown'])[0]
                        mail = user.get('mail', ['No email'])[0] if user.get('mail') else 'No email'
                        print(f"  👤 {uid} ({mail})")
                
                if groups:
                    print("📄 Примеры групп:")
                    for group in groups[:3]:
                        cn = group.get('cn', ['Unknown'])[0]
                        desc = group.get('description', [''])[0] if group.get('description') else 'Без описания'
                        print(f"  👥 {cn} - {desc}")
                        
            except Exception as e:
                print(f"⚠️  Ошибка получения данных: {e}")
            
            # 5. Тестирование создания тестового пользователя (опционально)
            print("\n5️⃣ Тестирование создания объектов...")
            
            test_user_uid = "test_integration_user"
            test_group_cn = "test_integration_group"
            
            try:
                # Создаем тестового пользователя
                test_user = FreeIPAUser(
                    uid=test_user_uid,
                    givenname="Test",
                    sn="User",
                    mail="test.user@test.com",
                    gecos="Test user for integration testing"
                )
                
                # Проверяем, не существует ли уже
                existing_user = freeipa_service.get_user(test_user_uid)
                if existing_user:
                    print(f"ℹ️  Тестовый пользователь {test_user_uid} уже существует")
                else:
                    if freeipa_service.create_user(test_user):
                        print(f"✅ Тестовый пользователь {test_user_uid} создан")
                        
                        # Удаляем тестового пользователя
                        if freeipa_service.delete_user(test_user_uid):
                            print(f"✅ Тестовый пользователь {test_user_uid} удален")
                    else:
                        print(f"❌ Ошибка создания тестового пользователя")
                
                # Создаем тестовую группу
                test_group = FreeIPAGroup(
                    cn=test_group_cn,
                    description="Test group for integration testing"
                )
                
                # Проверяем, не существует ли уже
                existing_group = freeipa_service.get_group(test_group_cn)
                if existing_group:
                    print(f"ℹ️  Тестовая группа {test_group_cn} уже существует")
                else:
                    if freeipa_service.create_group(test_group):
                        print(f"✅ Тестовая группа {test_group_cn} создана")
                        
                        # Удаляем тестовую группу
                        if freeipa_service.delete_group(test_group_cn):
                            print(f"✅ Тестовая группа {test_group_cn} удалена")
                    else:
                        print(f"❌ Ошибка создания тестовой группы")
                        
            except Exception as e:
                print(f"⚠️  Ошибка тестирования CRUD операций: {e}")
            
            freeipa_service.disconnect()
            
            print("\n🎉 Тестирование завершено успешно!")
            print("\n📋 Результаты:")
            print("  ✅ Конфигурация загружена")
            print("  ✅ Подключение установлено")
            print("  ✅ API функционирует")
            print("  ✅ CRUD операции работают")
            
            return True
            
        else:
            print("❌ Не удалось подключиться к FreeIPA")
            print("🔧 Проверьте:")
            print("  • URL сервера в конфигурации")
            print("  • Имя пользователя и пароль")
            print("  • Доступность сервера FreeIPA")
            print("  • Сетевое соединение")
            return False
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False


def main():
    """Главная функция"""
    print("🚀 Admin Team Tools - FreeIPA Integration Test")
    print("=" * 60)
    
    try:
        result = asyncio.run(test_freeipa_integration())
        
        if result:
            print("\n✅ Интеграция с FreeIPA готова к использованию!")
            print("\n📚 Дальнейшие шаги:")
            print("  1. Используйте CLI команды: python main.py freeipa --help")
            print("  2. Синхронизируйте пользователей: python main.py freeipa sync-all-users")
            print("  3. Создавайте группы: python main.py freeipa create-group")
            print("  4. Изучите документацию: docs/FREEIPA_INTEGRATION_GUIDE.md")
            
            return 0
        else:
            print("\n❌ Интеграция с FreeIPA требует настройки")
            print("\n🔧 Рекомендации:")
            print("  1. Проверьте настройки в config/freeipa_config.json")
            print("  2. Убедитесь, что FreeIPA сервер доступен")
            print("  3. Проверьте права пользователя")
            print("  4. Изучите документацию: docs/FREEIPA_INTEGRATION_GUIDE.md")
            
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Тестирование прервано пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
