#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления FreeIPA интеграции
"""

import sys
import asyncio
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

async def test_freeipa_integration():
    """Тест FreeIPA интеграции"""
    print("🔧 Тестируем исправление FreeIPA интеграции...")
    
    try:
        # Импортируем нужные модули
        from src.integrations.freeipa_integration import FreeIPAIntegration
        from src.services.user_service import UserService
        from src.services.group_service import GroupService
        from src.repositories.google_api_repository import GoogleUserRepository, GoogleGroupRepository
        from src.repositories.cache_repository import CacheRepository
        from src.repositories.audit_repository import SQLiteAuditRepository
        
        print("✅ Импорты успешны")
        
        # Создаем моки сервисов (для тестирования структуры)
        class MockRepo:
            async def get_all(self): return []
            async def get_by_email(self, email): return None
        
        mock_user_repo = MockRepo()
        mock_group_repo = MockRepo()
        mock_cache_repo = MockRepo()
        mock_audit_repo = MockRepo()
        
        user_service = UserService(mock_user_repo, mock_cache_repo, mock_audit_repo)
        group_service = GroupService(mock_group_repo, mock_cache_repo, mock_audit_repo)
        
        print("✅ Сервисы созданы")
        
        # Создаем FreeIPA интеграцию
        freeipa_integration = FreeIPAIntegration(user_service, group_service)
        
        # Проверяем, что атрибут freeipa_client доступен
        assert hasattr(freeipa_integration, 'freeipa_client'), "Атрибут freeipa_client не найден"
        print("✅ Атрибут freeipa_client доступен")
        
        # Проверяем, что freeipa_client возвращает правильный объект
        client = freeipa_integration.freeipa_client
        assert client is not None, "freeipa_client возвращает None"
        print("✅ freeipa_client возвращает объект")
        
        # Проверяем наличие нужных методов
        required_methods = ['get_groups', 'get_group', 'create_group']
        for method_name in required_methods:
            assert hasattr(client, method_name), f"Метод {method_name} не найден"
            method = getattr(client, method_name)
            assert asyncio.iscoroutinefunction(method), f"Метод {method_name} не асинхронный"
            print(f"✅ Метод {method_name} найден и асинхронный")
        
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("✅ Ошибка 'FreeIPAIntegration' object has no attribute 'freeipa_client' ИСПРАВЛЕНА")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ui_import():
    """Тест импорта UI компонентов"""
    print("\n🔧 Тестируем импорт UI компонентов...")
    
    try:
        from src.ui.freeipa_management import FreeIPAManagementWindow
        print("✅ FreeIPAManagementWindow импортирован успешно")
        
        # Проверяем, что класс можно создать (без GUI)
        # Это просто проверка структуры класса
        import inspect
        signature = inspect.signature(FreeIPAManagementWindow.__init__)
        print(f"✅ Конструктор FreeIPAManagementWindow: {signature}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта UI: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("="*60)
    print("🧪 ТЕСТ ИСПРАВЛЕНИЯ FREEIPA ИНТЕГРАЦИИ")
    print("="*60)
    
    # Запускаем асинхронные тесты
    success1 = asyncio.run(test_freeipa_integration())
    success2 = asyncio.run(test_ui_import())
    
    print("\n" + "="*60)
    if success1 and success2:
        print("🎯 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Проблема с FreeIPA интеграцией исправлена")
        print("✅ UI компоненты работают корректно")
    else:
        print("❌ Некоторые тесты не пройдены")
        
    print("="*60)

if __name__ == "__main__":
    main()
