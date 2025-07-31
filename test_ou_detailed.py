#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест загрузки всех OU включая дочерние подразделения
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_ou_loading():
    """Тестирует загрузку всех OU"""
    print("🧪 Тест загрузки всех организационных подразделений (включая дочерние)")
    print("=" * 75)
    
    try:
        # Импортируем необходимые модули
        from src.api.orgunits_api import list_orgunits, format_orgunits_for_combobox
        from src.auth import get_service
        
        print("✅ Модули импортированы успешно")
        
        # Получаем сервис
        print("🔑 Получение Google API сервиса...")
        service = get_service()
        print("✅ Сервис получен")
        
        # Загружаем все OU
        print("\n📋 Загрузка всех организационных подразделений...")
        orgunits = list_orgunits(service)
        
        print(f"📊 Всего получено OU: {len(orgunits)}")
        
        if not orgunits:
            print("❌ Не удалось получить OU. Возможные причины:")
            print("   • Недостаточно прав API")
            print("   • Отсутствует scope admin.directory.orgunit")
            print("   • Проблемы с авторизацией")
            return
        
        # Показываем детальную информацию о каждом OU
        print("\n🔍 Детальная информация о всех OU:")
        print("-" * 75)
        
        for i, ou in enumerate(orgunits, 1):
            path = ou.get('orgUnitPath', 'N/A')
            name = ou.get('name', 'N/A')
            description = ou.get('description', 'Нет описания')
            
            print(f"{i:2d}. Путь: {path}")
            print(f"    Имя: {name}")
            print(f"    Описание: {description}")
            print()
        
        # Тестируем форматирование для UI
        print("🎨 Форматирование для пользовательского интерфейса:")
        print("-" * 75)
        
        formatted = format_orgunits_for_combobox(orgunits)
        for i, formatted_name in enumerate(formatted, 1):
            print(f"{i:2d}. {formatted_name}")
        
        # Анализируем иерархию
        print(f"\n📈 Анализ иерархии:")
        print("-" * 75)
        
        levels = {}
        for ou in orgunits:
            path = ou.get('orgUnitPath', '/')
            level = path.count('/') - 1 if path != '/' else 0
            if level not in levels:
                levels[level] = []
            levels[level].append(ou.get('name', 'Unknown'))
        
        for level in sorted(levels.keys()):
            level_name = "Корневой уровень" if level == 0 else f"Уровень {level}"
            ou_names = ", ".join(levels[level])
            print(f"  {level_name}: {ou_names}")
        
        # Проверяем наличие дочерних OU
        child_ous = [ou for ou in orgunits if ou.get('orgUnitPath', '/').count('/') > 1]
        
        if child_ous:
            print(f"\n✅ Найдено {len(child_ous)} дочерних подразделений:")
            for ou in child_ous:
                print(f"  🏢 {ou.get('name')} ({ou.get('orgUnitPath')})")
        else:
            print(f"\n⚠️ Дочерние подразделения не найдены")
            print("   Возможные причины:")
            print("   • В домене нет дочерних OU")
            print("   • Требуется параметр type='all' в API запросе")
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Главная функция"""
    test_ou_loading()
    
    print("\n" + "=" * 75)
    print("🔧 Для исправления проблем с дочерними OU:")
    print("1. Убедитесь, что используется параметр type='all' в API запросе")
    print("2. Проверьте права Service Account")
    print("3. Убедитесь в наличии scope admin.directory.orgunit")

if __name__ == "__main__":
    main()
