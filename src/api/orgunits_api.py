# -*- coding: utf-8 -*-
"""
API функции для работы с организационными подразделениями (OU) Google Workspace.
"""

import logging
from typing import Any, List, Dict, Optional
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


def list_orgunits(service: Any) -> List[Dict[str, Any]]:
    """
    Получает список всех организационных подразделений в домене.
    
    Args:
        service: Сервис Google Directory API
        
    Returns:
        Список организационных подразделений
    """
    try:
        logger.info("📋 Получение списка организационных подразделений...")
        
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            # Это ServiceAdapter, получаем прямой доступ к Google API
            try:
                from ..auth import get_service
                google_service = get_service()
                result = google_service.orgunits().list(
                    customerId='my_customer',
                    type='all'  # Получаем все OU включая дочерние
                ).execute()
            except ImportError:
                logger.warning("⚠️ Не удалось получить прямой доступ к Google API")
                return []
        else:
            # Прямой Google API service
            result = service.orgunits().list(
                customerId='my_customer',
                type='all'  # Получаем все OU включая дочерние
            ).execute()
        
        orgunits = result.get('organizationUnits', [])
        
        # Добавляем корневое подразделение
        root_orgunit = {
            'name': 'Root Organization',
            'orgUnitPath': '/',
            'description': 'Корневое подразделение'
        }
        
        # Создаем список с корневым подразделением в начале
        all_orgunits = [root_orgunit] + orgunits
        
        logger.info(f"✅ Получено {len(all_orgunits)} организационных подразделений")
        
        return all_orgunits
        
    except HttpError as e:
        if e.resp.status == 403:
            logger.error("❌ Недостаточно прав для получения списка OU")
            logger.error("💡 Убедитесь, что у Service Account есть права Admin SDK API")
        else:
            logger.error(f"❌ HTTP ошибка при получении OU: {e}")
        return []
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка OU: {e}")
        return []


def get_orgunit(service: Any, org_unit_path: str) -> Optional[Dict[str, Any]]:
    """
    Получает информацию о конкретном организационном подразделении.
    
    Args:
        service: Сервис Google Directory API
        org_unit_path: Путь к организационному подразделению
        
    Returns:
        Информация об организационном подразделении или None
    """
    try:
        logger.info(f"📋 Получение информации об OU: {org_unit_path}")
        
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            try:
                from ..auth import get_service
                google_service = get_service()
                result = google_service.orgunits().get(
                    customerId='my_customer', 
                    orgUnitPath=org_unit_path
                ).execute()
            except ImportError:
                logger.warning("⚠️ Не удалось получить прямой доступ к Google API")
                return None
        else:
            result = service.orgunits().get(
                customerId='my_customer', 
                orgUnitPath=org_unit_path
            ).execute()
        
        logger.info(f"✅ Получена информация об OU: {result.get('name', 'Unknown')}")
        return result
        
    except HttpError as e:
        if e.resp.status == 404:
            logger.warning(f"⚠️ OU не найдено: {org_unit_path}")
        elif e.resp.status == 403:
            logger.error("❌ Недостаточно прав для получения информации об OU")
        else:
            logger.error(f"❌ HTTP ошибка при получении OU: {e}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения информации об OU: {e}")
        return None


def create_orgunit(service: Any, name: str, parent_path: str = "/", 
                  description: str = "") -> Optional[Dict[str, Any]]:
    """
    Создает новое организационное подразделение.
    
    Args:
        service: Сервис Google Directory API
        name: Название подразделения
        parent_path: Путь к родительскому подразделению (по умолчанию корень)
        description: Описание подразделения
        
    Returns:
        Информация о созданном подразделении или None
    """
    try:
        logger.info(f"➕ Создание OU: {name} в {parent_path}")
        
        orgunit_body = {
            'name': name,
            'parentOrgUnitPath': parent_path,
            'description': description
        }
        
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            try:
                from ..auth import get_service
                google_service = get_service()
                result = google_service.orgunits().insert(
                    customerId='my_customer',
                    body=orgunit_body
                ).execute()
            except ImportError:
                logger.warning("⚠️ Не удалось получить прямой доступ к Google API")
                return None
        else:
            result = service.orgunits().insert(
                customerId='my_customer',
                body=orgunit_body
            ).execute()
        
        logger.info(f"✅ OU создано: {result.get('name', 'Unknown')}")
        return result
        
    except HttpError as e:
        if e.resp.status == 403:
            logger.error("❌ Недостаточно прав для создания OU")
        elif e.resp.status == 409:
            logger.error(f"❌ OU с таким именем уже существует: {name}")
        else:
            logger.error(f"❌ HTTP ошибка при создании OU: {e}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания OU: {e}")
        return None


def get_orgunit_display_name(org_unit_path: str) -> str:
    """
    Преобразует путь OU в читаемое название для отображения.
    
    Args:
        org_unit_path: Путь к OU (например, "/IT/Developers")
        
    Returns:
        Читаемое название OU
    """
    if org_unit_path == "/":
        return "🏠 Корневое подразделение"
    
    # Убираем начальный слэш и заменяем слэши на стрелки
    clean_path = org_unit_path.lstrip("/")
    if "/" in clean_path:
        return f"🏢 {clean_path.replace('/', ' → ')}"
    else:
        return f"🏢 {clean_path}"


def format_orgunits_for_combobox(orgunits: List[Dict[str, Any]]) -> List[str]:
    """
    Форматирует список OU для отображения в Combobox.
    
    Args:
        orgunits: Список организационных подразделений
        
    Returns:
        Список отформатированных названий OU
    """
    formatted = []
    
    # Сортируем OU по пути для правильного иерархического отображения
    sorted_orgunits = sorted(orgunits, key=lambda ou: ou.get('orgUnitPath', '/'))
    
    for ou in sorted_orgunits:
        path = ou.get('orgUnitPath', '/')
        name = ou.get('name', 'Unknown')
        
        if path == "/":
            formatted.append("🏠 Корневое подразделение")
        else:
            # Добавляем отступы для визуального отображения иерархии
            level = path.count('/') - 1
            indent = "  " * level
            formatted.append(f"{indent}🏢 {name}")
    
    return formatted


def get_orgunit_path_from_display_name(display_name: str, orgunits: List[Dict[str, Any]]) -> str:
    """
    Получает путь OU по его отображаемому названию.
    
    Args:
        display_name: Отображаемое название OU
        orgunits: Список всех OU
        
    Returns:
        Путь к OU
    """
    if "Корневое подразделение" in display_name:
        return "/"
    
    # Убираем форматирование (отступы, эмодзи) и получаем чистое имя
    clean_name = display_name.replace("🏢", "").replace("🏠", "").strip()
    
    # Ищем OU с точно таким же именем
    for ou in orgunits:
        ou_name = ou.get('name', '').strip()
        if ou_name == clean_name:
            return ou.get('orgUnitPath', '/')
    
    return "/"  # По умолчанию возвращаем корень


def get_user_orgunit(service: Any, user_email: str) -> str:
    """
    Получает путь OU для конкретного пользователя.
    
    Args:
        service: Сервис Google Directory API
        user_email: Email пользователя
        
    Returns:
        Путь к OU пользователя
    """
    try:
        logger.info(f"📋 Получение OU для пользователя: {user_email}")
        
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            try:
                from ..auth import get_service
                google_service = get_service()
                user = google_service.users().get(userKey=user_email).execute()
            except ImportError:
                logger.warning("⚠️ Не удалось получить прямой доступ к Google API")
                return "/"
        else:
            # Прямой Google API service
            user = service.users().get(userKey=user_email).execute()
        
        org_unit_path = user.get('orgUnitPath', '/')
        logger.info(f"✅ OU пользователя {user_email}: {org_unit_path}")
        
        return org_unit_path
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения OU для пользователя {user_email}: {e}")
        return "/"


def get_display_name_for_orgunit_path(org_unit_path: str, orgunits: List[Dict[str, Any]]) -> str:
    """
    Получает отображаемое название OU по его пути.
    
    Args:
        org_unit_path: Путь к OU
        orgunits: Список всех OU
        
    Returns:
        Отображаемое название OU
    """
    if org_unit_path == "/":
        return "🏠 Корневое подразделение"
    
    # Ищем OU с указанным путем
    for ou in orgunits:
        if ou.get('orgUnitPath', '') == org_unit_path:
            name = ou.get('name', 'Unknown')
            # Добавляем отступы для визуального отображения иерархии
            level = org_unit_path.count('/') - 1
            indent = "  " * level
            return f"{indent}🏢 {name}"
    
    return "🏠 Корневое подразделение"  # По умолчанию возвращаем корень


def move_user_to_orgunit(service: Any, user_email: str, org_unit_path: str) -> Dict[str, Any]:
    """
    Перемещает пользователя в указанное организационное подразделение.
    
    Args:
        service: Сервис Google Directory API
        user_email: Email пользователя
        org_unit_path: Путь к целевому OU
        
    Returns:
        Результат операции с информацией об успехе/ошибке
    """
    try:
        logger.info(f"📁 Перемещение пользователя {user_email} в OU: {org_unit_path}")
        
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            try:
                from ..auth import get_service
                google_service = get_service()
                result = google_service.users().update(
                    userKey=user_email,
                    body={'orgUnitPath': org_unit_path}
                ).execute()
            except ImportError:
                logger.warning("⚠️ Не удалось получить прямой доступ к Google API")
                return {
                    'success': False,
                    'message': 'Ошибка доступа к Google API'
                }
        else:
            # Прямой Google API service
            result = service.users().update(
                userKey=user_email,
                body={'orgUnitPath': org_unit_path}
            ).execute()
        
        logger.info(f"✅ Пользователь {user_email} успешно перемещен в OU: {org_unit_path}")
        
        return {
            'success': True,
            'message': f'Пользователь успешно перемещен в {org_unit_path}',
            'user': result
        }
        
    except HttpError as e:
        if e.resp.status == 403:
            logger.error("❌ Недостаточно прав для перемещения пользователя")
            error_msg = "Недостаточно прав для перемещения пользователя в OU"
        elif e.resp.status == 404:
            logger.error("❌ Пользователь или OU не найден")
            error_msg = "Пользователь или организационное подразделение не найдено"
        else:
            logger.error(f"❌ HTTP ошибка при перемещении пользователя: {e}")
            error_msg = f"HTTP ошибка: {e}"
            
        return {
            'success': False,
            'message': error_msg
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка перемещения пользователя {user_email} в OU {org_unit_path}: {e}")
        return {
            'success': False,
            'message': f'Ошибка перемещения пользователя: {e}'
        }


def create_orgunit(service: Any, name: str, parent_ou_path: str = "/", description: str = "") -> Dict[str, Any]:
    """
    Создает новое организационное подразделение.
    
    Args:
        service: Сервис Google Directory API
        name: Название OU
        parent_ou_path: Путь к родительскому OU (по умолчанию корневое)
        description: Описание OU
        
    Returns:
        Результат операции с информацией об успехе/ошибке
    """
    try:
        logger.info(f"📁 Создание нового OU: {name} в {parent_ou_path}")
        
        # Формируем путь к новому OU
        if parent_ou_path == "/":
            new_ou_path = f"/{name}"
        else:
            new_ou_path = f"{parent_ou_path}/{name}"
        
        ou_body = {
            'name': name,
            'orgUnitPath': new_ou_path,
            'parentOrgUnitPath': parent_ou_path
        }
        
        if description:
            ou_body['description'] = description
        
        # Проверяем, является ли service объектом ServiceAdapter
        if hasattr(service, '_users') and hasattr(service, '_groups'):
            try:
                from ..auth import get_service
                google_service = get_service()
                result = google_service.orgunits().insert(
                    customerId='my_customer',
                    body=ou_body
                ).execute()
            except ImportError:
                logger.warning("⚠️ Не удалось получить прямой доступ к Google API")
                return {
                    'success': False,
                    'message': 'Ошибка доступа к Google API'
                }
        else:
            # Прямой Google API service
            result = service.orgunits().insert(
                customerId='my_customer',
                body=ou_body
            ).execute()
        
        logger.info(f"✅ OU {name} успешно создано по пути: {new_ou_path}")
        
        return {
            'success': True,
            'message': f'Подразделение "{name}" успешно создано',
            'orgunit': result,
            'path': new_ou_path
        }
        
    except HttpError as e:
        if e.resp.status == 403:
            logger.error("❌ Недостаточно прав для создания OU")
            error_msg = "Недостаточно прав для создания организационного подразделения"
        elif e.resp.status == 409:
            logger.error("❌ OU с таким именем уже существует")
            error_msg = "Подразделение с таким именем уже существует"
        else:
            logger.error(f"❌ HTTP ошибка при создании OU: {e}")
            error_msg = f"HTTP ошибка: {e}"
            
        return {
            'success': False,
            'message': error_msg
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания OU {name}: {e}")
        return {
            'success': False,
            'message': f'Ошибка создания подразделения: {e}'
        }
