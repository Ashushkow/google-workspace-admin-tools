#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест загрузки групп Google Workspace
"""

import sys
import os

# Добавляем корневую папку в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth import get_service
from src.config.enhanced_config import config

def test_groups_loading():
    """Тестирует загрузку групп из Google Workspace"""
    print("🔧 Тестируем загрузку групп...")
    print(f"📋 Используемые scopes:")
    for scope in config.google.scopes:
        print(f"  • {scope}")
    print()
    
    try:
        # Получаем сервис
        print("🔗 Подключаемся к Google API...")
        service = get_service()
        print("✅ Подключение успешно!")
        
        # Тестируем доступ к группам
        print("\n👥 Пытаемся получить список групп...")
        try:
            # Загружаем группы с пагинацией
            all_groups = []
            page_token = None
            page_num = 0
            
            while True:
                page_num += 1
                print(f"  📄 Загружаем страницу {page_num}...")
                
                request_params = {
                    'customer': 'my_customer',
                    'maxResults': 200
                }
                
                if page_token:
                    request_params['pageToken'] = page_token
                
                result = service.groups().list(**request_params).execute()
                groups = result.get('groups', [])
                
                print(f"    ↳ Найдено групп на странице: {len(groups)}")
                
                if groups:
                    all_groups.extend(groups)
                    
                    # Показываем первые несколько групп для примера
                    if page_num == 1:
                        print("    📋 Примеры групп:")
                        for i, group in enumerate(groups[:5]):
                            email = group.get('email', 'N/A')
                            name = group.get('name', 'N/A')
                            members_count = group.get('directMembersCount', 'N/A')
                            print(f"      {i+1}. {email} ({name}) - участников: {members_count}")
                        if len(groups) > 5:
                            print(f"      ... и еще {len(groups) - 5} групп")
                
                # Проверяем наличие следующей страницы
                page_token = result.get('nextPageToken')
                if not page_token:
                    break
            
            print(f"\n✅ Всего загружено групп: {len(all_groups)}")
            
            if all_groups:
                print("\n📊 Анализ загруженных групп:")
                print(f"  🥇 Первая группа: {all_groups[0].get('email', 'N/A')}")
                print(f"  🥉 Последняя группа: {all_groups[-1].get('email', 'N/A')}")
                
                # Проверяем типы групп
                group_types = {}
                for group in all_groups:
                    group_type = group.get('type', 'UNKNOWN')
                    group_types[group_type] = group_types.get(group_type, 0) + 1
                
                print(f"  📈 Типы групп:")
                for gtype, count in group_types.items():
                    print(f"    • {gtype}: {count} групп")
                    
                return True
            else:
                print("⚠️ Группы не найдены!")
                print("Возможные причины:")
                print("  • В домене нет созданных групп")
                print("  • Недостаточно прав доступа")
                print("  • Группы скрыты настройками безопасности")
                return False
                
        except Exception as groups_error:
            print(f"❌ Ошибка при получении групп: {groups_error}")
            if "403" in str(groups_error) or "Insufficient Permission" in str(groups_error):
                print("💡 Это ошибка недостатка прав доступа")
                print("🔧 Scope 'admin.directory.group' должен быть включен")
            return False
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Тест загрузки групп Google Workspace")
    print("=" * 60)
    
    success = test_groups_loading()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Тест пройден успешно!")
    else:
        print("❌ Тест не пройден. Проверьте настройки групп.")
    print("=" * 60)
