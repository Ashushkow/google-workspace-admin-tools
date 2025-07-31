#!/usr/bin/env python3
"""
Отладочный тест для проверки метода list_groups после исправления
"""

import sys
import os
import json
from pathlib import Path

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Принудительно перезагружаем модули
modules_to_reload = [
    'src.services.freeipa_client',
    'src.services.freeipa_safe_import', 
    'src.services.freeipa_client_stub'
]

for module in modules_to_reload:
    if module in sys.modules:
        print(f"🔄 Перезагружаем модуль: {module}")
        del sys.modules[module]

import importlib
try:
    from src.services import freeipa_client
    importlib.reload(freeipa_client)
    print("🔄 Принудительная перезагрузка freeipa_client")
except:
    pass

from src.services.freeipa_client import FreeIPAService, FreeIPAConfig

def debug_list_groups():
    """Отладка метода list_groups"""
    print("🐛 ОТЛАДКА МЕТОДА LIST_GROUPS")
    print("=" * 50)
    
    try:
        # Читаем конфигурацию
        config_path = Path("config/freeipa_config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Создаем конфигурацию FreeIPA
        config = FreeIPAConfig(
            server_url=config_data.get('server_url', ''),
            domain=config_data.get('domain', ''),
            username=config_data.get('username', ''),
            password=config_data.get('password', ''),
            use_kerberos=config_data.get('use_kerberos', False),
            verify_ssl=config_data.get('verify_ssl', True),
            timeout=config_data.get('timeout', 30)
        )
        
        print(f"📡 Сервер: {config.server_url}")
        print(f"👤 Пользователь: {config.username}")
        print()
        
        # Создаем сервис
        service = FreeIPAService(config)
        
        print("🔗 Подключение к FreeIPA...")
        if not service.connect():
            print("❌ Подключение не удалось")
            return
        
        print("✅ Подключение успешно")
        print()
        
        # Тестируем RAW вызов group_find
        print("🔬 Тест 1: RAW вызов client.group_find()...")
        raw_result = service.client.group_find(sizelimit=100)
        print(f"   📊 Тип результата: {type(raw_result)}")
        print(f"   📋 Ключи: {list(raw_result.keys()) if isinstance(raw_result, dict) else 'N/A'}")
        
        if isinstance(raw_result, dict) and 'result' in raw_result:
            groups_count = len(raw_result['result'])
            print(f"   ✅ Найдено групп в 'result': {groups_count}")
        else:
            print(f"   ❌ Неожиданная структура: {raw_result}")
        print()
        
        # Тестируем наш исправленный метод
        print("🔬 Тест 2: Исправленный метод list_groups()...")
        groups = service.list_groups()
        print(f"   📊 После вызова list_groups: тип результата: {type(groups)}")
        print(f"   📊 Количество: {len(groups) if isinstance(groups, list) else 'N/A'}")
        
        if isinstance(groups, list):
            print("   ✅ Метод возвращает список!")
            if groups:
                print(f"   🔍 Первые 3 группы:")
                for i, group in enumerate(groups[:3], 1):
                    if isinstance(group, dict):
                        name = group.get('cn', ['Unknown'])[0] if isinstance(group.get('cn'), list) else group.get('cn', 'Unknown')
                        print(f"      {i}. {name}")
                    else:
                        print(f"      {i}. {group} (неожиданный тип: {type(group)})")
        elif isinstance(groups, dict):
            print(f"   ❌ Метод возвращает словарь вместо списка")
            print(f"   📝 Ключи словаря: {list(groups.keys())}")
            # Возможно, где-то есть обертка, которая снова оборачивает наш результат
        else:
            print(f"   ❌ Метод возвращает неправильный тип: {type(groups)}")
            print(f"   📝 Содержимое: {groups}")
        print()
        
        # Тестируем метод get_groups (алиас)
        print("🔬 Тест 3: Алиас метод get_groups()...")
        groups2 = service.get_groups()
        print(f"   📊 Тип результата: {type(groups2)}")
        print(f"   📊 Количество: {len(groups2) if isinstance(groups2, list) else 'N/A'}")
        
        # Сравнение результатов
        if isinstance(groups, list) and isinstance(groups2, list):
            if len(groups) == len(groups2):
                print("   ✅ Алиас работает корректно (одинаковое количество)")
            else:
                print(f"   ⚠️ Разные результаты: list_groups={len(groups)}, get_groups={len(groups2)}")
        
        # Итоговый результат
        print("\n" + "=" * 50)
        if isinstance(groups, list) and len(groups) > 5:
            print("✅ ИСПРАВЛЕНИЕ РАБОТАЕТ!")
            print(f"   🎯 Найдено {len(groups)} реальных групп FreeIPA")
            print("   🎉 Больше нет проблемы с показом 5 фейковых групп")
        else:
            print("❌ ПРОБЛЕМА ОСТАЕТСЯ!")
            print("   🐛 Метод все еще не работает правильно")
            print("   💡 Возможно, нужна перезагрузка или кэш не обновился")
            
    except Exception as e:
        print(f"❌ Ошибка отладки: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_list_groups()
