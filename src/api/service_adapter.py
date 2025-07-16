#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Адаптер для совместимости старого GUI с новыми сервисами.
"""

import asyncio
import logging
from typing import Any, List, Dict
from ..services.user_service import UserService
from ..services.group_service import GroupService

logger = logging.getLogger(__name__)


class ServiceAdapter:
    """Адаптер для совместимости со старым GUI"""
    
    def __init__(self, user_service: UserService, group_service: GroupService = None):
        self.user_service = user_service
        self.group_service = group_service
        
        # Свойства для обратной совместимости
        self._users = []
        self._groups = []
        
        # Инициализируем данные из сервисов
        self._initialize_data()
    
    def _initialize_data(self):
        """Инициализация данных из сервисов"""
        try:
            # Простая синхронная инициализация без создания новых event loop'ов
            print("📊 Подготовка к загрузке данных...")
            
            # НЕ инициализируем демо-данные сразу - только при ошибках
            # Откладываем всю загрузку данных до первого запроса
            self._data_loaded = False
            
        except Exception as e:
            print(f"Ошибка инициализации данных: {e}")
            self._demo_fallback_mode = True
            self._initialize_demo_data()
    
    async def _load_data_async(self):
        """Асинхронная загрузка данных из сервисов"""
        try:
            # Сначала пробуем загрузить через новые сервисы
            users = await self.user_service.get_all_users()
            self._users = [
                {
                    'primaryEmail': user.email,
                    'name': {'fullName': user.full_name},
                    'id': user.id,
                    'suspended': getattr(user, 'is_suspended', False),
                    'orgUnitPath': getattr(user, 'org_unit_path', '/')
                }
                for user in users
            ]
            
            # Если новые сервисы вернули мало пользователей, попробуем старый API
            if len(self._users) < 10:  # Слишком мало, должно быть больше
                print(f"Новые сервисы вернули только {len(self._users)} пользователей, пробуем старый API для получения ВСЕХ...")
                try:
                    from ..auth import get_service
                    service = get_service()
                    
                    # Получаем ВСЕХ пользователей с пагинацией
                    all_users = []
                    page_token = None
                    page_count = 0
                    
                    while True:
                        page_count += 1
                        print(f"  Загружаем страницу {page_count}...")
                        
                        # Запрос с максимальным количеством пользователей на странице
                        request_params = {
                            'customer': 'my_customer',
                            'maxResults': 500,  # Максимум за один запрос
                            'orderBy': 'email'
                        }
                        
                        if page_token:
                            request_params['pageToken'] = page_token
                        
                        result = service.users().list(**request_params).execute()
                        page_users = result.get('users', [])
                        
                        if page_users:
                            all_users.extend(page_users)
                            print(f"    Получено {len(page_users)} пользователей на странице {page_count}")
                        
                        # Проверяем есть ли следующая страница
                        page_token = result.get('nextPageToken')
                        if not page_token:
                            break
                        
                        # Защита от бесконечного цикла
                        if page_count > 50:
                            print(f"    Остановлено после {page_count} страниц")
                            break
                    
                    if all_users:
                        self._users = [
                            {
                                'primaryEmail': user.get('primaryEmail', ''),
                                'name': {'fullName': user.get('name', {}).get('fullName', '')},
                                'id': user.get('id', ''),
                                'suspended': user.get('suspended', False),
                                'orgUnitPath': user.get('orgUnitPath', '/')
                            }
                            for user in all_users
                        ]
                        
                        # Сортируем пользователей по email для консистентного порядка
                        self._users.sort(key=lambda user: user.get('primaryEmail', '').lower())
                        print(f"✅ Старый API с пагинацией загрузил {len(self._users)} пользователей!")
                        
                except Exception as old_api_error:
                    print(f"⚠️ Ошибка старого API с пагинацией: {old_api_error}")
            
            # Загружаем группы если сервис доступен
            if self.group_service:
                groups = await self.group_service.get_all_groups()
                self._groups = [
                    {
                        'name': group.name,
                        'email': group.email,
                        'id': group.id,
                        'description': getattr(group, 'description', ''),
                        'directMembersCount': getattr(group, 'members_count', 0)
                    }
                    for group in groups
                ]
            
            # Если группы не загрузились через сервис, пробуем прямой API
            if not self._groups:
                print("Группы пусты, пробуем прямой API...")
                try:
                    from ..auth import get_service
                    service = get_service()
                    
                    # Загружаем группы с пагинацией
                    all_groups = []
                    page_token = None
                    page_count = 0
                    
                    while True:
                        page_count += 1
                        print(f"  Загружаем страницу групп {page_count}...")
                        
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
                            print(f"    ↳ Найдено групп на странице: {len(groups)}")
                        
                        # Проверяем наличие следующей страницы
                        page_token = result.get('nextPageToken')
                        if not page_token:
                            break
                    
                    self._groups = all_groups
                    print(f"✅ Прямой API загрузил {len(self._groups)} групп!")
                    
                except Exception as groups_error:
                    print(f"⚠️ Ошибка загрузки групп через прямой API: {groups_error}")
                
            print(f"Загружены данные из сервисов: {len(self._users)} пользователей, {len(self._groups)} групп")
            
        except Exception as e:
            print(f"Ошибка загрузки из сервисов: {e}")
            
            # Последняя попытка - прямой вызов старого API с полной пагинацией
            try:
                from ..auth import get_service
                service = get_service()
                
                print("Резервный режим: загружаем ВСЕХ пользователей...")
                all_users = []
                page_token = None
                page_count = 0
                
                while True:
                    page_count += 1
                    print(f"  Резервная страница {page_count}...")
                    
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
                        print(f"    Резервно получено {len(page_users)} пользователей")
                    
                    page_token = result.get('nextPageToken')
                    if not page_token:
                        break
                        
                    if page_count > 50:
                        break
                
                if all_users:
                    self._users = [
                        {
                            'primaryEmail': user.get('primaryEmail', ''),
                            'name': {'fullName': user.get('name', {}).get('fullName', '')},
                            'id': user.get('id', ''),
                            'suspended': user.get('suspended', False),
                            'orgUnitPath': user.get('orgUnitPath', '/')
                        }
                        for user in all_users
                    ]
                    
                    # Сортируем пользователей по email для консистентного порядка
                    self._users.sort(key=lambda user: user.get('primaryEmail', '').lower())
                    print(f"✅ Резервный API загрузил {len(self._users)} пользователей")
                else:
                    self._demo_fallback_mode = True
                    self._initialize_demo_data()
                    
            except Exception as fallback_error:
                print(f"❌ Резервный API тоже не работает: {fallback_error}")
                self._demo_fallback_mode = True
                self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Инициализация демонстрационных данных как резерв"""
        self._users = [
            {
                'primaryEmail': 'demo1@example.com',
                'name': {'fullName': 'Демо Пользователь 1'},
                'id': 'demo1',
                'suspended': False,
                'orgUnitPath': '/'
            },
            {
                'primaryEmail': 'demo2@example.com',
                'name': {'fullName': 'Демо Пользователь 2'},
                'id': 'demo2',
                'suspended': False,
                'orgUnitPath': '/'
            }
        ]
        
        self._groups = [
            {
                'name': 'Демо Группа 1',
                'email': 'demo-group1@example.com',
                'id': 'demo-group1',
                'description': 'Демонстрационная группа 1',
                'directMembersCount': 1
            },
            {
                'name': 'Демо Группа 2',
                'email': 'demo-group2@example.com',
                'id': 'demo-group2',
                'description': 'Демонстрационная группа 2',
                'directMembersCount': 1
            }
        ]
        
        # Логируем только в случае fallback'а на демо-данные
        if hasattr(self, '_demo_fallback_mode'):
            print(f"⚠️ Используем резервные демо-данные: {len(self._users)} пользователей, {len(self._groups)} групп")
    
    @property
    def users(self) -> List[Dict[str, Any]]:
        """Список пользователей в старом формате"""
        self._ensure_data_loaded()
        return self._users
    
    @property
    def groups(self) -> List[Dict[str, Any]]:
        """Список групп в старом формате"""
        self._ensure_data_loaded()
        return self._groups
    
    def _ensure_data_loaded(self):
        """Обеспечивает загрузку данных при первом обращении"""
        if not hasattr(self, '_data_loaded') or not self._data_loaded:
            try:
                print("📊 Загрузка всех пользователей из Google Workspace...")
                from ..auth import get_service
                service = get_service()
                
                # Загружаем ВСЕХ пользователей с пагинацией
                all_users = []
                page_token = None
                page_count = 0
                
                while True:
                    page_count += 1
                    print(f"  📄 Загружаем страницу пользователей {page_count}...")
                    
                    # Запрос с максимальным количеством пользователей на странице
                    request_params = {
                        'customer': 'my_customer',
                        'maxResults': 500,  # Максимум за один запрос
                        'orderBy': 'email'
                    }
                    
                    if page_token:
                        request_params['pageToken'] = page_token
                    
                    result = service.users().list(**request_params).execute()
                    page_users = result.get('users', [])
                    
                    if page_users:
                        all_users.extend(page_users)
                        print(f"    ↳ Получено {len(page_users)} пользователей на странице {page_count}")
                    
                    # Проверяем есть ли следующая страница
                    page_token = result.get('nextPageToken')
                    if not page_token:
                        break
                    
                    # Защита от бесконечного цикла
                    if page_count > 50:
                        print(f"    ⚠️ Остановлено после {page_count} страниц")
                        break
                
                if all_users:
                    self._users = [
                        {
                            'primaryEmail': user.get('primaryEmail', ''),
                            'name': {'fullName': user.get('name', {}).get('fullName', '')},
                            'id': user.get('id', ''),
                            'suspended': user.get('suspended', False),
                            'orgUnitPath': user.get('orgUnitPath', '/')
                        }
                        for user in all_users
                    ]
                    
                    # Сортируем пользователей по email для консистентного порядка
                    self._users.sort(key=lambda user: user.get('primaryEmail', '').lower())
                    print(f"✅ Загружено {len(self._users)} пользователей!")
                else:
                    print("⚠️ Не удалось загрузить пользователей, используем демо-данные")
                    self._demo_fallback_mode = True
                    self._initialize_demo_data()

                # Загружаем ВСЕ группы с пагинацией
                print("📊 Загрузка всех групп из Google Workspace...")
                all_groups = []
                page_token = None
                page_count = 0
                
                while True:
                    page_count += 1
                    print(f"  📄 Загружаем страницу групп {page_count}...")
                    
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
                        print(f"    ↳ Найдено групп на странице: {len(groups)}")
                    
                    # Проверяем наличие следующей страницы
                    page_token = result.get('nextPageToken')
                    if not page_token:
                        break
                
                if all_groups:
                    self._groups = all_groups
                    print(f"✅ Загружено {len(self._groups)} групп!")
                else:
                    print("⚠️ Не удалось загрузить группы, используем демо-данные")
                    if not hasattr(self, '_groups') or not self._groups:
                        self._groups = []
                
                self._data_loaded = True
                print(f"🎉 Загрузка завершена: {len(self._users)} пользователей, {len(self._groups)} групп")
                
            except Exception as e:
                print(f"❌ Ошибка загрузки данных: {e}")
                self._demo_fallback_mode = True
                self._initialize_demo_data()
                self._data_loaded = True

    def refresh_data(self):
        """Принудительно обновляет данные из Google Workspace"""
        print("🔄 Принудительное обновление данных...")
        self._data_loaded = False
        self._ensure_data_loaded()
    
    def get_users_count(self) -> int:
        """Возвращает количество загруженных пользователей"""
        self._ensure_data_loaded()
        return len(self._users)
    
    def get_groups_count(self) -> int:
        """Возвращает количество загруженных групп"""
        self._ensure_data_loaded()
        return len(self._groups)


# Функции для обратной совместимости с API
def get_user_list(service: Any, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Получить список пользователей через новый сервис
    
    Args:
        service: Сервис (UserService или ServiceAdapter)
        force_refresh: Принудительное обновление
        
    Returns:
        Список пользователей
    """
    if hasattr(service, 'users'):
        return service.users
    return []


def list_groups(service: Any) -> List[Dict[str, Any]]:
    """
    Получить список групп через новый сервис
    
    Args:
        service: Сервис (GroupService или ServiceAdapter)
        
    Returns:
        Список групп
    """
    if hasattr(service, 'groups'):
        return service.groups
    return []
