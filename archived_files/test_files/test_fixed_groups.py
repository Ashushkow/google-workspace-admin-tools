#!/usr/bin/env python3
"""
Простой тест исправленного метода list_groups
"""

import sys
import os
import json
from pathlib import Path

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.services.freeipa_client import FreeIPAService, FreeIPAConfig

def test_fixed_groups():
    """Тест исправленного метода получения групп"""
    print("🧪 ТЕСТ ИСПРАВЛЕННОГО МЕТОДА ПОЛУЧЕНИЯ ГРУПП")
    print("=" * 50)
    
    try:
        # Читаем конфигурацию FreeIPA
        freeipa_config_path = Path("config/freeipa_config.json")
        with open(freeipa_config_path, 'r', encoding='utf-8') as f:
            freeipa_config = json.load(f)
        
        # Создаем конфигурацию
        config = FreeIPAConfig(
            server_url=freeipa_config.get('server_url', ''),
            domain=freeipa_config.get('domain', ''),
            username=freeipa_config.get('username', ''),
            password=freeipa_config.get('password', ''),
            use_kerberos=freeipa_config.get('use_kerberos', False),
            verify_ssl=freeipa_config.get('verify_ssl', True),
            timeout=freeipa_config.get('timeout', 30)
        )
        
        # Создаем сервис
        service = FreeIPAService(config)
        
        print("🔗 Подключение...")
        if not service.connect():
            print("❌ Не удалось подключиться")
            return
        
        print("✅ Подключение успешно")
        
        print("\n📋 Тестируем list_groups()...")
        groups = service.list_groups()
        
        print(f"📊 Тип результата: {type(groups)}")
        print(f"📊 Количество групп: {len(groups) if isinstance(groups, list) else 'N/A'}")
        
        if isinstance(groups, list) and groups:
            print(f"\n🔍 ПЕРВЫЕ 5 ГРУПП:")
            for i, group in enumerate(groups[:5], 1):
                if isinstance(group, dict):
                    name = group.get('cn', ['Unknown'])[0] if isinstance(group.get('cn'), list) else group.get('cn', 'Unknown')
                    print(f"  {i}. {name}")
                else:
                    print(f"  {i}. {group} (тип: {type(group)})")
            
            print(f"\n🎯 НАЙДЕННЫЕ ГРУППЫ (analytics, dev_backup):")
            analytics_found = False
            dev_backup_found = False
            
            for group in groups:
                if isinstance(group, dict):
                    name = group.get('cn', [''])[0] if isinstance(group.get('cn'), list) else group.get('cn', '')
                    if name.lower() == 'analytics':
                        analytics_found = True
                        print(f"  ✅ analytics - {group}")
                    elif name.lower() == 'dev_backup':
                        dev_backup_found = True
                        print(f"  ✅ dev_backup - {group}")
            
            if not analytics_found:
                print("  ❌ analytics не найдена")
            if not dev_backup_found:
                print("  ❌ dev_backup не найдена")
                
            print(f"\n📊 ИТОГО НАЙДЕНО: {len(groups)} групп")
            print("✅ Метод list_groups работает правильно!" if isinstance(groups, list) else "❌ Метод возвращает неправильный тип")
        else:
            print("❌ Группы не найдены или неправильный формат")
            
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_groups()
