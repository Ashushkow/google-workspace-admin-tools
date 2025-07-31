#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диагностика конкретной проблемы с удалением пользователя из группы
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

import logging

# Настройка детального логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def diagnose_specific_removal():
    """Диагностирует конкретную проблему с удалением"""
    
    print("🔍 ДИАГНОСТИКА УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЯ ИЗ ГРУППЫ")
    print("=" * 80)
    
    # Данные для диагностики
    group_email = "admin_team@sputnik8.com"
    user_email = "testdecember2023@sputnik8.com"
    
    print(f"📧 Группа: {group_email}")
    print(f"👤 Пользователь: {user_email}")
    
    try:
        from src.api.google_api_client import GoogleAPIClient
        from src.repositories.google_api_repository import GoogleGroupRepository
        from src.config.enhanced_config import config
        
        # Шаг 1: Проверка инициализации API
        print("\n🧪 Шаг 1: Проверка Google API клиента")
        api_client = GoogleAPIClient(config.settings.google_application_credentials)
        is_initialized = api_client.initialize()
        
        print(f"📊 API инициализирован: {'✅ Да' if is_initialized else '❌ Нет'}")
        print(f"📊 API доступен: {'✅ Да' if api_client.is_available() else '❌ Нет'}")
        
        if not is_initialized:
            print("❌ ПРОБЛЕМА: Google API не инициализирован!")
            print("🔧 Проверьте:")
            print("   • Наличие файла credentials.json")
            print("   • Правильность конфигурации OAuth 2.0")
            print("   • Настройки скоупов в credentials")
            return False
        
        # Шаг 2: Проверка существования группы
        print(f"\n🧪 Шаг 2: Проверка существования группы {group_email}")
        try:
            groups = api_client.get_groups()
            group_exists = any(group.get('email', '').lower() == group_email.lower() for group in groups)
            
            print(f"📊 Группа существует: {'✅ Да' if group_exists else '❌ Нет'}")
            
            if not group_exists:
                print(f"❌ ПРОБЛЕМА: Группа {group_email} не найдена!")
                print("📋 Доступные группы:")
                for group in groups[:5]:  # Показываем первые 5 групп
                    print(f"   • {group.get('email', 'N/A')}: {group.get('name', 'N/A')}")
                if len(groups) > 5:
                    print(f"   ... и еще {len(groups) - 5} групп")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка получения групп: {e}")
            logger.error(f"Ошибка получения групп: {e}", exc_info=True)
            return False
        
        # Шаг 3: Проверка участников группы
        print(f"\n🧪 Шаг 3: Проверка участников группы {group_email}")
        try:
            members = api_client.get_group_members(group_email)
            user_in_group = any(member.get('email', '').lower() == user_email.lower() for member in members)
            
            print(f"📊 Всего участников в группе: {len(members)}")
            print(f"📊 Пользователь в группе: {'✅ Да' if user_in_group else '❌ Нет'}")
            
            if not user_in_group:
                print(f"⚠️ ВНИМАНИЕ: Пользователь {user_email} не найден в группе!")
                print("📋 Участники группы:")
                for member in members[:10]:  # Показываем первых 10 участников
                    email = member.get('email', 'N/A')
                    role = member.get('role', 'N/A')
                    print(f"   • {email} ({role})")
                if len(members) > 10:
                    print(f"   ... и еще {len(members) - 10} участников")
                
                # Пользователь не в группе, но это не ошибка - возможно уже удален
                print("ℹ️ Это может означать, что пользователь уже был удален из группы")
                return True
            
        except Exception as e:
            print(f"❌ Ошибка получения участников группы: {e}")
            logger.error(f"Ошибка получения участников группы: {e}", exc_info=True)
            
        # Шаг 4: Попытка удаления
        print(f"\n🧪 Шаг 4: Попытка удаления {user_email} из {group_email}")
        try:
            result = api_client.remove_group_member(group_email, user_email)
            print(f"📊 Результат удаления: {'✅ Успешно' if result else '❌ Неудачно'}")
            
            if result:
                print("✅ Удаление выполнено успешно!")
            else:
                print("❌ Удаление не выполнено!")
                
        except Exception as e:
            print(f"❌ Ошибка при удалении: {e}")
            logger.error(f"Ошибка при удалении: {e}", exc_info=True)
            
            # Анализируем тип ошибки
            if "404" in str(e) or "Not Found" in str(e):
                print("🔍 Анализ: Ошибка 404 - пользователь или группа не найдены")
            elif "403" in str(e) or "Forbidden" in str(e):
                print("🔍 Анализ: Ошибка 403 - недостаточно прав доступа")
            elif "400" in str(e) or "Bad Request" in str(e):
                print("🔍 Анализ: Ошибка 400 - некорректный запрос")
            
            return False
        
        # Шаг 5: Верификация удаления
        print(f"\n🧪 Шаг 5: Верификация удаления")
        try:
            from src.utils.group_verification import GroupChangeVerifier
            
            verifier = GroupChangeVerifier(api_client)
            verification_result = verifier.verify_member_removal(
                group_email, user_email,
                max_retries=2, retry_delay=3
            )
            
            print(f"📊 Верификация: {'✅ Подтверждено' if verification_result else '❌ Не подтверждено'}")
            
            return verification_result
            
        except Exception as e:
            print(f"❌ Ошибка верификации: {e}")
            logger.error(f"Ошибка верификации: {e}", exc_info=True)
            return False
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("🔧 Проверьте настройку Python path и наличие модулей")
        return False
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        return False


async def test_repository_method():
    """Тестирует метод репозитория напрямую"""
    
    print("\n🧪 ТЕСТ МЕТОДА РЕПОЗИТОРИЯ")
    print("=" * 50)
    
    group_email = "admin_team@sputnik8.com"
    user_email = "testdecember2023@sputnik8.com"
    
    try:
        from src.repositories.google_api_repository import GoogleGroupRepository
        
        # Создаем репозиторий
        repo = GoogleGroupRepository()
        
        # Тестируем удаление с верификацией
        print(f"🔄 Удаление {user_email} из {group_email} через репозиторий...")
        result = await repo.remove_member(group_email, user_email, verify=True)
        
        print(f"📊 Результат репозитория: {'✅ Успешно' if result else '❌ Неудачно'}")
        
        # Получаем статистику операций
        if hasattr(repo, 'get_operation_statistics'):
            stats = repo.get_operation_statistics()
            print(f"📊 Статистика операций: {stats}")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка тестирования репозитория: {e}")
        logger.error(f"Ошибка тестирования репозитория: {e}", exc_info=True)
        return False


def provide_troubleshooting_steps():
    """Предоставляет шаги по устранению проблем"""
    
    print("\n🔧 РУКОВОДСТВО ПО УСТРАНЕНИЮ ПРОБЛЕМ")
    print("=" * 80)
    
    print("1. 🔐 ПРОВЕРКА АВТОРИЗАЦИИ:")
    print("   • Убедитесь, что credentials.json настроен правильно")
    print("   • Проверьте OAuth 2.0 consent screen")
    print("   • Убедитесь, что у приложения есть скоуп admin.directory.group")
    
    print("\n2. 🏢 ПРОВЕРКА ДОМЕННЫХ ПРАВ:")
    print("   • Убедитесь, что вы администратор домена sputnik8.com")
    print("   • Проверьте права на управление группами")
    print("   • Убедитесь, что группа admin_team@sputnik8.com существует")
    
    print("\n3. 👤 ПРОВЕРКА ПОЛЬЗОВАТЕЛЯ:")
    print("   • Убедитесь, что testdecember2023@sputnik8.com существует")
    print("   • Проверьте, что пользователь действительно в группе")
    print("   • Возможно, пользователь уже был удален")
    
    print("\n4. 🔍 ПРОВЕРКА ЛОГОВ:")
    print("   • Изучите детальные логи в консоли")
    print("   • Обратите внимание на HTTP коды ошибок")
    print("   • Проверьте сообщения об ошибках Google API")
    
    print("\n5. 🚀 АЛЬТЕРНАТИВНЫЕ МЕТОДЫ:")
    print("   • Попробуйте удаление через Google Admin Console")
    print("   • Используйте gam (Google Apps Manager) для проверки")
    print("   • Проверьте через Google Cloud Console")


async def main():
    """Главная функция диагностики"""
    
    print("🚀 ДИАГНОСТИКА ПРОБЛЕМЫ УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЯ")
    print("testdecember2023@sputnik8.com из группы admin_team@sputnik8.com")
    print("=" * 80)
    
    # Запускаем диагностику API
    api_success = await diagnose_specific_removal()
    
    # Тестируем репозиторий
    repo_success = await test_repository_method()
    
    # Предоставляем рекомендации
    provide_troubleshooting_steps()
    
    print("\n" + "=" * 80)
    if api_success or repo_success:
        print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА: Проблема решена или пользователь уже удален")
    else:
        print("❌ ДИАГНОСТИКА ЗАВЕРШЕНА: Требуется дополнительное расследование")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
