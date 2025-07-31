# -*- coding: utf-8 -*-
"""
API функции для работы с пользователями Google Workspace.
"""

# -*- coding: utf-8 -*-
"""
API функции для работы с пользователями Google Workspace.
"""

from typing import Any, List, Dict, Optional, Tuple
from googleapiclient.errors import HttpError
from ..utils.data_cache import data_cache

# Импортируем адаптер для обратной совместимости
from .service_adapter import get_user_list as adapter_get_user_list

from typing import Any, List, Dict, Optional, Tuple
from googleapiclient.errors import HttpError
from ..utils.data_cache import data_cache


def user_exists(service: Any, email: str) -> Optional[bool]:
    """
    Проверяет существование пользователя по email.
    
    Args:
        service: Сервис Google Directory API
        email: Email пользователя для проверки
        
    Returns:
        True если пользователь найден, False если не найден, None при ошибке
    """
    try:
        service.users().get(userKey=email).execute()
        return True
    except HttpError as e:
        if e.resp is not None and hasattr(e.resp, 'status') and e.resp.status == 404:
            return False
        if 'notFound' in str(e):
            return False
        print(f"[user_exists] HttpError: {e}")
        return None
    except Exception as e:
        if 'notFound' in str(e):
            return False
        print(f"[user_exists] Exception: {e}")
        return None


def create_user(service: Any, email: str, first_name: str, last_name: str, 
                password: str, secondary_email: Optional[str] = None, 
                phone: Optional[str] = None, org_unit_path: Optional[str] = None) -> str:
    """
    Создаёт нового пользователя в домене.
    
    Args:
        service: Сервис Google Directory API
        email: Основной email пользователя
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        password: Пароль пользователя
        secondary_email: Дополнительный email (опционально)
        phone: Номер телефона (опционально)
        org_unit_path: Путь к организационному подразделению (опционально, по умолчанию "/")
        
    Returns:
        Строка с результатом операции
    """
    # Проверяем существование пользователя
    exists = user_exists(service, email)
    if exists is None:
        return 'Ошибка: Не удалось проверить существование пользователя.'
    if exists:
        return f'Пользователь с email {email} уже существует.'
    
    try:
        user_body = {
            'primaryEmail': email,
            'name': {
                'givenName': first_name,
                'familyName': last_name
            },
            'password': password,
            'orgUnitPath': org_unit_path or '/'  # По умолчанию корневое подразделение
        }
        
        # Добавляем дополнительные поля если указаны
        if secondary_email:
            user_body['emails'] = [{'address': secondary_email, 'type': 'home'}]
        if phone:
            user_body['phones'] = [{'value': phone, 'type': 'work'}]
        
        user = service.users().insert(body=user_body).execute()
        
        # Очищаем кэш пользователей для обновления
        data_cache.clear_cache()
        
        org_display = org_unit_path or '/'
        return f"Пользователь создан: {user['primaryEmail']} в подразделении {org_display}"
        
    except Exception as e:
        print(f"[create_user] Exception: {e}")
        return f'Ошибка создания пользователя: {e}'


def update_user(service: Any, email: str, fields: Dict[str, Any]) -> str:
    """
    Изменяет данные пользователя Google Workspace.
    
    Args:
        service: Сервис Google Directory API
        email: Email пользователя
        fields: Словарь с изменяемыми полями
        
    Returns:
        Строка с результатом операции
    """
    try:
        user = service.users().update(userKey=email, body=fields).execute()
        
        # Очищаем кэш для обновления данных
        data_cache.clear_cache()
        
        return f"Данные пользователя {user['primaryEmail']} успешно обновлены."
    except Exception as e:
        return f'Ошибка обновления пользователя: {e}'


def delete_user(service: Any, email: str) -> str:
    """
    Удаляет пользователя из Google Workspace.
    
    Args:
        service: Сервис Google Directory API
        email: Email пользователя для удаления
        
    Returns:
        Строка с результатом операции
    """
    try:
        service.users().delete(userKey=email).execute()
        
        # Очищаем кэш для обновления данных
        data_cache.clear_cache()
        
        return f'Пользователь {email} успешно удалён.'
    except Exception as e:
        return f'Ошибка удаления пользователя: {e}'


def get_user_list(service: Any, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Получает всех пользователей домена с кэшированием для ускорения.
    
    Args:
        service: Сервис (может быть новым ServiceAdapter или старым Google API)
        force_refresh: Принудительное обновление кэша
        
    Returns:
        Список пользователей с основными полями
    """
    # Используем адаптер для новых сервисов
    return adapter_get_user_list(service, force_refresh)


def list_users(service: Any) -> Tuple[str, int]:
    """
    Получение всех пользователей домена для отображения в старом формате.
    
    Args:
        service: Сервис Google Directory API
        
    Returns:
        Кортеж (строка со списком пользователей, количество пользователей)
    """
    try:
        users = get_user_list(service)
        
        if not users:
            return 'Пользователи не найдены.', 0
        
        user_list = '\n'.join([
            f"{user['primaryEmail']} ({user['name']['fullName']})" 
            for user in users
        ])
        
        return user_list, len(users)
        
    except Exception as e:
        return f'Ошибка: {e}', 0
