#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Адаптер для совместимости старого GUI с новыми сервисами.
"""

import asyncio
import logging
import os
from typing import Any, List, Dict, Optional
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
        self._demo_fallback_mode: bool = False
        self._demo_reason: Optional[str] = None  # Причина, по которой включён демо-режим

        # НЕ инициализируем данные сразу - только при первом обращении
        self._data_loaded = False
    
    def _initialize_data(self):
        """Подготовка к отложенной загрузке данных"""
        try:
            # Не выполняем никаких сетевых операций при создании адаптера
            print("📊 ServiceAdapter инициализирован (данные будут загружены при первом обращении)")
            self._data_loaded = False
            
        except Exception as e:
            print(f"Ошибка инициализации адаптера: {e}")
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
    
    def _activate_demo_fallback(self, reason: str, exc: Exception = None):
        """Активация режима демонстрационных данных с указанием причины.

        Если установлен DISABLE_DEMO_FALLBACK=true, выбрасывает исключение
        вместо тихого перехода в демо-режим, чтобы пользователь сразу увидел проблему.
        """
        self._demo_reason = reason
        disable = os.getenv('DISABLE_DEMO_FALLBACK', 'false').lower() == 'true'
        if disable:
            # Эскалируем ошибку, не маскируя её демо-режимом
            raise RuntimeError(f"Demo fallback disabled. Reason: {reason}. Original error: {exc}") from exc
        self._demo_fallback_mode = True
        if exc:
            print(f"⚠️ Переход на демо-данные: {reason} (исключение: {exc})")
        else:
            print(f"⚠️ Переход на демо-данные: {reason}")
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        """Инициализация демонстрационных данных как резерв"""
        print("⚠️ ВНИМАНИЕ: Используются демонстрационные данные!")
        if self._demo_reason:
            print(f"⚠️ Причина: {self._demo_reason}")
        print("⚠️ Проверьте конфигурацию Google API в config/settings.json")
        
        self._users = [
            {
                'primaryEmail': f'demo1@{self._get_configured_domain()}',
                'name': {'fullName': 'Демо Пользователь 1 (ТЕСТ)'},
                'id': 'demo1',
                'suspended': False,
                'orgUnitPath': '/'
            },
            {
                'primaryEmail': f'demo2@{self._get_configured_domain()}',
                'name': {'fullName': 'Демо Пользователь 2 (ТЕСТ)'},
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
        if self._demo_fallback_mode:
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
                import time
                import os
                start_time = time.time()
                timeout_seconds = 120  # 2 минуты максимум на загрузку
                
                # Проверяем режим быстрой загрузки
                fast_mode = os.getenv('FAST_LOAD_MODE', 'False').lower() == 'true'
                if fast_mode:
                    print("🚀 Быстрый режим активирован")
                    self._activate_demo_fallback("FAST_LOAD_MODE=true (быстрый режим)")
                    self._data_loaded = True
                    return
                
                print("📊 Загрузка всех пользователей из Google Workspace...")
                
                # Попытка получить сервис с таймаутом
                try:
                    from ..auth import get_service
                    service = get_service()
                    print("✅ Авторизация успешна!")
                except (TimeoutError, Exception) as e:
                    print(f"❌ Ошибка авторизации: {e}")
                    try:
                        self._activate_demo_fallback("Ошибка авторизации / получения сервиса", e)
                    except Exception as escalated:
                        # При отключённом демо-режиме эскалируем исключение выше
                        raise
                    self._data_loaded = True
                    return
                
                # Загружаем ВСЕХ пользователей с пагинацией
                all_users = []
                page_token = None
                page_count = 0
                max_user_pages = 30  # Максимум страниц для пользователей
                
                while page_count < max_user_pages:
                    # Проверяем тайм-аут
                    if time.time() - start_time > timeout_seconds:
                        print("⏰ Превышен тайм-аут загрузки пользователей")
                        try:
                            self._activate_demo_fallback("Тайм-аут загрузки пользователей > 120с")
                        except Exception:
                            raise
                        self._data_loaded = True
                        return
                    
                    page_count += 1
                    print(f"  📄 Загружаем страницу пользователей {page_count}...")
                    
                    try:
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
                            print(f"    ↳ Получено {len(page_users)} пользователей на странице {page_count} (всего: {len(all_users)})")
                        else:
                            print(f"    ⚠️ Страница {page_count} пуста, завершаем загрузку пользователей")
                            break
                        
                        # Проверяем есть ли следующая страница
                        page_token = result.get('nextPageToken')
                        if not page_token:
                            print(f"    🏁 Достигнута последняя страница пользователей")
                            break
                            
                    except Exception as user_page_error:
                        print(f"    ❌ Ошибка загрузки страницы пользователей {page_count}: {user_page_error}")
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
                    print("⚠️ Не удалось загрузить ни одного пользователя")
                    try:
                        self._activate_demo_fallback("Пустой список пользователей из API")
                    except Exception:
                        raise

                # Загружаем ВСЕ группы с пагинацией
                # Проверяем, не потратили ли мы уже слишком много времени на пользователей
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout_seconds * 0.7:  # Если потратили больше 70% времени
                    print(f"⏰ Загрузка пользователей заняла {elapsed_time:.1f}с, пропускаем группы")
                    self._groups = []
                    self._data_loaded = True
                    print(f"🎉 Загрузка завершена: {len(self._users)} пользователей, 0 групп (тайм-аут)")
                    return
                
                print("📊 Загрузка всех групп из Google Workspace...")
                all_groups = []
                page_token = None
                page_count = 0
                max_pages = 50  # Защита от бесконечного цикла
                
                while page_count < max_pages:
                    # Проверяем тайм-аут
                    if time.time() - start_time > timeout_seconds:
                        print("⏰ Превышен тайм-аут загрузки групп, завершаем операцию")
                        break
                    
                    page_count += 1
                    print(f"  📄 Загружаем страницу групп {page_count}...")
                    
                    try:
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
                        else:
                            print(f"    ⚠️ Страница {page_count} пуста, завершаем загрузку")
                            break
                        
                        # Проверяем наличие следующей страницы
                        page_token = result.get('nextPageToken')
                        if not page_token:
                            print(f"    🏁 Достигнута последняя страница")
                            break
                            
                    except Exception as page_error:
                        print(f"    ❌ Ошибка загрузки страницы {page_count}: {page_error}")
                        break
                
                if page_count >= max_pages:
                    print(f"    ⚠️ Остановлено после {max_pages} страниц (защита от зацикливания)")
                
                if all_groups:
                    self._groups = all_groups
                    print(f"✅ Загружено {len(self._groups)} групп!")
                else:
                    print("⚠️ Не удалось загрузить группы, используем демо-данные")
                    if not hasattr(self, '_groups') or not self._groups:
                        self._groups = []
                
                self._data_loaded = True
                end_time = time.time()
                total_time = end_time - start_time
                print(f"🎉 Загрузка завершена за {total_time:.1f}с: {len(self._users)} пользователей, {len(self._groups)} групп")
                
            except Exception as e:
                print(f"❌ Ошибка загрузки данных: {e}")
                try:
                    self._activate_demo_fallback("Общая ошибка при загрузке данных", e)
                except Exception:
                    raise
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
    
    def _get_configured_domain(self) -> str:
        """Получить настроенный домен из конфигурации"""
        try:
            from ..config.enhanced_config import config
            domain = config.settings.google_workspace_domain
            if domain and domain != "yourdomain.com":
                return domain
            return "example.com"
        except:
            return "example.com"
    
    def get_credentials(self):
        """
        Получает credentials, используемые для авторизации Google API
        
        Returns:
            Google credentials object
        """
        try:
            # Импортируем auth только при необходимости
            from ..auth import get_service
            
            # Получаем сервис и извлекаем из него credentials
            service = get_service()
            
            # У сервиса Google API есть свойство _http с credentials
            if hasattr(service, '_http') and hasattr(service._http, 'credentials'):
                return service._http.credentials
            
            # Альтернативный способ через прямое получение credentials
            from ..auth import detect_credentials_type, get_service_account_credentials, get_oauth2_credentials
            
            creds_type = detect_credentials_type()
            if creds_type == 'service_account':
                return get_service_account_credentials()
            elif creds_type == 'oauth2':
                return get_oauth2_credentials()
            else:
                raise ValueError(f"Неподдерживаемый тип credentials: {creds_type}")
                
        except Exception as e:
            logger.error(f"Ошибка получения credentials: {e}")
            raise


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
