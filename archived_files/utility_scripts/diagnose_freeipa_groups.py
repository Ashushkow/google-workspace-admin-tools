#!/usr/bin/env python3
"""
Диагностический скрипт для анализа групп FreeIPA
Показывает RAW данные, которые возвращает FreeIPA API
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.integrations.freeipa_integration import FreeIPAIntegration
from src.config.enhanced_config import config

async def diagnose_freeipa_groups():
    """Диагностика групп FreeIPA"""
    print("🔍 ДИАГНОСТИКА ГРУПП FREEIPA")
    print("=" * 50)
    
    try:
        # Читаем конфигурацию FreeIPA
        freeipa_config_path = Path("config/freeipa_config.json")
        if not freeipa_config_path.exists():
            print("❌ Файл config/freeipa_config.json не найден")
            return
        
        with open(freeipa_config_path, 'r', encoding='utf-8') as f:
            freeipa_config = json.load(f)
        
        print(f"📡 Подключение к FreeIPA серверу: {freeipa_config.get('server_url', 'N/A')}")
        print(f"👤 Пользователь: {freeipa_config.get('username', 'N/A')}")
        print()
        
        # Создаем прямое подключение к FreeIPA сервису
        from src.services.freeipa_client import FreeIPAService, FreeIPAConfig
        
        # Загружаем конфигурацию FreeIPA
        freeipa_config_obj = FreeIPAConfig(
            server_url=freeipa_config.get('server_url', ''),
            domain=freeipa_config.get('domain', ''),
            username=freeipa_config.get('username', ''),
            password=freeipa_config.get('password', ''),
            use_kerberos=freeipa_config.get('use_kerberos', False),
            verify_ssl=freeipa_config.get('verify_ssl', True),
            timeout=freeipa_config.get('timeout', 30)
        )
        
        # Создаем сервис напрямую
        freeipa_service = FreeIPAService(freeipa_config_obj)
        
        print("🔗 Подключение к FreeIPA...")
        connection_result = freeipa_service.connect()
        if connection_result:
            print("✅ Подключение установлено")
        else:
            print("❌ Не удалось подключиться к FreeIPA")
            return
        print()
        
        print("📋 Получение RAW данных групп...")
        groups = freeipa_service.list_groups()
        
        print(f"📊 Тип возвращаемых данных: {type(groups)}")
        print()
        
        if isinstance(groups, dict):
            print("🔍 АНАЛИЗ СТРУКТУРЫ ОТВЕТА API:")
            print("-" * 50)
            print(f"📋 Ключи ответа: {list(groups.keys())}")
            print()
            
            # Показываем содержимое каждого ключа
            for key, value in groups.items():
                print(f"🔑 {key}:")
                print(f"   🔧 Тип: {type(value)}")
                if isinstance(value, list):
                    print(f"   📊 Количество элементов: {len(value)}")
                    if len(value) > 0:
                        print(f"   🔍 Первый элемент: {type(value[0])} - {value[0] if len(str(value[0])) < 100 else str(value[0])[:100] + '...'}")
                elif isinstance(value, dict):
                    print(f"   📋 Ключи: {list(value.keys())}")
                else:
                    print(f"   📝 Значение: {value}")
                print()
            
            # Ищем реальные группы в ключе 'result'
            if 'result' in groups and isinstance(groups['result'], list):
                actual_groups = groups['result']
                print(f"✅ Найдены реальные группы в ключе 'result': {len(actual_groups)}")
                
                if actual_groups:
                    print("\n🔍 АНАЛИЗ РЕАЛЬНЫХ ГРУПП:")
                    print("-" * 50)
                    
                    for i, group in enumerate(actual_groups, 1):
                        print(f"\n📁 Группа #{i}:")
                        if isinstance(group, dict):
                            print(f"   📋 Ключи: {list(group.keys())}")
                            
                            # Имя группы
                            group_name = group.get('cn', ['Unknown'])[0] if isinstance(group.get('cn'), list) else group.get('cn', 'Unknown')
                            print(f"   📛 Имя: {group_name}")
                            
                            # Описание
                            if 'description' in group:
                                desc = group['description']
                                if isinstance(desc, list):
                                    desc = desc[0] if desc else ''
                                print(f"   📝 Описание: {desc}")
                            
                            # Участники
                            if 'member' in group:
                                members = group['member']
                                if isinstance(members, list):
                                    print(f"   👥 Участников: {len(members)}")
                                
                        else:
                            print(f"   📛 Значение: {group}")
                else:
                    print("⚠️ Список групп пуст!")
            else:
                print("❌ Ключ 'result' не найден или не является списком")
        else:
            # Старая логика для случая, если это не словарь
            print(f"\n📁 Группа #{i}:")
            print(f"   🔧 Тип: {type(group)}")
            
            if isinstance(group, dict):
                print(f"   📋 Ключи: {list(group.keys())}")
                
                # Извлекаем имя группы
                group_name = None
                if 'cn' in group:
                    cn = group['cn']
                    if isinstance(cn, list):
                        group_name = cn[0] if cn else 'Unknown'
                    else:
                        group_name = cn
                elif 'group_name' in group:
                    group_name = group['group_name']
                
                print(f"   📛 Имя: {group_name}")
                
                # Показываем description если есть
                if 'description' in group:
                    desc = group['description']
                    if isinstance(desc, list):
                        desc = desc[0] if desc else ''
                    print(f"   📝 Описание: {desc}")
                
                # Показываем членов если есть
                if 'member' in group:
                    members = group['member']
                    if isinstance(members, list):
                        print(f"   👥 Участников: {len(members)}")
                    else:
                        print(f"   👥 Участники: {members}")
                
                # Показываем полные данные для первых 3 групп
                if i <= 3:
                    print(f"   🗂️ Полные данные:")
                    for key, value in group.items():
                        if isinstance(value, list) and len(value) > 3:
                            print(f"      {key}: [список из {len(value)} элементов]")
                        else:
                            print(f"      {key}: {value}")
                        
            else:
                print(f"   📛 Значение: {group}")
        
        print("\n" + "=" * 50)
        print("🎯 ИТОГОВЫЙ АНАЛИЗ:")
        
        # Системные группы для сравнения
        system_groups = [
            'admins', 'editors', 'ipausers', 'trust admins',
            'default smb group', 'domain admins', 'domain users'
        ]
        
        user_groups = []
        system_found = []
        
        for group in groups:
            if isinstance(group, dict):
                group_name = group.get('cn', [''])[0] if isinstance(group.get('cn'), list) else group.get('cn', '')
            else:
                group_name = str(group)
            
            if group_name.lower() in [name.lower() for name in system_groups]:
                system_found.append(group_name)
            else:
                user_groups.append(group_name)
        
        print(f"📊 Всего групп: {len(groups)}")
        print(f"🔧 Системных групп: {len(system_found)}")
        print(f"👥 Пользовательских групп: {len(user_groups)}")
        print()
        
        if system_found:
            print("🔧 Найденные системные группы:")
            for group in system_found:
                print(f"   - {group}")
            print()
        
        if user_groups:
            print("👥 Найденные пользовательские группы:")
            for group in user_groups:
                print(f"   - {group}")
        else:
            print("⚠️ Пользовательские группы не найдены!")
        
        print("\n💡 Рекомендации:")
        if not user_groups:
            print("   - Проверьте, существуют ли группы analytics и dev_backup в FreeIPA")
            print("   - Возможно, группы находятся в другом контейнере или OU")
            print("   - Убедитесь, что у пользователя есть права на чтение групп")
        
    except Exception as e:
        print(f"❌ Ошибка диагностики: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose_freeipa_groups())
