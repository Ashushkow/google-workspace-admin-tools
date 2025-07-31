#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для проверки функциональности удаления участников из групп Google Workspace
"""

import sys
import os
import asyncio
import tracemalloc
from pathlib import Path

# Включаем tracemalloc для отладки
tracemalloc.start()

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.repositories.google_api_repository import GoogleGroupRepository
from src.api.google_api_client import GoogleAPIClient
from src.config.enhanced_config import config
import logging

logger = logging.getLogger(__name__)


async def test_group_member_removal():
    """Тестирует удаление участников из групп"""
    
    print("🔍 Тестирование функциональности удаления участников из групп Google Workspace")
    print("=" * 80)
    
    # Инициализация сервисов
    try:
        # Создаем репозитории
        group_repo = GoogleGroupRepository()
        
        print("✅ Репозиторий инициализирован успешно")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации репозитория: {e}")
        return False
    
    # Тестовые данные
    test_group_email = "test-group@example.com"
    test_member_email = "test-member@example.com"
    
    print(f"\n📧 Тестовая группа: {test_group_email}")
    print(f"👤 Тестовый участник: {test_member_email}")
    
    # Тест 1: Проверка текущей реализации удаления
    print("\n🧪 Тест 1: Проверка текущей реализации удаления участника")
    try:
        result = await group_repo.remove_member(test_group_email, test_member_email)
        print(f"📊 Результат удаления: {'✅ Успешно' if result else '❌ Неудачно'}")
        
        if result:
            print("⚠️  ВНИМАНИЕ: Метод возвращает True, но это может быть заглушка!")
    
    except Exception as e:
        print(f"❌ Ошибка при удалении участника: {e}")
        logger.error(f"Ошибка удаления участника: {e}", exc_info=True)
    
    # Тест 2: Проверка базового репозитория
    print("\n🧪 Тест 2: Проверка метода репозитория напрямую")
    try:
        result = await group_repo.remove_member(test_group_email, test_member_email)
        print(f"📊 Результат репозитория: {'✅ Успешно' if result else '❌ Неудачно'}")
        
        if result:
            print("⚠️  ВНИМАНИЕ: Репозиторий возвращает True - это определенно заглушка!")
            
    except Exception as e:
        print(f"❌ Ошибка в репозитории: {e}")
        logger.error(f"Ошибка репозитория: {e}", exc_info=True)
    
    # Тест 3: Проверка Google API клиента
    print("\n🧪 Тест 3: Проверка Google API клиента")
    try:
        api_client = GoogleAPIClient(config.settings.google_application_credentials)
        is_initialized = api_client.initialize()
        
        print(f"📊 API клиент инициализирован: {'✅ Да' if is_initialized else '❌ Нет'}")
        print(f"📊 API доступен: {'✅ Да' if api_client.is_available() else '❌ Нет'}")
        
        # Проверяем наличие методов для работы с участниками групп
        has_remove_method = hasattr(api_client, 'remove_group_member')
        has_add_method = hasattr(api_client, 'add_group_member')
        
        print(f"📊 Метод remove_group_member: {'✅ Есть' if has_remove_method else '❌ Отсутствует'}")
        print(f"📊 Метод add_group_member: {'✅ Есть' if has_add_method else '❌ Отсутствует'}")
        
        if not has_remove_method:
            print("🚨 ПРОБЛЕМА НАЙДЕНА: В Google API клиенте отсутствуют методы для управления участниками групп!")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования API клиента: {e}")
        logger.error(f"Ошибка API клиента: {e}", exc_info=True)
    
    # Анализ кода
    print("\n🔍 Анализ исходного кода:")
    
    # Проверяем исходный код метода remove_member в репозитории
    repo_file = Path(__file__).parent / 'src' / 'repositories' / 'google_api_repository.py'
    if repo_file.exists():
        with open(repo_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'TODO: Реализовать через Google API' in content:
            print("🚨 НАЙДЕНА ПРОБЛЕМА: В коде найдены TODO комментарии - методы не реализованы!")
            
        if content.count('async def remove_member') > 1:
            print("🚨 НАЙДЕНА ПРОБЛЕМА: Дублирование методов remove_member в репозитории!")
            
        if '(заглушка)' in content:
            print("🚨 НАЙДЕНА ПРОБЛЕМА: В коде найдены заглушки!")
    
    print("\n" + "=" * 80)
    return True


async def generate_fix_recommendations():
    """Генерирует рекомендации по исправлению"""
    
    print("💡 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:")
    print("=" * 80)
    
    print("1. 🔧 Исправить дублирование методов в GoogleGroupRepository")
    print("   - Удалить дублированный метод remove_member")
    print("   - Оставить только один корректный метод")
    
    print("\n2. 🔧 Реализовать методы управления участниками в GoogleAPIClient:")
    print("   - add_group_member(group_email, member_email)")
    print("   - remove_group_member(group_email, member_email)")
    print("   - get_group_members(group_email)")
    
    print("\n3. 🔧 Обновить GoogleGroupRepository:")
    print("   - Заменить заглушки на реальные вызовы Google API")
    print("   - Добавить корректную обработку ошибок")
    
    print("\n4. 🔧 Добавить логирование и аудит:")
    print("   - Логировать успешные операции")
    print("   - Логировать ошибки с деталями")
    print("   - Сохранять аудит изменений")
    
    print("\n5. 🔧 Добавить валидацию:")
    print("   - Проверка существования группы")
    print("   - Проверка существования пользователя")
    print("   - Проверка прав доступа")
    
    print("\n" + "=" * 80)


async def main():
    """Главная функция теста"""
    
    print("🚀 ДИАГНОСТИКА ПРОБЛЕМЫ УДАЛЕНИЯ УЧАСТНИКОВ ИЗ ГРУПП")
    print("=" * 80)
    
    success = await test_group_member_removal()
    
    if success:
        await generate_fix_recommendations()
    
    print("\n✅ Диагностика завершена")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
