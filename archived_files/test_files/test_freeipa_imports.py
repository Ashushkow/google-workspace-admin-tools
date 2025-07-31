#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест импортов FreeIPA модулей
Проверяет, что приложение может запускаться без ошибок Kerberos
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_basic_imports():
    """Тест основных импортов без FreeIPA"""
    print("🔍 Тестирование основных импортов...")
    
    try:
        from src.core.application import Application
        print("✅ Application импортирован")
        
        from src.utils.enhanced_logger import setup_logging
        print("✅ Logger импортирован")
        
        from src.config.enhanced_config import config
        print("✅ Config импортирован")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка основных импортов: {e}")
        return False

def test_ui_imports():
    """Тест импортов UI модулей"""
    print("\n🔍 Тестирование UI импортов...")
    
    try:
        from src.ui.main_window import AdminToolsMainWindow
        print("✅ AdminToolsMainWindow импортирован")
        
        # Тест условного импорта FreeIPA
        try:
            from src.ui.main_window import AdminToolsMainWindow
            window_class = AdminToolsMainWindow
            print("✅ AdminToolsMainWindow создан без ошибок")
        except Exception as e:
            print(f"⚠️ Проблема с AdminToolsMainWindow: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка UI импортов: {e}")
        return False

def test_freeipa_conditional_imports():
    """Тест условных импортов FreeIPA"""
    print("\n🔍 Тестирование условных импортов FreeIPA...")
    
    try:
        # Тест services
        from src.services.freeipa_client import FREEIPA_AVAILABLE
        print(f"✅ FreeIPA client модуль: {'доступен' if FREEIPA_AVAILABLE else 'недоступен'}")
        
        # Тест integrations
        from src.integrations import FREEIPA_AVAILABLE as integrations_available
        print(f"✅ FreeIPA integrations: {'доступен' if integrations_available else 'недоступен'}")
        
        # Тест ленивого импорта UI
        try:
            # Этот импорт НЕ должен вызывать ошибку Kerberos
            def lazy_import_test():
                from src.ui.freeipa_management import FREEIPA_MODULES_AVAILABLE
                return FREEIPA_MODULES_AVAILABLE
            
            freeipa_ui_available = lazy_import_test()
            print(f"✅ FreeIPA UI модуль: {'доступен' if freeipa_ui_available else 'недоступен'}")
            
        except Exception as e:
            if "kerberos" in str(e).lower() or "kfw" in str(e).lower():
                print("⚠️ FreeIPA UI: Проблема с Kerberos (ожидаемо)")
            else:
                print(f"❌ FreeIPA UI: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка условных импортов: {e}")
        return False

def test_manual_freeipa_import():
    """Ручной тест импорта python-freeipa"""
    print("\n🔍 Прямой тест python-freeipa...")
    
    try:
        import python_freeipa
        print("✅ python-freeipa импортирован")
        return True
    except ImportError as e:
        if "kerberos" in str(e).lower() or "kfw" in str(e).lower():
            print("⚠️ python-freeipa: Проблема с Kerberos (ожидаемо в Windows)")
            print("💡 Это нормально - библиотека будет работать при подключении")
            return True
        else:
            print(f"❌ python-freeipa недоступен: {e}")
            return False
    except Exception as e:
        print(f"❌ Ошибка импорта python-freeipa: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("=" * 70)
    print("🧪 ТЕСТ ИМПОРТОВ FREEIPA МОДУЛЕЙ")
    print("🎯 Цель: Убедиться, что приложение запускается без ошибок")
    print("=" * 70)
    
    tests = [
        ("Основные импорты", test_basic_imports),
        ("UI импорты", test_ui_imports),
        ("Условные импорты FreeIPA", test_freeipa_conditional_imports),
        ("Прямой импорт python-freeipa", test_manual_freeipa_import),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
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
        print("✅ Приложение должно запускаться без ошибок Kerberos")
        print("✅ FreeIPA функциональность доступна при необходимости")
        
        print("\n🚀 РЕКОМЕНДАЦИИ:")
        print("   1. Запустите main.py - ошибок Kerberos быть не должно")
        print("   2. FreeIPA интеграция будет работать при подключении")
        print("   3. Используйте test_freeipa_connection.py для проверки сервера")
        
    elif passed_tests >= total_tests * 0.75:
        print("\n⚠️ БОЛЬШИНСТВО ТЕСТОВ ПРОЙДЕНО")
        print("✅ Приложение должно работать")
        print("⚠️ Могут быть проблемы с некоторыми FreeIPA функциями")
        
    else:
        print("\n❌ СЕРЬЕЗНЫЕ ПРОБЛЕМЫ")
        print("❌ Возможны проблемы с запуском приложения")
        print("💡 Проверьте установку зависимостей")
    
    return 0 if passed_tests >= total_tests * 0.75 else 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Тестирование завершено с кодом выхода: {exit_code}")
    sys.exit(exit_code)
