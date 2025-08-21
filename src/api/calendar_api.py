#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Calendar API для управления календарями и их участниками.
Поддерживает OAuth 2.0 и Service Account авторизацию.
"""

import logging
import os
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
except ImportError as e:
    logging.warning(f"Google API библиотеки не установлены: {e}")
    build = None
    HttpError = Exception

# Пути проекта
from ..utils.file_paths import get_config_path

logger = logging.getLogger(__name__)


@dataclass
class CalendarInfo:
    """Информация о календаре"""
    id: str
    name: str
    description: str = ""
    owner: str = ""
    access_role: str = ""
    primary: bool = False


@dataclass
class CalendarPermission:
    """Права доступа к календарю"""
    user_email: str
    role: str  # owner, reader, writer, freeBusyReader
    scope_type: str = "user"  # user, group, domain, default


class GoogleCalendarAPI:
    """API для работы с Google Calendar"""
    
    # Области доступа для Calendar API
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.acls',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self, credentials_path: str = "credentials.json"):
        """
        Инициализация Calendar API
        
        Args:
            credentials_path: Путь к файлу с учетными данными
        """
        # Разрешаем путь к credentials: ENV -> config/ -> переданный -> локальный
        self.credentials_path = self._resolve_credentials_path(credentials_path)
        self.service = None
        self.credentials = None
        # Храним токен в конфиге, чтобы не плодить файлы в корне
        self._token_path = str(get_config_path('token.pickle'))

    @staticmethod
    def _resolve_credentials_path(initial_path: Optional[str]) -> str:
        """Определяет фактический путь к credentials.json.
        Порядок:
        1) ENV GOOGLE_CREDENTIALS_PATH или GOOGLE_APPLICATION_CREDENTIALS
        2) config/credentials.json
        3) Переданный путь, если существует
        4) ./credentials.json (текущая директория)
        """
        # 1) Переменные окружения
        for env_key in ("GOOGLE_CREDENTIALS_PATH", "GOOGLE_APPLICATION_CREDENTIALS"):
            env_path = os.environ.get(env_key)
            if env_path and os.path.exists(env_path):
                return env_path
        
        # 2) Файл в конфигурации проекта
        cfg_path = get_config_path('credentials.json')
        try:
            if cfg_path.exists():
                return str(cfg_path)
        except Exception:
            pass
        
        # 3) Переданный путь
        if initial_path and os.path.exists(initial_path):
            return initial_path
        
        # 4) Файл в рабочей директории
        if os.path.exists('credentials.json'):
            return 'credentials.json'
        
        # Возвращаем как есть (дальше authenticate() сообщит об ошибке)
        return initial_path or 'credentials.json'
        
    def authenticate(self) -> bool:
        """
        Аутентификация с приоритетом OAuth 2.0
        
        Returns:
            True если аутентификация успешна
        """
        try:
            # Проверяем существование файла учетных данных
            if not os.path.exists(self.credentials_path):
                logger.error(
                    "Файл учетных данных не найден: %s.\n"
                    "Ожидались пути: %s\n"
                    "Подсказка: поместите credentials.json в папку config/ или укажите переменную окружения "
                    "GOOGLE_CREDENTIALS_PATH/GOOGLE_APPLICATION_CREDENTIALS.",
                    self.credentials_path,
                    ", ".join([
                        str(get_config_path('credentials.json')),
                        os.path.abspath('credentials.json')
                    ])
                )
                return False
            
            # Определяем тип учетных данных
            import json
            with open(self.credentials_path, 'r', encoding='utf-8') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data:
                # OAuth 2.0 credentials (приоритетный метод)
                logger.info("🔑 Используем OAuth 2.0 аутентификацию для Calendar API")
                return self._oauth2_authenticate()
            elif 'type' in creds_data and creds_data['type'] == 'service_account':
                # Service Account credentials (запасной метод)
                logger.info("🔧 Используем Service Account аутентификацию для Calendar API")
                return self._service_account_authenticate()
            else:
                logger.error("❌ Неизвестный формат файла учетных данных")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка аутентификации: {e}")
            return False
    
    def _oauth2_authenticate(self) -> bool:
        """OAuth 2.0 аутентификация"""
        try:
            creds = None
            token_path = self._token_path
            
            # Загружаем существующий токен
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # Если токен недействителен, получаем новый
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Сохраняем токен для следующих запусков
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.credentials = creds
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("✅ OAuth 2.0 аутентификация успешна")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка OAuth 2.0 аутентификации: {e}")
            return False
    
    def _service_account_authenticate(self) -> bool:
        """Service Account аутентификация"""
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES
            )
            self.credentials = creds
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("✅ Service Account аутентификация успешна")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка Service Account аутентификации: {e}")
            return False
    
    def get_calendar_list(self) -> List[CalendarInfo]:
        """
        Получение списка календарей пользователя
        
        Returns:
            Список календарей
        """
        if not self.service:
            logger.error("Сервис не инициализирован")
            return []
        
        try:
            calendars = []
            page_token = None
            
            while True:
                calendar_list = self.service.calendarList().list(
                    pageToken=page_token
                ).execute()
                
                for calendar_item in calendar_list.get('items', []):
                    calendar_info = CalendarInfo(
                        id=calendar_item['id'],
                        name=calendar_item.get('summary', 'Без названия'),
                        description=calendar_item.get('description', ''),
                        owner=calendar_item.get('owner', {}).get('email', ''),
                        access_role=calendar_item.get('accessRole', ''),
                        primary=calendar_item.get('primary', False)
                    )
                    calendars.append(calendar_info)
                
                page_token = calendar_list.get('nextPageToken')
                if not page_token:
                    break
            
            logger.info(f"Найдено календарей: {len(calendars)}")
            return calendars
            
        except HttpError as e:
            logger.error(f"Ошибка получения списка календарей: {e}")
            return []
    
    def get_calendar_by_id(self, calendar_id: str) -> Optional[CalendarInfo]:
        """
        Получение информации о календаре по ID
        
        Args:
            calendar_id: ID календаря
            
        Returns:
            Информация о календаре или None
        """
        if not self.service:
            logger.error("Сервис не инициализирован")
            return None
        
        try:
            calendar = self.service.calendars().get(calendarId=calendar_id).execute()
            
            calendar_info = CalendarInfo(
                id=calendar['id'],
                name=calendar.get('summary', 'Без названия'),
                description=calendar.get('description', ''),
                owner=calendar.get('owner', {}).get('email', ''),
                access_role='owner'  # Если можем получить календарь, то имеем доступ
            )
            
            return calendar_info
            
        except HttpError as e:
            logger.error(f"Ошибка получения календаря {calendar_id}: {e}")
            return None
    
    def get_calendar_permissions(self, calendar_id: str) -> List[CalendarPermission]:
        """
        Получение списка разрешений для календаря с пагинацией
        
        Args:
            calendar_id: ID календаря
            
        Returns:
            Список разрешений
        """
        if not self.service:
            logger.error("Сервис не инициализирован")
            return []
        
        try:
            permissions = []
            next_page_token = None
            
            while True:
                # Запрос с пагинацией
                if next_page_token:
                    acl_list = self.service.acl().list(
                        calendarId=calendar_id,
                        pageToken=next_page_token
                    ).execute()
                else:
                    acl_list = self.service.acl().list(calendarId=calendar_id).execute()
                
                # Обрабатываем элементы текущей страницы
                for acl_item in acl_list.get('items', []):
                    scope = acl_item.get('scope', {})
                    
                    # Пропускаем системные разрешения
                    if scope.get('type') == 'default':
                        continue
                    
                    permission = CalendarPermission(
                        user_email=scope.get('value', ''),
                        role=acl_item.get('role', ''),
                        scope_type=scope.get('type', 'user')
                    )
                    permissions.append(permission)
                
                # Проверяем, есть ли следующая страница
                next_page_token = acl_list.get('nextPageToken')
                if not next_page_token:
                    break
            
            logger.info(f"Найдено разрешений для календаря {calendar_id}: {len(permissions)}")
            return permissions
            
        except HttpError as e:
            logger.error(f"Ошибка получения разрешений календаря {calendar_id}: {e}")
            return []
            return []
    
    def add_user_to_calendar(self, calendar_id: str, user_email: str, role: str = 'reader') -> bool:
        """
        Добавление пользователя к календарю
        
        Args:
            calendar_id: ID календаря
            user_email: Email пользователя
            role: Роль доступа (owner, reader, writer, freeBusyReader)
            
        Returns:
            True если пользователь добавлен успешно
        """
        if not self.service:
            logger.error("Сервис не инициализирован")
            return False
        
        try:
            acl_rule = {
                'scope': {
                    'type': 'user',
                    'value': user_email
                },
                'role': role
            }
            
            self.service.acl().insert(
                calendarId=calendar_id,
                body=acl_rule
            ).execute()
            
            logger.info(f"✅ Пользователь {user_email} добавлен к календарю {calendar_id} с ролью {role}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Ошибка добавления пользователя {user_email} к календарю {calendar_id}: {e}")
            return False
    
    def remove_user_from_calendar(self, calendar_id: str, user_email: str) -> bool:
        """
        Удаление пользователя из календаря с поддержкой пагинации
        
        Args:
            calendar_id: ID календаря
            user_email: Email пользователя
            
        Returns:
            True если пользователь удален успешно
        """
        if not self.service:
            logger.error("Сервис не инициализирован")
            return False
        
        try:
            # Ищем ACL ID для пользователя с пагинацией
            acl_id = None
            next_page_token = None
            
            while True:
                # Запрос с пагинацией
                if next_page_token:
                    acl_list = self.service.acl().list(
                        calendarId=calendar_id,
                        pageToken=next_page_token
                    ).execute()
                else:
                    acl_list = self.service.acl().list(calendarId=calendar_id).execute()
                
                # Ищем пользователя на текущей странице
                for acl_item in acl_list.get('items', []):
                    scope = acl_item.get('scope', {})
                    if (scope.get('value', '').lower() == user_email.lower() and 
                        scope.get('type') == 'user'):
                        acl_id = acl_item.get('id')
                        break
                
                # Если нашли пользователя, выходим
                if acl_id:
                    break
                
                # Проверяем, есть ли следующая страница
                next_page_token = acl_list.get('nextPageToken')
                if not next_page_token:
                    break
            
            if not acl_id:
                logger.warning(f"Пользователь {user_email} не найден в календаре {calendar_id}")
                return False
            
            # Удаляем разрешение
            self.service.acl().delete(
                calendarId=calendar_id,
                ruleId=acl_id
            ).execute()
            
            logger.info(f"✅ Пользователь {user_email} удален из календаря {calendar_id}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Ошибка удаления пользователя {user_email} из календаря {calendar_id}: {e}")
            return False
    
    def update_user_role(self, calendar_id: str, user_email: str, new_role: str) -> bool:
        """
        Обновление роли пользователя в календаре
        
        Args:
            calendar_id: ID календаря
            user_email: Email пользователя
            new_role: Новая роль (owner, reader, writer, freeBusyReader)
            
        Returns:
            True если роль обновлена успешно
        """
        if not self.service:
            logger.error("Сервис не инициализирован")
            return False
        
        try:
            # Сначала находим ACL ID для пользователя
            acl_list = self.service.acl().list(calendarId=calendar_id).execute()
            
            acl_id = None
            for acl_item in acl_list.get('items', []):
                scope = acl_item.get('scope', {})
                if scope.get('value') == user_email and scope.get('type') == 'user':
                    acl_id = acl_item.get('id')
                    break
            
            if not acl_id:
                logger.warning(f"Пользователь {user_email} не найден в календаре {calendar_id}")
                return False
            
            # Обновляем роль
            acl_rule = {
                'scope': {
                    'type': 'user',
                    'value': user_email
                },
                'role': new_role
            }
            
            self.service.acl().update(
                calendarId=calendar_id,
                ruleId=acl_id,
                body=acl_rule
            ).execute()
            
            logger.info(f"✅ Роль пользователя {user_email} в календаре {calendar_id} обновлена на {new_role}")
            return True
            
        except HttpError as e:
            logger.error(f"❌ Ошибка обновления роли пользователя {user_email} в календаре {calendar_id}: {e}")
            return False
    
    def find_calendar_by_name(self, calendar_name: str) -> Optional[CalendarInfo]:
        """
        Поиск календаря по названию
        
        Args:
            calendar_name: Название календаря для поиска
            
        Returns:
            Информация о найденном календаре или None
        """
        calendars = self.get_calendar_list()
        
        for calendar in calendars:
            if calendar.name.lower() == calendar_name.lower():
                return calendar
        
        return None
    
    @staticmethod
    def extract_calendar_id_from_url(calendar_url: str) -> Optional[str]:
        """
        Извлечение ID календаря из URL
        
        Args:
            calendar_url: URL календаря Google
            
        Returns:
            ID календаря или None
        """
        try:
            # Пример URL: https://calendar.google.com/calendar/u/0?cid=dGNvNXZpcWxjNnZ0MjBsYmtsaDAzdTJrYjhAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ
            if 'cid=' in calendar_url:
                import urllib.parse
                parsed_url = urllib.parse.urlparse(calendar_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                if 'cid' in query_params:
                    cid = query_params['cid'][0]
                    # Декодируем base64url
                    import base64
                    decoded_id = base64.urlsafe_b64decode(cid + '==').decode('utf-8')
                    return decoded_id
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка извлечения ID календаря из URL: {e}")
            return None


def create_calendar_api(credentials_path: str = "credentials.json") -> Optional[GoogleCalendarAPI]:
    """
    Создание и инициализация Calendar API
    
    Args:
        credentials_path: Путь к файлу учетных данных
        
    Returns:
        Инициализированный API или None при ошибке
    """
    try:
        api = GoogleCalendarAPI(credentials_path)
        
        if api.authenticate():
            return api
        else:
            logger.error("Не удалось аутентифицироваться в Calendar API")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка создания Calendar API: {e}")
        return None
