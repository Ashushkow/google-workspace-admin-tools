# -*- coding: utf-8 -*-
"""
API функции для работы с группами Google Workspace.
"""

from typing import Any, List, Dict
from ..utils.data_cache import data_cache


def list_groups(service: Any, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Получает все группы домена с кэшированием.
    
    Args:
        service: Сервис Google Directory API
        force_refresh: Принудительное обновление кэша
        
    Returns:
        Список групп с ключами 'email' и 'name'
    """
    return data_cache.get_groups(service, force_refresh)


def create_group(service: Any, email: str, name: str, description: str = "") -> str:
    """
    Создает новую группу в Google Workspace.
    
    Args:
        service: Сервис Google Directory API
        email: Email адрес группы
        name: Название группы
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
        
        group = service.groups().insert(body=group_body).execute()
        
        # Очищаем кэш для обновления списка групп
        data_cache.clear_cache()
        
        return f"Группа создана: {group['email']}"
        
    except Exception as e:
        return f'Ошибка создания группы: {e}'


def update_group(service: Any, group_email: str, fields: Dict[str, Any]) -> str:
    """
    Обновляет данные группы.
    
    Args:
        service: Сервис Google Directory API
        group_email: Email группы
        fields: Словарь с обновляемыми полями
        
    Returns:
        Строка с результатом операции
    """
    try:
        group = service.groups().update(groupKey=group_email, body=fields).execute()
        data_cache.clear_cache()
        return f"Группа {group['email']} успешно обновлена."
        
    except Exception as e:
        return f'Ошибка обновления группы: {e}'


def delete_group(service: Any, group_email: str) -> str:
    """
    Удаляет группу из Google Workspace.
    
    Args:
        service: Сервис Google Directory API
        group_email: Email группы для удаления
        
    Returns:
        Строка с результатом операции
    """
    try:
        service.groups().delete(groupKey=group_email).execute()
        data_cache.clear_cache()
        return f"Группа {group_email} успешно удалена."
        
    except Exception as e:
        return f'Ошибка удаления группы: {e}'


def get_group_members(service: Any, group_email: str) -> List[Dict[str, Any]]:
    """
    Получает список участников группы.
    
    Args:
        service: Сервис Google Directory API
        group_email: Email группы
        
    Returns:
        Список участников группы
    """
    try:
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
        
    except Exception as e:
        print(f"Ошибка получения участников группы: {e}")
        return []


def add_user_to_group(service: Any, group_email: str, user_email: str) -> str:
    """
    Добавляет пользователя в группу Google Workspace.
    
    Args:
        service: Сервис Google Directory API
        group_email: Email группы
        user_email: Email пользователя
        
    Returns:
        Строка с результатом операции
    """
    try:
        body = {
            'email': user_email,
            'role': 'MEMBER'
        }
        service.members().insert(groupKey=group_email, body=body).execute()
        return f'Пользователь {user_email} добавлен в группу {group_email}.'
        
    except Exception as e:
        if 'Member already exists' in str(e):
            return f'Пользователь {user_email} уже состоит в группе {group_email}.'
        print(f"[add_user_to_group] Exception: {e}")
        return f'Ошибка добавления в группу: {e}'


def remove_user_from_group(service: Any, group_email: str, user_email: str) -> str:
    """
    Удаляет пользователя из группы.
    
    Args:
        service: Сервис Google Directory API
        group_email: Email группы
        user_email: Email пользователя
        
    Returns:
        Строка с результатом операции
    """
    try:
        service.members().delete(groupKey=group_email, memberKey=user_email).execute()
        return f'Пользователь {user_email} удален из группы {group_email}.'
        
    except Exception as e:
        if 'Member not found' in str(e):
            return f'Пользователь {user_email} не состоит в группе {group_email}.'
        return f'Ошибка удаления из группы: {e}'
