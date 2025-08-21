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
    Проверяет существование пользователя по email с retry логикой.
    
    Args:
        service: Сервис Google Directory API
        email: Email пользователя для проверки
        
    Returns:
        True если пользователь найден, False если не найден, None при ошибке
    """
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            service.users().get(userKey=email).execute()
            return True
        except HttpError as e:
            # Проверяем различные варианты ошибки "пользователь не найден"
            if e.resp is not None and hasattr(e.resp, 'status') and e.resp.status == 404:
                return False
            if 'notFound' in str(e):
                return False
            if 'User not found' in str(e):
                return False
            if 'does not exist' in str(e):
                return False
            
            # Обрабатываем ошибку 403 для внешних доменов
            if e.resp is not None and hasattr(e.resp, 'status') and e.resp.status == 403:
                # Проверяем, относится ли email к нашему домену
                email_domain = email.split('@')[-1] if '@' in email else ''
                
                # Получаем домен из конфигурации
                try:
                    from ..config.enhanced_config import config
                    workspace_domain = config.settings.google_workspace_domain
                except ImportError:
                    workspace_domain = "sputnik8.com"  # Fallback
                
                if email_domain != workspace_domain:
                    # Это внешний домен, Google Workspace не может управлять такими пользователями
                    print(f"[user_exists] Email {email} относится к внешнему домену {email_domain}")
                    return False
                else:
                    # Это наш домен, но нет прав доступа - возможно временная проблема
                    print(f"[user_exists] Нет прав доступа к пользователю {email} в нашем домене (попытка {retry_count + 1})")
                    
                    if retry_count < max_retries - 1:
                        import time
                        time.sleep(1)  # Ждем секунду перед повтором
                        retry_count += 1
                        continue
                    else:
                        return None
                        
            # Для других HTTP ошибок - возможно временная проблема
            if retry_count < max_retries - 1:
                print(f"[user_exists] HTTP ошибка для {email} (попытка {retry_count + 1}): {e}")
                import time
                time.sleep(1)
                retry_count += 1
                continue
            else:
                # Логируем неожиданные HTTP ошибки после всех попыток
                print(f"[user_exists] Неожиданная HttpError для {email} после {max_retries} попыток: {e}")
                print(f"[user_exists] Статус ответа: {getattr(e.resp, 'status', 'N/A') if e.resp else 'N/A'}")
                return None
                
        except Exception as e:
            # Проверяем различные варианты ошибки "пользователь не найден"
            if 'notFound' in str(e):
                return False
            if 'User not found' in str(e):
                return False
            if 'does not exist' in str(e):
                return False
                
            # Для других ошибок - возможно временная проблема
            if retry_count < max_retries - 1:
                print(f"[user_exists] Exception для {email} (попытка {retry_count + 1}): {e}")
                import time
                time.sleep(1)
                retry_count += 1
                continue
            else:
                # Логируем неожиданные ошибки после всех попыток
                print(f"[user_exists] Неожиданная Exception для {email} после {max_retries} попыток: {e}")
                print(f"[user_exists] Тип ошибки: {type(e)}")
                return None
    
    # Это не должно произойти, но на всякий случай
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
    # Валидация email
    if not email or '@' not in email:
        return 'Ошибка: Неверный формат email адреса.'
    
    email_domain = email.split('@')[-1]
    
    # Получаем доступные домены из Google Workspace
    try:
        # Пробуем получить информацию о домене из существующих пользователей
        result = service.users().list(domain=email_domain, maxResults=1).execute()
        # Если запрос успешен, значит домен допустим
        allowed_domains = [email_domain]
    except Exception as domain_check_error:
        # Если не удалось проверить напрямую, используем конфигурацию
        try:
            from ..config.enhanced_config import config
            workspace_domain = config.settings.google_workspace_domain
            allowed_domains = [workspace_domain]
        except ImportError:
            workspace_domain = "sputnik8.com"  # Fallback
            allowed_domains = [workspace_domain]
        
        # Также пробуем получить домены из существующих пользователей
        try:
            existing_users = service.users().list(maxResults=5).execute()
            if 'users' in existing_users:
                detected_domains = set()
                for user in existing_users['users']:
                    if 'primaryEmail' in user:
                        domain = user['primaryEmail'].split('@')[-1]
                        detected_domains.add(domain)
                if detected_domains:
                    allowed_domains = list(detected_domains)
                    print(f"[create_user] Автоматически определены домены: {allowed_domains}")
        except Exception as detect_error:
            print(f"[create_user] Не удалось определить домены автоматически: {detect_error}")
    
    if email_domain not in allowed_domains:
        return f'Ошибка: Можно создавать пользователей только в доменах: {", ".join(allowed_domains)}. Указанный email относится к домену {email_domain}.'
    
    # Проверяем существование пользователя
    print(f"[create_user] Проверка существования пользователя: {email}")
    exists = user_exists(service, email)
    print(f"[create_user] Результат проверки: {exists}")
    
    if exists is None:
        # Пытаемся получить новый сервис и повторить проверку
        print(f"[create_user] Получен None от user_exists, пытаемся восстановить...")
        
        try:
            from ..auth import get_service
            new_service = get_service()
            
            if new_service:
                print(f"[create_user] Получен новый сервис, повторная проверка...")
                exists = user_exists(new_service, email)
                print(f"[create_user] Результат с новым сервисом: {exists}")
                
                if exists is not None:
                    print(f"[create_user] Восстановление успешно, используем новый сервис")
                    service = new_service  # Используем новый сервис для создания
                else:
                    error_msg = f'Ошибка: Не удалось проверить существование пользователя {email}. Проверьте права доступа и подключение к Google API.'
                    print(f"[create_user] {error_msg}")
                    return error_msg
            else:
                error_msg = f'Ошибка: Не удалось получить новый сервис для проверки пользователя {email}.'
                print(f"[create_user] {error_msg}")
                return error_msg
                
        except Exception as recovery_error:
            error_msg = f'Ошибка: Не удалось восстановить подключение к API для проверки пользователя {email}. Детали: {recovery_error}'
            print(f"[create_user] {error_msg}")
            return error_msg
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
