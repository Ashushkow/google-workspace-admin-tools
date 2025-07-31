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
