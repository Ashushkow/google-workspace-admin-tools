#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенная функция создания пользователей с отправкой приветственных писем.
"""

import logging
from typing import Any, Optional
from .users_api import create_user as base_create_user, user_exists
from .gmail_api import create_gmail_service
from ..utils.data_cache import data_cache
from ..config.enhanced_config import config

logger = logging.getLogger(__name__)


def create_user_with_welcome_email(
    service: Any, 
    gmail_credentials: Any,
    email: str, 
    first_name: str, 
    last_name: str, 
    password: str, 
    admin_email: str,
    secondary_email: Optional[str] = None, 
    phone: Optional[str] = None,
    org_unit_path: Optional[str] = None,
    send_welcome_email: bool = True
) -> str:
    """
    Создаёт нового пользователя в домене и отправляет приветственное письмо.
    
    Args:
        service: Сервис Google Directory API
        gmail_credentials: Credentials для Gmail API
        email: Основной email пользователя
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        password: Пароль пользователя
        admin_email: Email администратора (отправителя письма)
        secondary_email: Дополнительный email (опционально)
        phone: Номер телефона (опционально)
        org_unit_path: Путь к организационному подразделению (опционально)
        send_welcome_email: Отправлять ли приветственное письмо
        
    Returns:
        Строка с результатом операции
    """
    # Сначала создаем пользователя
    creation_result = base_create_user(
        service, email, first_name, last_name, password, 
        secondary_email, phone, org_unit_path
    )
    
    # Проверяем, был ли пользователь создан успешно
    if "создан" not in creation_result.lower():
        return creation_result
    
    # Если пользователь создан и нужно отправить письмо
    if send_welcome_email:
        try:
            # Создаем Gmail сервис
            gmail_service = create_gmail_service(gmail_credentials)
            
            if not gmail_service:
                logger.warning("⚠️ Не удалось инициализировать Gmail сервис")
                return f"{creation_result}\n⚠️ Приветственное письмо не отправлено (ошибка Gmail API)"
            
            # Отправляем приветственное письмо
            full_name = f"{first_name} {last_name}".strip()
            email_sent = gmail_service.send_welcome_email(
                to_email=email,
                user_name=full_name,
                temporary_password=password,
                admin_email=admin_email
            )
            
            if email_sent:
                logger.info(f"✅ Приветственное письмо отправлено: {email}")
                return f"{creation_result}\n✅ Приветственное письмо отправлено на {email}"
            else:
                logger.warning(f"⚠️ Не удалось отправить приветственное письмо: {email}")
                return f"{creation_result}\n⚠️ Приветственное письмо не отправлено (ошибка отправки)"
                
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке приветственного письма: {e}")
            return f"{creation_result}\n❌ Ошибка отправки приветственного письма: {e}"
    
    return creation_result


def create_user_with_auto_welcome(
    service: Any,
    gmail_service: Any,
    email: str, 
    first_name: str, 
    last_name: str, 
    password: str,
    secondary_email: Optional[str] = None, 
    phone: Optional[str] = None,
    org_unit_path: Optional[str] = None
) -> str:
    """
    Создаёт пользователя и автоматически отправляет приветственное письмо
    от имени администратора (из конфигурации).
    
    Args:
        service: Сервис Google Directory API
        gmail_service: Gmail API сервис
        email: Основной email пользователя
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        password: Пароль пользователя
        secondary_email: Дополнительный email (опционально)
        phone: Номер телефона (опционально)
        
    Returns:
        Строка с результатом операции
    """
    # Получаем email администратора из конфигурации
    admin_email = config.settings.google_workspace_admin
    
    return create_user_with_welcome_email(
        service=service,
        gmail_credentials=gmail_service,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        admin_email=admin_email,
        secondary_email=secondary_email,
        phone=phone,
        org_unit_path=org_unit_path,
        send_welcome_email=True
    )


def send_welcome_email_to_existing_user(
    gmail_credentials: Any,
    user_email: str,
    user_name: str,
    temporary_password: str,
    admin_email: str
) -> bool:
    """
    Отправляет приветственное письмо существующему пользователю.
    
    Args:
        gmail_credentials: Credentials для Gmail API
        user_email: Email пользователя
        user_name: Имя пользователя
        temporary_password: Временный пароль
        admin_email: Email администратора
        
    Returns:
        True если письмо отправлено успешно
    """
    try:
        gmail_service = create_gmail_service(gmail_credentials)
        
        if not gmail_service:
            logger.error("❌ Не удалось создать Gmail сервис")
            return False
        
        return gmail_service.send_welcome_email(
            to_email=user_email,
            user_name=user_name,
            temporary_password=temporary_password,
            admin_email=admin_email
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки письма: {e}")
        return False
