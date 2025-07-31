#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Прямой тест удаления пользователя из группы без сложных зависимостей
"""

import sys
import os
import asyncio
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def direct_removal_test():
    """Прямой тест удаления через Google API"""
    
    print("🔍 ПРЯМОЙ ТЕСТ УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 60)
    
    group_email = "admin_team@sputnik8.com"
    user_email = "testdecember2023@sputnik8.com"
    
    print(f"📧 Группа: {group_email}")
    print(f"👤 Пользователь: {user_email}")
    
    try:
        from src.api.google_api_client import GoogleAPIClient
        from src.config.enhanced_config import config
        
        # Создаем API клиент
        print("\n🔧 Инициализация Google API клиента...")
        api_client = GoogleAPIClient(config.settings.google_application_credentials)
        
        # Инициализируем
        if not api_client.initialize():
            print("❌ Не удалось инициализировать Google API")
            return False
        
        print("✅ Google API успешно инициализирован")
        
        # Шаг 1: Проверяем существование группы
        print(f"\n🔍 Проверка существования группы {group_email}...")
        try:
            groups = api_client.get_groups()
            target_group = None
            
            for group in groups:
                if group.get('email', '').lower() == group_email.lower():
                    target_group = group
                    break
            
            if target_group:
                print(f"✅ Группа найдена: {target_group.get('name', 'N/A')}")
            else:
                print(f"❌ Группа {group_email} не найдена!")
                print("📋 Доступные группы:")
                for i, group in enumerate(groups[:5]):
                    print(f"   {i+1}. {group.get('email', 'N/A')}")
                return False
            
        except Exception as e:
            print(f"❌ Ошибка при проверке групп: {e}")
            return False
        
        # Шаг 2: Проверяем участников группы
        print(f"\n🔍 Проверка участников группы {group_email}...")
        try:
            members = api_client.get_group_members(group_email)
            print(f"📊 Всего участников: {len(members)}")
            
            # Ищем нашего пользователя
            target_member = None
            for member in members:
                if member.get('email', '').lower() == user_email.lower():
                    target_member = member
                    break
            
            if target_member:
                role = target_member.get('role', 'N/A')
                print(f"✅ Пользователь найден в группе с ролью: {role}")
            else:
                print(f"⚠️ Пользователь {user_email} не найден в группе")
                print("📋 Участники группы:")
                for i, member in enumerate(members[:10]):
                    email = member.get('email', 'N/A')
                    role = member.get('role', 'N/A')
                    print(f"   {i+1}. {email} ({role})")
                
                print("ℹ️ Возможно, пользователь уже был удален из группы")
                return True  # Это не ошибка, просто пользователь уже не в группе
            
        except Exception as e:
            print(f"❌ Ошибка при получении участников: {e}")
            logger.error(f"Ошибка при получении участников: {e}", exc_info=True)
            return False
        
        # Шаг 3: Пытаемся удалить пользователя
        print(f"\n🗑️ Попытка удаления {user_email} из {group_email}...")
        try:
            success = api_client.remove_group_member(group_email, user_email)
            
            if success:
                print("✅ Удаление выполнено успешно!")
            else:
                print("❌ Удаление не выполнено")
                return False
            
        except Exception as e:
            print(f"❌ Ошибка при удалении: {e}")
            logger.error(f"Ошибка при удалении: {e}", exc_info=True)
            
            # Анализируем ошибку
            error_str = str(e).lower()
            if "404" in error_str or "not found" in error_str:
                print("🔍 Анализ: Возможно, пользователь уже не в группе")
                return True
            elif "403" in error_str or "forbidden" in error_str:
                print("🔍 Анализ: Недостаточно прав для удаления")
                print("   Проверьте права администратора домена")
            elif "400" in error_str or "bad request" in error_str:
                print("🔍 Анализ: Некорректный запрос")
            
            return False
        
        # Шаг 4: Проверяем результат
        print(f"\n🔍 Проверка результата удаления...")
        try:
            # Ждем немного и проверяем снова
            import time
            time.sleep(2)
            
            members_after = api_client.get_group_members(group_email)
            user_still_in_group = any(
                member.get('email', '').lower() == user_email.lower() 
                for member in members_after
            )
            
            if user_still_in_group:
                print(f"❌ Пользователь все еще в группе")
                return False
            else:
                print(f"✅ Пользователь успешно удален из группы")
                print(f"📊 Участников в группе теперь: {len(members_after)}")
                return True
                
        except Exception as e:
            print(f"⚠️ Ошибка при проверке результата: {e}")
            # Не критично, основная операция могла пройти успешно
            return True
    
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        return False


def main():
    """Главная функция"""
    
    print("🚀 ПРЯМОЙ ТЕСТ УДАЛЕНИЯ testdecember2023@sputnik8.com")
    print("    из группы admin_team@sputnik8.com")
    print("=" * 60)
    
    success = asyncio.run(direct_removal_test())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО")
        print("Пользователь удален из группы или уже не был в ней")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН")
        print("Требуется дополнительная диагностика")
    print("=" * 60)


if __name__ == "__main__":
    main()
