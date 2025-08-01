#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест функциональности управления организационными подразделениями (OU).
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.api.orgunits_api import list_orgunits, format_orgunits_for_combobox
from src.auth import get_service


def test_ou_functionality():
    """Тестирует основную функциональность OU"""
    try:
        print("🔧 Получение сервиса Google Directory API...")
        service = get_service()
        
        print("📋 Загрузка списка организационных подразделений...")
        orgunits = list_orgunits(service)
        
        print(f"✅ Найдено {len(orgunits)} подразделений:")
        for ou in orgunits:
            path = ou.get('orgUnitPath', '/')
            name = ou.get('name', 'Unknown')
            print(f"  📁 {path} - {name}")
        
        print("\n🎨 Форматированный список для UI:")
        formatted = format_orgunits_for_combobox(orgunits)
        for i, display_name in enumerate(formatted):
            print(f"  {i+1}. {display_name}")
        
        print("\n✅ Тест завершен успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")


if __name__ == "__main__":
    test_ou_functionality()
