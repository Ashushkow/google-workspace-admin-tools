#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрая проверка количества пользователей и групп в Google Workspace
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрая проверка количества пользователей и групп в Google Workspace
"""

import sys
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def check_users_count():
    """Проверяет количество пользователей и групп"""
    try:
        from src.auth import get_service
        
        print("🔍 Проверка количества пользователей и групп...")
        print("=" * 50)
        
        service = get_service()
        
        # Подсчитываем пользователей
        print("👥 Подсчет пользователей...")
        all_users = []
        page_token = None
        page_count = 0
        
        while True:
            page_count += 1
            print(f"  📄 Загружаем страницу {page_count}...")
            
            request_params = {
                'customer': 'my_customer',
                'maxResults': 500,
                'orderBy': 'email'
            }
            
            if page_token:
                request_params['pageToken'] = page_token
            
            result = service.users().list(**request_params).execute()
            page_users = result.get('users', [])
            
            if page_users:
                all_users.extend(page_users)
                print(f"    ↳ Получено {len(page_users)} пользователей")
            
            page_token = result.get('nextPageToken')
            if not page_token:
                break
            
            if page_count > 50:  # Защита от бесконечного цикла
                break
        
        # Подсчитываем группы
        print("\\n👥 Подсчет групп...")
        all_groups = []
        page_token = None
        page_count = 0
        
        while True:
            page_count += 1
            print(f"  📄 Загружаем страницу {page_count}...")
            
            request_params = {
                'customer': 'my_customer',
                'maxResults': 200
            }
            
            if page_token:
                request_params['pageToken'] = page_token
            
            result = service.groups().list(**request_params).execute()
            groups = result.get('groups', [])
            
            if groups:
                all_groups.extend(groups)
                print(f"    ↳ Найдено {len(groups)} групп")
            
            page_token = result.get('nextPageToken')
            if not page_token:
                break
        
        print("\\n" + "=" * 50)
        print(f"📊 ИТОГО:")
        print(f"👥 Всего пользователей: {len(all_users)}")
        print(f"👥 Всего групп: {len(all_groups)}")
        print("=" * 50)
        
        # Показываем первых 5 пользователей для проверки
        if all_users:
            print("\\n📋 Первые 5 пользователей:")
            for i, user in enumerate(all_users[:5]):
                email = user.get('primaryEmail', 'Нет email')
                name = user.get('name', {}).get('fullName', 'Нет имени')
                suspended = "🔴 Заблокирован" if user.get('suspended') else "🟢 Активен"
                print(f"  {i+1}. {email} - {name} ({suspended})")
        
        if all_groups:
            print("\\n📋 Первые 5 групп:")
            for i, group in enumerate(all_groups[:5]):
                email = group.get('email', 'Нет email')
                name = group.get('name', 'Нет имени')
                print(f"  {i+1}. {email} - {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_users_count()
    sys.exit(0 if success else 1)
