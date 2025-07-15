#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест системы обработки ошибок Admin Team Tools
"""

import sys
from pathlib import Path

# Добавляем src в path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_error_handling():
    """Тест системы обработки ошибок"""
    print("🧪 Тестирование системы обработки ошибок...")
    
    try:
        # Тест логирования
        from utils.enhanced_logger import setup_logging
        logger = setup_logging('INFO', 'test_logs')
        logger.info("✅ Система логирования работает!")
        
        # Тест валидации окружения
        from utils.environment_validator import EnvironmentValidator
        validator = EnvironmentValidator(logger)
        success, errors, warnings = validator.validate_all()
        
        print(f"\n📋 Результат валидации:")
        print(f"   Успех: {'✅' if success else '❌'}")
        print(f"   Ошибок: {len(errors)}")
        print(f"   Предупреждений: {len(warnings)}")
        
        if errors:
            print("\n❌ Критические ошибки:")
            for i, error in enumerate(errors[:3], 1):
                print(f"   {i}. {error}")
        
        if warnings:
            print("\n⚠️ Предупреждения:")
            for i, warning in enumerate(warnings[:3], 1):
                print(f"   {i}. {warning}")
        
        # Тест обработчика ошибок
        from utils.error_handler import ErrorHandler
        from utils.exceptions import GoogleAPIError
        
        error_handler = ErrorHandler(logger)
        
        # Тестируем обработку ошибки
        test_error = GoogleAPIError(
            "Тестовая ошибка Google API",
            error_code="API_TEST_001"
        )
        
        print(f"\n🔧 Тестирование обработчика ошибок...")
        result = error_handler.handle_exception(
            test_error, 
            "тестирование системы", 
            show_dialog=False
        )
        print(f"   Результат обработки: {'✅' if result else '❌'}")
        
        print(f"\n🎉 Тестирование завершено!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_error_handling()
    sys.exit(0 if success else 1)
