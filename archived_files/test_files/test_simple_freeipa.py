#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест FreeIPA подключения
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_simple():
    """Простой тест подключения"""
    print("🧪 Простой тест FreeIPA...")
    
    try:
        from src.services.freeipa_safe_import import create_freeipa_client
        
        # Создаем клиент
        client = create_freeipa_client(
            server="ipa001.infra.int.sputnik8.com",
            verify_ssl=False,
            timeout=30
        )
        
        print(f"✅ Клиент создан: {type(client).__name__}")
        
        # Тест логина
        success = client.login("Ashushkow", "Kudrovo95!")
        print(f"📡 Логин: {'✅ Успешно' if success else '❌ Неудача'}")
        
        if success:
            # Тест API
            try:
                groups = client.group_find()
                print(f"📁 Получение групп: ✅ Успешно")
                print(f"📊 Данные: {type(groups)} - {len(str(groups))} символов")
                if 'result' in groups:
                    print(f"🔢 Количество групп: {len(groups.get('result', []))}")
            except Exception as e:
                print(f"📁 Получение групп: ❌ Ошибка - {e}")
            
            client.logout()
            print("🔓 Логаут выполнен")
            
        return success
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_simple()
    print(f"\n🏁 Результат: {'✅ УСПЕХ' if result else '❌ НЕУДАЧА'}")
    if result:
        print("🎉 FreeIPA интеграция работает!")
        print("🚀 Можно запускать основное приложение")
    sys.exit(0 if result else 1)
