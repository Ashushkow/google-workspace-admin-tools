#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сервис для управления Google документами и доступом к ним.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from ..api.drive_api import DriveAPI, DriveFile, DrivePermission

logger = logging.getLogger(__name__)


@dataclass
class DocumentAccessRequest:
    """Запрос на предоставление доступа к документу"""
    document_url: str
    user_email: str
    role: str  # 'reader', 'commenter', 'writer'
    notify: bool = True
    message: Optional[str] = None


@dataclass
class DocumentInfo:
    """Информация о документе с доступами"""
    file_id: str
    name: str
    url: str
    owner: str
    permissions: List[DrivePermission]
    
    
class DocumentService:
    """Сервис для управления документами"""
    
    def __init__(self, credentials):
        """
        Инициализация сервиса
        
        Args:
            credentials: Google API credentials
        """
        self.drive_api = DriveAPI(credentials)
        self.logger = logging.getLogger(__name__)
    
    def get_document_info(self, document_url: str) -> Optional[DocumentInfo]:
        """
        Получает информацию о документе по URL
        
        Args:
            document_url: URL документа Google
            
        Returns:
            Информация о документе или None
        """
        try:
            # Извлекаем ID файла из URL
            file_id = self.drive_api.extract_file_id_from_url(document_url)
            if not file_id:
                self.logger.error(f"Не удалось извлечь ID файла из URL: {document_url}")
                return None
            
            # Получаем информацию о файле
            drive_file = self.drive_api.get_file_info(file_id)
            if not drive_file:
                return None
            
            return DocumentInfo(
                file_id=drive_file.file_id,
                name=drive_file.name,
                url=drive_file.web_view_link,
                owner=drive_file.owner_email or "Неизвестно",
                permissions=drive_file.permissions
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации о документе: {e}")
            return None
    
    def grant_access(self, request: DocumentAccessRequest) -> bool:
        """
        Предоставляет доступ к документу
        
        Args:
            request: Запрос на предоставление доступа
            
        Returns:
            True если доступ предоставлен успешно
        """
        try:
            # Извлекаем ID файла из URL
            file_id = self.drive_api.extract_file_id_from_url(request.document_url)
            if not file_id:
                self.logger.error(f"Не удалось извлечь ID файла из URL: {request.document_url}")
                return False
            
            # Проверяем, что роль валидна
            valid_roles = ['reader', 'commenter', 'writer']
            if request.role not in valid_roles:
                self.logger.error(f"Неверная роль: {request.role}. Допустимые: {valid_roles}")
                return False
            
            # Предоставляем доступ
            success = self.drive_api.add_permission(
                file_id=file_id,
                email=request.user_email,
                role=request.role,
                notify=request.notify,
                message=request.message
            )
            
            if success:
                self.logger.info(f"✅ Доступ предоставлен: {request.user_email} ({request.role}) к документу {file_id}")
            else:
                self.logger.error(f"❌ Не удалось предоставить доступ: {request.user_email} к документу {file_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при предоставлении доступа: {e}")
            return False
    
    def revoke_access(self, document_url: str, user_email: str) -> bool:
        """
        Отзывает доступ к документу
        
        Args:
            document_url: URL документа
            user_email: Email пользователя
            
        Returns:
            True если доступ отозван успешно
        """
        try:
            # Извлекаем ID файла из URL
            file_id = self.drive_api.extract_file_id_from_url(document_url)
            if not file_id:
                self.logger.error(f"Не удалось извлечь ID файла из URL: {document_url}")
                return False
            
            # Получаем список разрешений
            permissions = self.drive_api.get_permissions(file_id)
            
            # Ищем разрешение для указанного пользователя
            permission_to_remove = None
            for perm in permissions:
                if perm.email_address == user_email:
                    permission_to_remove = perm
                    break
            
            if not permission_to_remove:
                self.logger.warning(f"Разрешение для {user_email} не найдено в документе {file_id}")
                return False
            
            # Удаляем разрешение
            success = self.drive_api.remove_permission(file_id, permission_to_remove.permission_id)
            
            if success:
                self.logger.info(f"✅ Доступ отозван: {user_email} к документу {file_id}")
            else:
                self.logger.error(f"❌ Не удалось отозвать доступ: {user_email} к документу {file_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при отзыве доступа: {e}")
            return False
    
    def change_access_role(self, document_url: str, user_email: str, new_role: str) -> bool:
        """
        Изменяет роль пользователя в доступе к документу
        
        Args:
            document_url: URL документа
            user_email: Email пользователя
            new_role: Новая роль ('reader', 'commenter', 'writer')
            
        Returns:
            True если роль изменена успешно
        """
        try:
            # Извлекаем ID файла из URL
            file_id = self.drive_api.extract_file_id_from_url(document_url)
            if not file_id:
                self.logger.error(f"Не удалось извлечь ID файла из URL: {document_url}")
                return False
            
            # Проверяем, что роль валидна
            valid_roles = ['reader', 'commenter', 'writer']
            if new_role not in valid_roles:
                self.logger.error(f"Неверная роль: {new_role}. Допустимые: {valid_roles}")
                return False
            
            # Получаем список разрешений
            permissions = self.drive_api.get_permissions(file_id)
            
            # Ищем разрешение для указанного пользователя
            permission_to_update = None
            for perm in permissions:
                if perm.email_address == user_email:
                    permission_to_update = perm
                    break
            
            if not permission_to_update:
                self.logger.warning(f"Разрешение для {user_email} не найдено в документе {file_id}")
                return False
            
            # Обновляем разрешение
            success = self.drive_api.update_permission(
                file_id, 
                permission_to_update.permission_id, 
                new_role
            )
            
            if success:
                self.logger.info(f"✅ Роль изменена: {user_email} -> {new_role} для документа {file_id}")
            else:
                self.logger.error(f"❌ Не удалось изменить роль: {user_email} для документа {file_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при изменении роли: {e}")
            return False
    
    def list_document_permissions(self, document_url: str) -> List[DrivePermission]:
        """
        Получает список всех разрешений для документа
        
        Args:
            document_url: URL документа
            
        Returns:
            Список разрешений
        """
        try:
            # Извлекаем ID файла из URL
            file_id = self.drive_api.extract_file_id_from_url(document_url)
            if not file_id:
                self.logger.error(f"Не удалось извлечь ID файла из URL: {document_url}")
                return []
            
            # Получаем список разрешений
            permissions = self.drive_api.get_permissions(file_id)
            
            self.logger.info(f"📋 Получено {len(permissions)} разрешений для документа {file_id}")
            return permissions
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка разрешений: {e}")
            return []
    
    def get_role_description(self, role: str) -> str:
        """
        Возвращает описание роли на русском языке
        
        Args:
            role: Роль
            
        Returns:
            Описание роли
        """
        role_descriptions = {
            'reader': 'Чтение',
            'commenter': 'Комментирование', 
            'writer': 'Редактирование',
            'owner': 'Владелец'
        }
        return role_descriptions.get(role, role)
    
    def get_permission_type_description(self, perm_type: str) -> str:
        """
        Возвращает описание типа разрешения на русском языке
        
        Args:
            perm_type: Тип разрешения
            
        Returns:
            Описание типа
        """
        type_descriptions = {
            'user': 'Пользователь',
            'group': 'Группа',
            'domain': 'Домен',
            'anyone': 'Любой'
        }
        return type_descriptions.get(perm_type, perm_type)
