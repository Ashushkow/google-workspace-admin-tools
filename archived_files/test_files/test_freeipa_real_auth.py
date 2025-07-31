#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест реального подключения к FreeIPA с учетными данными
"""

import sys
import asyncio
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.services.freeipa_safe_import import create_freeipa_client, get_freeipa_status
from src.services.freeipa_client import FreeIPAConfig, FreeIPAService

def test_stub_directly():
    """Прямой тест FreeIPA stub с реальными данными"""
    print("🧪 Прямой тест FreeIPA stub...")
    
    try:
        # Создаем клиент напрямую
        client = create_freeipa_client(
            server="ipa001.infra.int.sputnik8.com",  # Без схемы - проверим исправление
            verify_ssl=False,
            timeout=30
        )
        
        print(f"✅ Клиент создан: {type(client).__name__}")
        print(f"🌐 Host: {client.host}")
        
        # Тест простого ping
        try:
            ping_result = client.ping()
            print(f"✅ Ping успешен: {ping_result}")
        except Exception as e:
            print(f"⚠️ Ping не удался: {e}")
        
        # Тест логина
        print("\n🔐 Тестирование логина...")
        login_success = client.login("Ashushkow", "Kudrovo95!")
        
        if login_success:
            print("✅ Логин успешен!")
            
            # Тест API вызовов
            try:
                print("\n📁 Тестирование получения групп...")
                groups_result = client.group_find()
                print(f"✅ Группы получены: {groups_result}")
            except Exception as e:
                print(f"⚠️ Ошибка получения групп: {e}")
            
            # Логаут
            client.logout()
            print("✅ Логаут выполнен")
            
        else:
            print("❌ Логин не удался")
            
        return login_success
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

def test_freeipa_service():
    """Тест через FreeIPAService"""
    print("\n🧪 Тест через FreeIPAService...")
    
    try:
        # Загружаем конфигурацию
        config = FreeIPAConfig.from_file("config/freeipa_config.json")
        print(f"✅ Конфигурация загружена: {config.server_url}")
        
        # Создаем сервис
        service = FreeIPAService(config)
        
        # Тестируем подключение
        print("\n🔌 Тестирование подключения...")
        connect_result = service.connect()
        
        if connect_result:
            print("✅ Подключение через сервис успешно!")
            
            # Тест получения групп
            try:
                print("\n📁 Получение групп через сервис...")
                groups = service.get_groups()
                print(f"✅ Получено групп: {len(groups) if groups else 0}")
                
                if groups:
                    for i, group in enumerate(groups[:3]):
                        print(f"  📁 {group}")
                    if len(groups) > 3:
                        print(f"  ... и еще {len(groups) - 3}")
                        
            except Exception as e:
                print(f"⚠️ Ошибка получения групп: {e}")
            
            # Отключение
            service.disconnect()
            print("✅ Отключение выполнено")
            
        else:
            print("❌ Подключение через сервис не удалось")
            
        return connect_result
        
    except Exception as e:
        print(f"❌ Ошибка сервиса: {e}")
        return False

async def test_async_operations():
    """Тест асинхронных операций"""
    print("\n🧪 Тест асинхронных операций...")
    
    try:
        config = FreeIPAConfig.from_file("config/freeipa_config.json")
        service = FreeIPAService(config)
        
        # Эмулируем async операцию как в GUI
        async def async_connect():
            print("🔄 Асинхронное подключение...")
            result = service.connect()
            if result:
                print("✅ Async подключение успешно")
                groups = service.get_groups()
                print(f"✅ Async получение групп: {len(groups) if groups else 0}")
                service.disconnect()
            return result
        
        result = await async_connect()
        return result
        
    except Exception as e:
        print(f"❌ Ошибка async операций: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("=" * 70)
    print("🧪 ТЕСТ РЕАЛЬНОГО ПОДКЛЮЧЕНИЯ К FREEIPA")
    print("🌐 Сервер: https://ipa001.infra.int.sputnik8.com/")
    print("👤 Пользователь: Ashushkow")
    print("=" * 70)
    
    # Проверим статус FreeIPA
    status = get_freeipa_status()
    print(f"📊 FreeIPA статус:")
    print(f"  Доступен: {status['freeipa_available']}")
    print(f"  Клиент: {status['client_class']}")
    if status['import_error']:
        print(f"  Примечание: {status['import_error']}")
    
    tests = [
        ("Прямой тест stub", test_stub_directly),
        ("Тест FreeIPAService", test_freeipa_service),
        ("Тест async операций", lambda: asyncio.run(test_async_operations())),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            results[test_name] = False
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 70)
    
    for test_name, success in results.items():
        status = "✅ ПРОЙДЕН" if success else "❌ НЕ ПРОЙДЕН"
        print(f"{status:<15} {test_name}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\nРезультат: {passed_tests}/{total_tests} тестов пройдено")
    
    if passed_tests == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("✅ Подключение к FreeIPA работает с реальными учетными данными")
        print("✅ Можно начинать работу с группами")
        print("\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
        print("   1. Запустите приложение: python main.py")
        print("   2. Откройте: Интеграции → FreeIPA Интеграция")
        print("   3. Нажмите: Тестировать подключение")
        print("   4. Начните работу с группами!")
        
    elif passed_tests >= total_tests * 0.66:
        print("\n⚠️ БОЛЬШИНСТВО ТЕСТОВ ПРОЙДЕНО")
        print("✅ Основное подключение работает")
        print("⚠️ Некоторые операции могут требовать доработки")
        
    else:
        print("\n❌ ПРОБЛЕМЫ С ПОДКЛЮЧЕНИЕМ")
        print("❌ Проверьте учетные данные и сетевое подключение")
        print("💡 Убедитесь, что пользователь имеет права в FreeIPA")
    
    return 0 if passed_tests >= total_tests * 0.66 else 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Тестирование завершено с кодом выхода: {exit_code}")
    sys.exit(exit_code)
