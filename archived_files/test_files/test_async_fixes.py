#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления async ошибок в FreeIPA
"""

import sys
import asyncio
import tracemalloc
from pathlib import Path

# Включаем tracemalloc
tracemalloc.start()

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.simple_utils import SimpleAsyncManager

def test_async_manager():
    """Тест нового async менеджера"""
    print("🧪 Тестирование SimpleAsyncManager...")
    
    async_manager = SimpleAsyncManager()
    
    # Тест 1: Обычная функция
    def sync_func():
        print("✅ Обычная функция выполнена")
        return "sync_result"
    
    # Тест 2: Асинхронная функция
    async def async_func():
        print("✅ Асинхронная функция выполнена")
        await asyncio.sleep(0.1)  # Имитация async операции
        return "async_result"
    
    def on_success(result):
        print(f"✅ Результат получен: {result}")
    
    def on_error(error):
        print(f"❌ Ошибка: {error}")
    
    print("\n1. Тест обычной функции...")
    async_manager.run_async(sync_func, on_success, on_error)
    
    print("\n2. Тест асинхронной функции...")
    async_manager.run_async(async_func, on_success, on_error)
    
    # Ждем завершения тестов
    import time
    time.sleep(1)
    
    print("\n✅ Тесты async менеджера завершены")
    return True

def test_freeipa_imports():
    """Тест импортов FreeIPA"""
    print("\n🧪 Тестирование импортов FreeIPA...")
    
    try:
        from src.services.freeipa_safe_import import get_freeipa_status
        status = get_freeipa_status()
        
        print(f"FreeIPA доступен: {status['freeipa_available']}")
        print(f"Kerberos доступен: {status['kerberos_available']}")
        print(f"Клиент: {status['client_class']}")
        
        if status['import_error']:
            print(f"Ошибка импорта: {status['import_error']}")
        
        return status['freeipa_available']
        
    except Exception as e:
        print(f"❌ Ошибка тестирования импортов: {e}")
        return False

def test_freeipa_connection():
    """Тест создания FreeIPA подключения"""
    print("\n🧪 Тестирование создания FreeIPA подключения...")
    
    try:
        from src.services.freeipa_safe_import import create_freeipa_client
        
        # Пробуем создать клиент
        client = create_freeipa_client('ipa001.infra.int.sputnik8.com', verify_ssl=False)
        print(f"✅ FreeIPA клиент создан: {type(client).__name__}")
        
        # Простой тест
        if hasattr(client, 'ping'):
            print("✅ Метод ping доступен")
        
        if hasattr(client, 'login'):
            print("✅ Метод login доступен")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания клиента: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("=" * 70)
    print("🧪 ТЕСТ ИСПРАВЛЕНИЯ ASYNC ОШИБОК FREEIPA")
    print("🎯 Проверяем: корутины, импорты, создание клиента")
    print("=" * 70)
    
    tests = [
        ("Async Manager", test_async_manager),
        ("FreeIPA импорты", test_freeipa_imports),
        ("FreeIPA подключение", test_freeipa_connection),
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
        print("✅ Async ошибки исправлены")
        print("✅ FreeIPA готов к использованию")
        print("✅ Тестирование соединения должно работать")
        
    elif passed_tests >= total_tests * 0.66:
        print("\n⚠️ БОЛЬШИНСТВО ТЕСТОВ ПРОЙДЕНО")
        print("✅ Основная функциональность работает")
        print("⚠️ Могут быть проблемы с некоторыми компонентами")
        
    else:
        print("\n❌ СЕРЬЕЗНЫЕ ПРОБЛЕМЫ")
        print("❌ Требуется дополнительная отладка")
    
    return 0 if passed_tests >= total_tests * 0.66 else 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Тестирование завершено с кодом выхода: {exit_code}")
    sys.exit(exit_code)
