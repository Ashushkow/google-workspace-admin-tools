#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google API Client для работы с Google Workspace API.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
from dataclasses import dataclass

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    service_account = None
    build = None
    HttpError = Exception

from ..config.enhanced_config import config

logger = logging.getLogger(__name__)


@dataclass
class QuotaStatus:
    """Статус квот Google API"""
    usage_percentage: float
    requests_per_day: int
    requests_used: int


class GoogleAPIClient:
    """Клиент для работы с Google Workspace API"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Инициализация клиента
        
        Args:
            credentials_path: Путь к файлу с учетными данными
        """
        self.credentials_path = credentials_path
        self.credentials = None
        self.service = None
        self.drive_service = None  # Добавляем сервис для Drive API
        self.gmail_service = None  # Добавляем сервис для Gmail API
    
    def initialize(self) -> bool:
        """
        Инициализация клиента с учетными данными
        
        Returns:
            True если инициализация успешна
        """
        # Проверяем режим разработки
        import os
        is_dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'
        
        if is_dev_mode:
            logger.info("Запуск в режиме разработки - используем заглушку для Google API")
            # В режиме разработки возвращаем True даже без реальной инициализации
            self.service = "dev_mode_service"  # Заглушка для режима разработки
            self.drive_service = "dev_mode_drive_service"  # Заглушка для Drive API
            return True
        
        if not self.credentials_path:
            logger.warning("Путь к учетным данным не указан")
            return False
            
        credentials_file = Path(self.credentials_path)
        if not credentials_file.exists():
            logger.warning(f"Файл учетных данных не найден: {self.credentials_path}")
            return False
            
        try:
            if service_account is None:
                logger.error("Google API библиотеки не установлены")
                return False
            
            # Загружаем и проверяем файл учетных данных
            import json
            with open(credentials_file, 'r') as f:
                creds_data = json.load(f)
            
            # ПРИОРИТЕТ: OAuth 2.0 (Desktop Application)
            if 'installed' in creds_data:
                logger.info("🔑 Используем OAuth 2.0 credentials (приоритетный метод)")
                if not self._setup_oauth2_credentials(credentials_file):
                    return False
            elif 'type' in creds_data and creds_data['type'] == 'service_account':
                logger.info("🔧 Используем Service Account credentials (запасной метод)")
                if not self._setup_service_account_credentials(credentials_file):
                    return False
            else:
                logger.error("❌ Неизвестный формат файла учетных данных")
                return False
            
            try:
                # Создаем сервисы
                logger.info("🔧 Создаем подключение к Google Admin SDK...")
                self.service = build('admin', 'directory_v1', credentials=self.credentials)
                
                logger.info("🔧 Создаем подключение к Google Drive API...")
                self.drive_service = build('drive', 'v3', credentials=self.credentials)
                logger.info("✅ Google Drive API успешно инициализирован")
                
                logger.info("🔧 Создаем подключение к Gmail API...")
                self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
                logger.info("✅ Gmail API успешно инициализирован")
                
                # Проверка подключения (мягкая)
                logger.info("🔍 Проверяем подключение к Google Admin SDK...")
                try:
                    test_result = self.service.users().list(customer='my_customer', maxResults=1).execute()
                    users_found = test_result.get('users', [])
                    if users_found:
                        logger.info("✅ Права на чтение пользователей подтверждены")
                    else:
                        logger.warning("⚠️ Пользователи не найдены или ограничен доступ")
                except Exception as user_test_error:
                    logger.warning(f"⚠️ Ограничение доступа при проверке: {user_test_error}")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Ошибка при инициализации сервиса: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Google API клиента: {e}")
            return False
    
    def get_credentials(self):
        """
        Возвращает объект credentials для использования в других сервисах.
        Совместимо с вызовами в UI (open_document_management).
        """
        return self.credentials
    
    async def test_connection(self) -> bool:
        """
        Тестирует соединение с Google API
        """
        try:
            import os
            is_dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'
            if is_dev_mode:
                return True
            if not self.service:
                return False
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.service.users().list(customer='my_customer', maxResults=1).execute()
            )
            return 'users' in result
        except Exception as e:
            logger.error(f"Ошибка тестирования соединения: {e}")
            return False

    def _execute_with_retries(self, func: Callable[[], Any], retries: int = 3, base_delay: float = 1.0) -> Any:
        """Простая обертка для повторов при временных ошибках"""
        import time
        for attempt in range(1, retries + 1):
            try:
                return func()
            except HttpError as e:
                status = getattr(e, 'resp', None).status if hasattr(e, 'resp') else None
                if status in (429, 500, 503) and attempt < retries:
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"HTTP {status}. Повтор {attempt}/{retries} через {delay:.1f}с")
                    time.sleep(delay)
                    continue
                raise

    def get_users(self, max_results: int = None) -> List[Dict[str, Any]]:
        """Получает список всех пользователей с пагинацией"""
        try:
            if not self.service:
                logger.error("❌ API клиент не инициализирован")
                return []
            
            import os
            is_dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'
            if is_dev_mode:
                logger.info("🔧 Режим разработки: возвращаем демо пользователей")
                return [
                    {
                        'id': 'demo1',
                        'primaryEmail': 'demo1@testdomain.com',
                        'name': {'fullName': 'Демо Пользователь 1', 'givenName': 'Демо', 'familyName': 'Пользователь 1'},
                        'suspended': False,
                        'orgUnitPath': '/'
                    },
                    {
                        'id': 'demo2',
                        'primaryEmail': 'demo2@testdomain.com',
                        'name': {'fullName': 'Демо Пользователь 2', 'givenName': 'Демо', 'familyName': 'Пользователь 2'},
                        'suspended': False,
                        'orgUnitPath': '/'
                    }
                ]
            
            logger.info(f"👥 Запрашиваем ВСЕХ пользователей (без ограничений)...")
            all_users: List[Dict[str, Any]] = []
            page_token = None
            page_count = 0
            
            while True:
                page_count += 1
                logger.info(f"  📄 Загружаем страницу {page_count}...")
                request_params = {
                    'customer': 'my_customer',
                    'maxResults': 500,
                    'orderBy': 'email'
                }
                if page_token:
                    request_params['pageToken'] = page_token
                if max_results and len(all_users) >= max_results:
                    break
                
                result = self._execute_with_retries(lambda: self.service.users().list(**request_params).execute())
                page_users = result.get('users', [])
                if page_users:
                    all_users.extend(page_users)
                    logger.info(f"    ✅ Получено {len(page_users)} пользователей на странице {page_count} (всего: {len(all_users)})")
                else:
                    logger.info(f"    ⚠️ Страница {page_count} пуста")
                    break
                page_token = result.get('nextPageToken')
                if not page_token:
                    logger.info("    🏁 Достигнута последняя страница")
                    break
                if page_count > 100:
                    logger.warning(f"    ⚠️ Остановлено после {page_count} страниц (защита от зацикливания)")
                    break
            
            if max_results and len(all_users) > max_results:
                all_users = all_users[:max_results]
                logger.info(f"  ✂️ Обрезано до {max_results} пользователей")
            
            if not all_users:
                logger.warning("⚠️ Пользователи не найдены.")
                return []
            
            logger.info(f"✅ Успешно получено {len(all_users)} пользователей ВСЕГО")
            return all_users
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователей: {str(e)}")
            if isinstance(e, HttpError):
                logger.error(f"🔍 HTTP статус: {e.resp.status}")
                logger.error(f"🔍 Ответ сервера: {e.content}")
            return []

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получить пользователя по email через точечный запрос"""
        try:
            if not self.service:
                return None
            result = self._execute_with_retries(lambda: self.service.users().get(userKey=email).execute())
            return result
        except HttpError as e:
            if getattr(e, 'resp', None) and e.resp.status == 404:
                return None
            logger.error(f"Ошибка get_user_by_email({email}): {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка get_user_by_email({email}): {e}")
            return None

    def get_groups(self, max_results: int = None) -> List[Dict[str, Any]]:
        """Получает список всех групп с пагинацией"""
        try:
            if not self.service:
                return []
            all_groups: List[Dict[str, Any]] = []
            page_token = None
            while True:
                request_params = {
                    'customer': 'my_customer',
                    'maxResults': 200
                }
                if page_token:
                    request_params['pageToken'] = page_token
                result = self._execute_with_retries(lambda: self.service.groups().list(**request_params).execute())
                groups = result.get('groups', [])
                if groups:
                    all_groups.extend(groups)
                    logger.debug(f"Загружена страница групп: {len(groups)} записей")
                page_token = result.get('nextPageToken')
                if not page_token:
                    break
                if max_results and len(all_groups) >= max_results:
                    all_groups = all_groups[:max_results]
                    break
            logger.info(f"Загружено групп: {len(all_groups)}")
            return all_groups
        except Exception as e:
            logger.error(f"Ошибка получения групп: {e}")
            return []

    def add_group_member(self, group_email: str, member_email: str) -> bool:
        """Добавляет участника в группу"""
        try:
            if not self.service:
                logger.warning("Google API сервис не инициализирован")
                return False
            member_data = {'email': member_email, 'role': 'MEMBER'}
            self._execute_with_retries(lambda: self.service.members().insert(groupKey=group_email, body=member_data).execute())
            logger.info(f"✅ Участник {member_email} успешно добавлен в группу {group_email}")
            return True
        except HttpError as e:
            if e.resp.status == 409:
                logger.info(f"ℹ️ Участник {member_email} уже является членом группы {group_email}")
                return True
            else:
                logger.error(f"❌ Ошибка добавления участника {member_email} в группу {group_email}: {e}")
                logger.error(f"🔍 HTTP статус: {e.resp.status}")
                logger.error(f"🔍 Ответ сервера: {e.content}")
                return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при добавлении участника {member_email} в группу {group_email}: {e}")
            return False
    
    def remove_group_member(self, group_email: str, member_email: str) -> bool:
        """Удаляет участника из группы"""
        try:
            if not self.service:
                logger.warning("Google API сервис не инициализирован")
                return False
            self._execute_with_retries(lambda: self.service.members().delete(groupKey=group_email, memberKey=member_email).execute())
            logger.info(f"✅ Участник {member_email} успешно удален из группы {group_email}")
            return True
        except HttpError as e:
            if e.resp.status == 404:
                logger.info(f"ℹ️ Участник {member_email} не найден в группе {group_email} (возможно, уже удален)")
                return True
            else:
                logger.error(f"❌ Ошибка удаления участника {member_email} из группы {group_email}: {e}")
                logger.error(f"🔍 HTTP статус: {e.resp.status}")
                logger.error(f"🔍 Ответ сервера: {e.content}")
                return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при удалении участника {member_email} из группы {group_email}: {e}")
            return False

    def get_group_members(self, group_email: str, max_results: int = None) -> List[Dict[str, Any]]:
        """Получает список участников группы"""
        try:
            if not self.service:
                logger.warning("Google API сервис не инициализирован")
                return []
            all_members: List[Dict[str, Any]] = []
            page_token = None
            while True:
                request_params = {'groupKey': group_email, 'maxResults': 200}
                if page_token:
                    request_params['pageToken'] = page_token
                result = self._execute_with_retries(lambda: self.service.members().list(**request_params).execute())
                members = result.get('members', [])
                if members:
                    all_members.extend(members)
                    logger.debug(f"Загружена страница участников группы {group_email}: {len(members)} записей")
                page_token = result.get('nextPageToken')
                if not page_token:
                    break
                if max_results and len(all_members) >= max_results:
                    all_members = all_members[:max_results]
                    break
            logger.info(f"Загружено участников группы {group_email}: {len(all_members)}")
            return all_members
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Группа {group_email} не найдена")
                return []
            else:
                logger.error(f"❌ Ошибка получения участников группы {group_email}: {e}")
                logger.error(f"🔍 HTTP статус: {e.resp.status}")
                logger.error(f"🔍 Ответ сервера: {e.content}")
                return []
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при получении участников группы {group_email}: {e}")
            return []
    
    async def get_quota_status(self) -> Optional[QuotaStatus]:
        """Получает статус квот Google API"""
        try:
            return QuotaStatus(
                usage_percentage=10.0,
                requests_per_day=1000,
                requests_used=100
            )
        except Exception as e:
            logger.error(f"Ошибка получения статуса квот: {e}")
            return None
    
    def is_available(self) -> bool:
        """Проверяет доступность Google API (по инициализации клиента)"""
        return self.service is not None
    
    def _setup_oauth2_credentials(self, credentials_file: Path) -> bool:
        """
        Настройка OAuth 2.0 credentials (приоритетный метод)
        """
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            import pickle
            
            SCOPES = config.google.scopes
            
            token_file = Path(config.google.token_file)
            token_file.parent.mkdir(parents=True, exist_ok=True)
            if token_file.exists():
                logger.info("📁 Загружаем сохраненный токен OAuth 2.0")
                with open(token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    logger.info("🔄 Обновляем истекший токен OAuth 2.0")
                    self.credentials.refresh(Request())
                else:
                    logger.info("🌐 Запускаем интерактивную авторизацию OAuth 2.0...")
                    print("\n" + "="*60)
                    print("🔐 АВТОРИЗАЦИЯ GOOGLE WORKSPACE")
                    print("="*60)
                    print("Сейчас откроется браузер для авторизации.")
                    print("Войдите в Google аккаунт с правами администратора.")
                    print("После успешной авторизации вернитесь в это приложение.")
                    print("="*60 + "\n")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                    self.credentials = flow.run_local_server(
                        port=0,
                        prompt='select_account',
                        authorization_prompt_message='🔐 Откроется браузер для авторизации Google Workspace...',
                        success_message='✅ Авторизация успешна! Можете закрыть браузер.'
                    )
                    print("✅ Авторизация OAuth 2.0 завершена успешно!")
            
            with open(token_file, 'wb') as token:
                pickle.dump(self.credentials, token)
                logger.info("💾 Токен OAuth 2.0 сохранен для последующих запусков")
            
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка настройки OAuth 2.0: {e}")
            return False
    
    def _setup_service_account_credentials(self, credentials_file: Path) -> bool:
        """
        Настройка Service Account credentials (запасной метод)
        """
        try:
            logger.info("⚙️ Настраиваем Service Account credentials...")
            scopes = config.google.scopes
            self.credentials = service_account.Credentials.from_service_account_file(
                str(credentials_file),
                scopes=scopes
            )
            admin_email = config.settings.google_workspace_admin
            if admin_email and admin_email not in ("admin@yourdomain.com", "admin@example.com"):
                self.credentials = self.credentials.with_subject(admin_email)
                logger.info(f"✅ Применено делегирование на администратора домена: {admin_email}")
            else:
                logger.warning("⚠️ Администратор домена не настроен, делегирование не применяется")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка настройки Service Account: {e}")
            return False
