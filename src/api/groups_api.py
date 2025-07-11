# -*- coding: utf-8 -*-
"""
API функции для работы с группами Google Workspace.
"""

import logging
from typing import Any, List, Dict
from ..utils.data_cache import data_cache

logger = logging.getLogger(__name__)


def list_groups(service: Any, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Получает все группы домена с кэшированием.
    
    Args:
        service: Сервис (может быть новым ServiceAdapter или старым Google API)
        force_refresh: Принудительное обновление кэша
        
    Returns:
        Список групп с ключами 'email' и 'name'
    """
    try:
        # Сначала проверяем, есть ли у сервиса атрибут groups (новые сервисы)
        if hasattr(service, 'groups') and not callable(getattr(service, 'groups')):
            # Если groups - это атрибут (не метод), возвращаем его
            if service.groups:
                return service.groups
            
            # Если группы пусты, пробуем загрузить их
            if hasattr(service, 'load_groups'):
                try:
                    service.load_groups()
                    return service.groups
                except Exception as e:
                    logger.error(f"Ошибка загрузки групп: {e}")
        
        # Если это Google API сервис (service.groups() - метод)
        if hasattr(service, 'groups') and callable(getattr(service, 'groups')):
            # Получаем группы напрямую через Google API с пагинацией
            all_groups = []
            page_token = None
            
            while True:
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
                
                # Проверяем наличие следующей страницы
                page_token = result.get('nextPageToken')
                if not page_token:
                    break
            
            logger.info(f"Загружено групп через прямой API: {len(all_groups)}")
            return all_groups
            
    except Exception as e:
        logger.error(f"Ошибка получения групп: {e}")
    
    return []


def create_group(service: Any, name: str, email: str, description: str = "") -> str:
    """
    Создает новую группу в Google Workspace.
    
    Args:
        service: Сервис Google Directory API или ServiceAdapter
        name: Название группы
        email: Email адрес группы
        description: Описание группы
        
    Returns:
        Строка с результатом операции
    """
    try:
        group_body = {
            'email': email,
            'name': name,
            'description': description
        }
        
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            # Это ServiceAdapter, получаем прямой доступ к Google API
            try:
                from ..auth import get_service
                google_service = get_service()
                
                group = google_service.groups().insert(body=group_body).execute()
                
                # Очищаем кэш для обновления списка групп
                data_cache.clear_cache()
                
                return f"Группа создана: {group['email']}"
                
            except Exception as e:
                return f'Ошибка создания группы через прямой API: {e}'
        
        # Обычный Google API сервис
        elif hasattr(service, 'groups') and callable(getattr(service, 'groups')):
            group = service.groups().insert(body=group_body).execute()
            
            # Очищаем кэш для обновления списка групп
            data_cache.clear_cache()
            
            return f"Группа создана: {group['email']}"
        
        else:
            return f'Неподдерживаемый тип сервиса: {type(service)}'
        
    except Exception as e:
        return f'Ошибка создания группы: {e}'


def update_group(service: Any, group_email: str, name: str = None, description: str = None) -> str:
    """
    Обновляет данные группы.
    
    Args:
        service: Сервис Google Directory API или ServiceAdapter
        group_email: Email группы
        name: Новое название группы
        description: Новое описание группы
        
    Returns:
        Строка с результатом операции
    """
    try:
        fields = {}
        if name is not None:
            fields['name'] = name
        if description is not None:
            fields['description'] = description
            
        if not fields:
            return "Нет полей для обновления"
        
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            # Это ServiceAdapter, получаем прямой доступ к Google API
            try:
                from ..auth import get_service
                google_service = get_service()
                
                group = google_service.groups().update(groupKey=group_email, body=fields).execute()
                data_cache.clear_cache()
                return f"Группа {group['email']} успешно обновлена."
                
            except Exception as e:
                return f'Ошибка обновления группы через прямой API: {e}'
        
        # Обычный Google API сервис
        elif hasattr(service, 'groups') and callable(getattr(service, 'groups')):
            group = service.groups().update(groupKey=group_email, body=fields).execute()
            data_cache.clear_cache()
            return f"Группа {group['email']} успешно обновлена."
        
        else:
            return f'Неподдерживаемый тип сервиса: {type(service)}'
        
    except Exception as e:
        return f'Ошибка обновления группы: {e}'


def delete_group(service: Any, group_email: str) -> str:
    """
    Удаляет группу из Google Workspace.
    
    Args:
        service: Сервис Google Directory API или ServiceAdapter
        group_email: Email группы для удаления
        
    Returns:
        Строка с результатом операции
    """
    try:
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            # Это ServiceAdapter, получаем прямой доступ к Google API
            try:
                from ..auth import get_service
                google_service = get_service()
                
                google_service.groups().delete(groupKey=group_email).execute()
                data_cache.clear_cache()
                return f"Группа {group_email} успешно удалена."
                
            except Exception as e:
                return f'Ошибка удаления группы через прямой API: {e}'
        
        # Обычный Google API сервис
        elif hasattr(service, 'groups') and callable(getattr(service, 'groups')):
            service.groups().delete(groupKey=group_email).execute()
            data_cache.clear_cache()
            return f"Группа {group_email} успешно удалена."
        
        else:
            return f'Неподдерживаемый тип сервиса: {type(service)}'
        
    except Exception as e:
        return f'Ошибка удаления группы: {e}'


def get_group_members(service: Any, group_email: str) -> List[Dict[str, Any]]:
    """
    Получает список участников группы.
    
    Args:
        service: Сервис Google Directory API или ServiceAdapter
        group_email: Email группы
        
    Returns:
        Список участников группы
    """
    try:
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            # Это ServiceAdapter, получаем прямой доступ к Google API
            try:
                from ..auth import get_service
                google_service = get_service()
                
                members = []
                page_token = None
                
                while True:
                    result = google_service.members().list(
                        groupKey=group_email,
                        maxResults=200,
                        pageToken=page_token
                    ).execute()
                    
                    members.extend(result.get('members', []))
                    page_token = result.get('nextPageToken')
                    
                    if not page_token:
                        break
                        
                return members
                
            except Exception as e:
                print(f"Ошибка получения участников через прямой API: {e}")
                return []
        
        # Обычный Google API сервис
        elif hasattr(service, 'members') and callable(getattr(service, 'members')):
            members = []
            page_token = None
            
            while True:
                result = service.members().list(
                    groupKey=group_email,
                    maxResults=200,
                    pageToken=page_token
                ).execute()
                
                members.extend(result.get('members', []))
                page_token = result.get('nextPageToken')
                
                if not page_token:
                    break
                    
            return members
        
        else:
            print(f"Неподдерживаемый тип сервиса: {type(service)}")
            return []
        
    except Exception as e:
        print(f"Ошибка получения участников группы: {e}")
        return []


def add_user_to_group(service: Any, group_email: str, user_email: str) -> str:
    """
    Добавляет пользователя в группу Google Workspace.
    
    Args:
        service: Сервис Google Directory API или ServiceAdapter
        group_email: Email группы
        user_email: Email пользователя
        
    Returns:
        Строка с результатом операции
    """
    try:
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            # Это ServiceAdapter, получаем прямой доступ к Google API
            try:
                from ..auth import get_service
                google_service = get_service()
                
                body = {
                    'email': user_email,
                    'role': 'MEMBER'
                }
                google_service.members().insert(groupKey=group_email, body=body).execute()
                return f'Пользователь {user_email} добавлен в группу {group_email}.'
                
            except Exception as e:
                if 'Member already exists' in str(e):
                    return f'Пользователь {user_email} уже состоит в группе {group_email}.'
                print(f"[add_user_to_group] Exception через прямой API: {e}")
                return f'Ошибка добавления в группу: {e}'
        
        # Обычный Google API сервис
        elif hasattr(service, 'members') and callable(getattr(service, 'members')):
            body = {
                'email': user_email,
                'role': 'MEMBER'
            }
            service.members().insert(groupKey=group_email, body=body).execute()
            return f'Пользователь {user_email} добавлен в группу {group_email}.'
        
        else:
            return f'Неподдерживаемый тип сервиса: {type(service)}'
        
    except Exception as e:
        if 'Member already exists' in str(e):
            return f'Пользователь {user_email} уже состоит в группе {group_email}.'
        print(f"[add_user_to_group] Exception: {e}")
        return f'Ошибка добавления в группу: {e}'


def remove_user_from_group(service: Any, group_email: str, user_email: str) -> str:
    """
    Удаляет пользователя из группы.
    
    Args:
        service: Сервис Google Directory API или ServiceAdapter
        group_email: Email группы
        user_email: Email пользователя
        
    Returns:
        Строка с результатом операции
    """
    try:
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            # Это ServiceAdapter, получаем прямой доступ к Google API
            try:
                from ..auth import get_service
                google_service = get_service()
                
                google_service.members().delete(groupKey=group_email, memberKey=user_email).execute()
                return f'Пользователь {user_email} удален из группы {group_email}.'
                
            except Exception as e:
                if 'Member not found' in str(e):
                    return f'Пользователь {user_email} не состоит в группе {group_email}.'
                return f'Ошибка удаления из группы через прямой API: {e}'
        
        # Обычный Google API сервис
        elif hasattr(service, 'members') and callable(getattr(service, 'members')):
            service.members().delete(groupKey=group_email, memberKey=user_email).execute()
            return f'Пользователь {user_email} удален из группы {group_email}.'
        
        else:
            return f'Неподдерживаемый тип сервиса: {type(service)}'
        
    except Exception as e:
        if 'Member not found' in str(e):
            return f'Пользователь {user_email} не состоит в группе {group_email}.'
        return f'Ошибка удаления из группы: {e}'
