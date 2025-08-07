#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive API для управления доступом к файлам и папкам.
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    build = None
    HttpError = Exception

logger = logging.getLogger(__name__)


@dataclass
class DrivePermission:
    """Разрешение на доступ к файлу/папке"""
    permission_id: str
    email_address: str
    role: str  # 'reader', 'commenter', 'writer', 'owner'
    permission_type: str  # 'user', 'group', 'domain', 'anyone'
    display_name: Optional[str] = None


@dataclass
class DriveFile:
    """Информация о файле Google Drive"""
    file_id: str
    name: str
    mime_type: str
    web_view_link: str
    permissions: List[DrivePermission]
    owner_email: Optional[str] = None


class DriveAPI:
    """API для работы с Google Drive"""
    
    def __init__(self, credentials):
        """
        Инициализация Drive API
        
        Args:
            credentials: Google API credentials
        """
        self.credentials = credentials
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self) -> bool:
        """
        Инициализация сервиса Google Drive
        
        Returns:
            True если инициализация успешна
        """
        try:
            if build is None:
                logger.error("Google API библиотеки не установлены")
                return False
            
            self.service = build('drive', 'v3', credentials=self.credentials)
            logger.info("✅ Google Drive API успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Google Drive API: {e}")
            return False
    
    def extract_file_id_from_url(self, url: str) -> Optional[str]:
        """
        Извлекает ID файла из URL Google Docs/Sheets/Slides
        
        Args:
            url: URL документа Google
            
        Returns:
            ID файла или None
        """
        try:
            # Поддерживаемые форматы URL:
            # https://docs.google.com/document/d/FILE_ID/edit
            # https://docs.google.com/spreadsheets/d/FILE_ID/edit
            # https://docs.google.com/presentation/d/FILE_ID/edit
            # https://drive.google.com/file/d/FILE_ID/view
            
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split('/')
            
            # Ищем индекс 'd' в пути
            if 'd' in path_parts:
                d_index = path_parts.index('d')
                if d_index + 1 < len(path_parts):
                    file_id = path_parts[d_index + 1]
                    logger.debug(f"Извлечен ID файла: {file_id}")
                    return file_id
            
            logger.warning(f"Не удалось извлечь ID файла из URL: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении ID файла: {e}")
            return None
    
    def get_file_info(self, file_id: str) -> Optional[DriveFile]:
        """
        Получает информацию о файле
        
        Args:
            file_id: ID файла
            
        Returns:
            Информация о файле или None
        """
        try:
            if not self.service:
                logger.error("Drive service не инициализирован")
                return None
            
            # Получаем информацию о файле
            file_info = self.service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,webViewLink,owners'
            ).execute()
            
            # Получаем список разрешений
            permissions_result = self.service.permissions().list(
                fileId=file_id,
                fields='permissions(id,emailAddress,role,type,displayName)'
            ).execute()
            
            permissions = []
            for perm in permissions_result.get('permissions', []):
                permissions.append(DrivePermission(
                    permission_id=perm['id'],
                    email_address=perm.get('emailAddress', ''),
                    role=perm['role'],
                    permission_type=perm['type'],
                    display_name=perm.get('displayName')
                ))
            
            # Получаем email владельца
            owner_email = None
            owners = file_info.get('owners', [])
            if owners:
                owner_email = owners[0].get('emailAddress')
            
            return DriveFile(
                file_id=file_info['id'],
                name=file_info['name'],
                mime_type=file_info['mimeType'],
                web_view_link=file_info['webViewLink'],
                permissions=permissions,
                owner_email=owner_email
            )
            
        except HttpError as e:
            logger.error(f"HTTP ошибка при получении информации о файле: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении информации о файле: {e}")
            return None
    
    def add_permission(self, file_id: str, email: str, role: str = 'reader', 
                      notify: bool = True, message: str = None) -> bool:
        """
        Добавляет разрешение на доступ к файлу
        
        Args:
            file_id: ID файла
            email: Email пользователя
            role: Роль ('reader', 'commenter', 'writer')
            notify: Отправлять ли уведомление
            message: Сообщение для уведомления
            
        Returns:
            True если разрешение добавлено успешно
        """
        try:
            if not self.service:
                logger.error("Drive service не инициализирован")
                return False
            
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            
            # Подготавливаем параметры запроса
            request_params = {
                'fileId': file_id,
                'body': permission,
                'sendNotificationEmail': notify,
                'fields': 'id'
            }
            
            # Добавляем сообщение, если указано
            if notify and message:
                request_params['emailMessage'] = message
            
            result = self.service.permissions().create(**request_params).execute()
            
            logger.info(f"✅ Разрешение добавлено: {email} -> {role} для файла {file_id}")
            return True
            
        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else str(e)
            
            # Проверяем, если ошибка связана с отсутствием Google аккаунта или требованием уведомления
            if ('invalidSharingRequest' in str(error_details) and 
                ('Notify people' in str(error_details) or 'notify' in str(error_details).lower())):
                
                logger.warning(f"⚠️ Email {email} требует отправки уведомления. Попытка добавить с уведомлением...")
                
                # Пробуем ещё раз с обязательным уведомлением
                try:
                    request_params['sendNotificationEmail'] = True
                    if not message:
                        request_params['emailMessage'] = f"Вам предоставлен доступ к документу с ролью '{role}'"
                    else:
                        request_params['emailMessage'] = message
                    
                    result = self.service.permissions().create(**request_params).execute()
                    logger.info(f"✅ Разрешение добавлено с уведомлением: {email} -> {role} для файла {file_id}")
                    return True
                    
                except HttpError as e2:
                    logger.error(f"❌ Повторная попытка не удалась: {e2}")
                    return False
            
            # Специальная обработка для корпоративных доменов
            elif email.endswith('@sputnik8.com') and 'invalidSharingRequest' in str(error_details):
                logger.warning(f"⚠️ Корпоративный email {email}. Попытка с принудительным уведомлением...")
                
                try:
                    request_params['sendNotificationEmail'] = True
                    request_params['emailMessage'] = f"Вам предоставлен доступ к документу с ролью '{role}'"
                    
                    result = self.service.permissions().create(**request_params).execute()
                    logger.info(f"✅ Разрешение добавлено для корпоративного email: {email} -> {role}")
                    return True
                    
                except HttpError as e3:
                    logger.error(f"❌ Не удалось добавить доступ для корпоративного email: {e3}")
                    return False
            
            logger.error(f"❌ HTTP ошибка при добавлении разрешения: {error_details}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении разрешения: {e}")
            return False
    
    def remove_permission(self, file_id: str, permission_id: str) -> bool:
        """
        Удаляет разрешение на доступ к файлу
        
        Args:
            file_id: ID файла
            permission_id: ID разрешения
            
        Returns:
            True если разрешение удалено успешно
        """
        try:
            if not self.service:
                logger.error("Drive service не инициализирован")
                return False
            
            self.service.permissions().delete(
                fileId=file_id,
                permissionId=permission_id
            ).execute()
            
            logger.info(f"✅ Разрешение удалено: {permission_id} для файла {file_id}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ HTTP ошибка при удалении разрешения: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении разрешения: {e}")
            return False
    
    def update_permission(self, file_id: str, permission_id: str, new_role: str) -> bool:
        """
        Обновляет роль в разрешении
        
        Args:
            file_id: ID файла
            permission_id: ID разрешения
            new_role: Новая роль ('reader', 'commenter', 'writer')
            
        Returns:
            True если разрешение обновлено успешно
        """
        try:
            if not self.service:
                logger.error("Drive service не инициализирован")
                return False
            
            permission = {'role': new_role}
            
            self.service.permissions().update(
                fileId=file_id,
                permissionId=permission_id,
                body=permission
            ).execute()
            
            logger.info(f"✅ Разрешение обновлено: {permission_id} -> {new_role} для файла {file_id}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ HTTP ошибка при обновлении разрешения: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении разрешения: {e}")
            return False
    
    def get_permissions(self, file_id: str) -> List[DrivePermission]:
        """
        Получает список всех разрешений для файла
        
        Args:
            file_id: ID файла
            
        Returns:
            Список разрешений
        """
        try:
            if not self.service:
                logger.error("Drive service не инициализирован")
                return []
            
            permissions_result = self.service.permissions().list(
                fileId=file_id,
                fields='permissions(id,emailAddress,role,type,displayName)'
            ).execute()
            
            permissions = []
            for perm in permissions_result.get('permissions', []):
                permissions.append(DrivePermission(
                    permission_id=perm['id'],
                    email_address=perm.get('emailAddress', ''),
                    role=perm['role'],
                    permission_type=perm['type'],
                    display_name=perm.get('displayName')
                ))
            
            return permissions
            
        except HttpError as e:
            logger.error(f"❌ HTTP ошибка при получении разрешений: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка при получении разрешений: {e}")
            return []
