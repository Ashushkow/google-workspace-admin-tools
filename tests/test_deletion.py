#!/usr/bin/env python3
"""
Тест удаления пользователя из календаря SPUTNIK
"""

import sys
import os

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.sputnik_calendar import SputnikCalendarManager
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_delete_user():
    """Тест удаления пользователя"""
    
    # Инициализация
    calendar_manager = SputnikCalendarManager()
    
    # Инициализация API
    if not calendar_manager.calendar_api.authenticate():
        logger.error("❌ Не удалось инициализировать Google Calendar API")
        return False
    
    # Получаем список участников для проверки наличия пользователя
    logger.info("📋 Получение списка участников...")
    members = calendar_manager.get_members()
    
    if not members:
        logger.error("❌ Не удалось получить список участников")
        return False
    
    logger.info(f"📊 Найдено {len(members)} участников")
    
    # Ищем test.0307@sputnik8.com
    test_email = "test.0307@sputnik8.com"
    test_user = None
    
    for member in members:
        if member.email.lower() == test_email.lower():
            test_user = member
            break
    
    if not test_user:
        logger.warning(f"⚠️  Пользователь {test_email} не найден в списке участников")
        # Показываем первых 5 пользователей для справки
        logger.info("📝 Первые участники:")
        for i, member in enumerate(members[:5]):
            logger.info(f"  {i+1}. {member.email} - {member.role}")
        return False
    
    logger.info(f"👤 Найден пользователь: {test_user.email} ({test_user.role})")
    
    # Попытка удаления
    logger.info(f"🗑️  Попытка удаления пользователя {test_email}...")
    success = calendar_manager.remove_member(test_email)
    
    if success:
        logger.info(f"✅ Пользователь {test_email} успешно удален")
        
        # Проверяем, что пользователь действительно удален
        logger.info("🔍 Проверка удаления...")
        updated_members = calendar_manager.get_members()
        
        still_exists = any(m.email.lower() == test_email.lower() for m in updated_members)
        
        if not still_exists:
            logger.info(f"✅ Подтверждено: пользователь {test_email} больше не в календаре")
            logger.info(f"📊 Участников сейчас: {len(updated_members)}")
        else:
            logger.error(f"❌ Ошибка: пользователь {test_email} все еще в календаре")
            return False
    else:
        logger.error(f"❌ Не удалось удалить пользователя {test_email}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Тест удаления пользователя из календаря SPUTNIK")
    print("=" * 60)
    
    try:
        success = test_delete_user()
        if success:
            print("\n✅ Тест пройден успешно!")
        else:
            print("\n❌ Тест не пройден")
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте: {e}")
        print(f"\n❌ Ошибка: {e}")
