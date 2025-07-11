#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google API Client для работы с Google Workspace API.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
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
            # Проверяем тип учетных данных и отдаем приоритет OAuth 2.0
            if 'installed' in creds_data:
                # OAuth2 credentials - ПРИОРИТЕТНЫЙ метод
                logger.info("🔑 Используем OAuth 2.0 credentials (приоритетный метод)")
                if not self._setup_oauth2_credentials(credentials_file):
                    return False
            elif 'type' in creds_data and creds_data['type'] == 'service_account':
                # Service Account credentials - запасной метод
                logger.info("🔧 Используем Service Account credentials (запасной метод)")
                if not self._setup_service_account_credentials(credentials_file):
                    return False
            else:
                logger.error("❌ Неизвестный формат файла учетных данных")
                return False
            
            try:
                # Создаем сервис Google Admin SDK
                logger.info("🔧 Создаем подключение к Google Admin SDK...")
                self.service = build('admin', 'directory_v1', credentials=self.credentials)
                
                # Проверяем подключение и права доступа (опционально)
                logger.info("🔍 Проверяем подключение к Google Admin SDK...")
                try:
                    # Сначала пробуем получить домены (требует больше прав)
                    test_result = self.service.domains().list(customer='my_customer').execute()
                    domains = test_result.get('domains', [])
                    
                    logger.info(f"✅ Google API клиент успешно инициализирован!")
                    if domains:
                        logger.info(f"📊 Подключен к {len(domains)} домену(ам): {[d['domainName'] for d in domains]}")
                    else:
                        logger.warning("⚠️ Домены не найдены. Проверьте права доступа в Google Workspace.")
                        
                except Exception as domain_error:
                    logger.warning(f"⚠️ Ограниченный доступ к доменам: {domain_error}")
                    logger.info("Продолжаем с ограниченными правами...")
                
                try:
                    logger.info("🔍 Проверяем права на чтение пользователей...")
                    test_users = self.service.users().list(customer='my_customer', maxResults=1).execute()
                    users_found = test_users.get('users', [])
                    if users_found:
                        logger.info(f"✅ Права на чтение пользователей подтверждены, найден {len(users_found)} пользователь(ей)")
                    else:
                        logger.warning("⚠️ Пользователи не найдены. Возможные причины:")
                        logger.warning("  • В домене нет пользователей")
                        logger.warning("  • Недостаточно прав доступа")
                        logger.warning("  • OAuth consent screen не настроен")
                        logger.warning("  • Требуется верификация приложения в Google")
                except Exception as user_test_error:
                    logger.error(f"❌ Ошибка проверки прав на пользователей: {user_test_error}")
                    if "insufficient permissions" in str(user_test_error).lower():
                        logger.error("🔒 Недостаточно прав доступа. Проверьте:")
                        logger.error("  • OAuth consent screen настроен и опубликован")
                        logger.error("  • Добавлены необходимые scopes")
                        logger.error("  • Аккаунт имеет права администратора")
                    elif "domain verification" in str(user_test_error).lower():
                        logger.error("🔐 Требуется верификация домена в Google Cloud Console")
                    return False
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Ошибка при инициализации сервиса: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Google API клиента: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Тестирует соединение с Google API
        
        Returns:
            True если соединение работает
        """
        try:
            # Проверяем режим разработки
            import os
            is_dev_mode = os.getenv('DEV_MODE', 'False').lower() == 'true'
            
            if is_dev_mode:
                logger.debug("Тест соединения в режиме разработки - возвращаем True")
                return True
            
            if not self.service:
                return False
                
            # Выполняем в отдельном потоке, чтобы не блокировать event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.service.domains().list(customer='my_customer').execute()
            )
            
            logger.debug(f"Тест соединения успешен: {len(result.get('domains', []))} доменов")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка тестирования соединения: {e}")
            return False
    
    def get_users(self, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Получает список всех пользователей с пагинацией
        
        Args:
            max_results: Максимальное количество результатов (None = все)
            
        Returns:
            Список всех пользователей
        """
        try:
            if not self.service:
                logger.error("❌ API клиент не инициализирован")
                return []
            
            # Добавляем режим разработки
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
            
            all_users = []
            page_token = None
            page_count = 0
            
            while True:
                page_count += 1
                logger.info(f"  📄 Загружаем страницу {page_count}...")
                
                # Параметры запроса
                request_params = {
                    'customer': 'my_customer',
                    'maxResults': 500,  # Максимум за один запрос в Google API
                    'orderBy': 'email'
                }
                
                if page_token:
                    request_params['pageToken'] = page_token
                
                # Если задан лимит и мы уже его достигли
                if max_results and len(all_users) >= max_results:
                    break
                
                result = self.service.users().list(**request_params).execute()
                page_users = result.get('users', [])
                
                if page_users:
                    all_users.extend(page_users)
                    logger.info(f"    ✅ Получено {len(page_users)} пользователей на странице {page_count} (всего: {len(all_users)})")
                else:
                    logger.info(f"    ⚠️ Страница {page_count} пуста")
                    break
                
                # Проверяем есть ли следующая страница
                page_token = result.get('nextPageToken')
                if not page_token:
                    logger.info(f"    🏁 Достигнута последняя страница")
                    break
                
                # Защита от бесконечного цикла
                if page_count > 100:
                    logger.warning(f"    ⚠️ Остановлено после {page_count} страниц (защита от зацикливания)")
                    break
            
            # Применяем лимит если задан
            if max_results and len(all_users) > max_results:
                all_users = all_users[:max_results]
                logger.info(f"  ✂️ Обрезано до {max_results} пользователей")
            
            if not all_users:
                logger.warning("⚠️ Пользователи не найдены. Проверьте:")
                logger.warning("1. Права доступа аккаунта администратора")
                logger.warning("2. Наличие пользователей в домене")
                logger.warning("3. Настройки OAuth consent screen")
                logger.warning("4. Статус верификации приложения в Google")
                return []
            
            logger.info(f"✅ Успешно получено {len(all_users)} пользователей ВСЕГО")
            return all_users
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователей: {str(e)}")
            if isinstance(e, HttpError):
                logger.error(f"🔍 HTTP статус: {e.resp.status}")
                logger.error(f"🔍 Ответ сервера: {e.content}")
            return []
    
    def get_groups(self, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Получает список всех групп с пагинацией
        
        Args:
            max_results: Максимальное количество результатов (None = все)
            
        Returns:
            Список групп
        """
        try:
            if not self.service:
                return []
            
            all_groups = []
            page_token = None
            
            while True:
                request_params = {
                    'customer': 'my_customer',
                    'maxResults': 200  # Используем максимальный размер страницы
                }
                
                if page_token:
                    request_params['pageToken'] = page_token
                
                result = self.service.groups().list(**request_params).execute()
                groups = result.get('groups', [])
                
                if groups:
                    all_groups.extend(groups)
                    logger.debug(f"Загружена страница групп: {len(groups)} записей")
                
                # Проверяем наличие следующей страницы
                page_token = result.get('nextPageToken')
                if not page_token:
                    break
                    
                # Если задано ограничение и мы его достигли
                if max_results and len(all_groups) >= max_results:
                    all_groups = all_groups[:max_results]
                    break
            
            logger.info(f"Загружено групп: {len(all_groups)}")
            return all_groups
            
        except Exception as e:
            logger.error(f"Ошибка получения групп: {e}")
            return []
    
    async def get_quota_status(self) -> Optional[QuotaStatus]:
        """
        Получает статус квот Google API
        
        Returns:
            Информация о квотах или None
        """
        try:
            # В реальном приложении здесь был бы запрос к API квот
            # Для демонстрации возвращаем заглушку
            return QuotaStatus(
                usage_percentage=10.0,  # Процент использования квоты
                requests_per_day=1000,
                requests_used=100
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса квот: {e}")
            return None
    
    def is_available(self) -> bool:
        """Проверяет доступность Google API"""
        return self.service is not None and self.test_connection()
    
    def _setup_oauth2_credentials(self, credentials_file: Path) -> bool:
        """
        Настройка OAuth 2.0 credentials (приоритетный метод)
        
        Args:
            credentials_file: Путь к файлу OAuth 2.0 credentials
            
        Returns:
            True если настройка успешна
        """
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            import pickle
            
            # Определяем необходимые scopes для Google Workspace Admin
            SCOPES = [
                'https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group',
                'https://www.googleapis.com/auth/admin.directory.orgunit',
                'https://www.googleapis.com/auth/calendar',
            ]
            
            # Проверяем существующий токен
            token_file = Path('token.pickle')
            if token_file.exists():
                logger.info("📁 Загружаем сохраненный токен OAuth 2.0")
                with open(token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # Если нет валидных учетных данных, запускаем поток авторизации
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
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, SCOPES)
                    # Запускаем локальный сервер для получения авторизации
                    self.credentials = flow.run_local_server(
                        port=0,
                        prompt='select_account',
                        authorization_prompt_message='🔐 Откроется браузер для авторизации Google Workspace...',
                        success_message='✅ Авторизация успешна! Можете закрыть браузер.'
                    )
                    print("✅ Авторизация OAuth 2.0 завершена успешно!")
                    
            # Сохраняем токен для последующих запусков
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
        
        Args:
            credentials_file: Путь к файлу Service Account credentials
            
        Returns:
            True если настройка успешна
        """
        try:
            logger.info("⚙️ Настраиваем Service Account credentials...")
            self.credentials = service_account.Credentials.from_service_account_file(
                str(credentials_file),
                scopes=[
                    'https://www.googleapis.com/auth/admin.directory.user',
                    'https://www.googleapis.com/auth/admin.directory.group',
                    'https://www.googleapis.com/auth/admin.directory.orgunit',
                    'https://www.googleapis.com/auth/calendar',
                ]
            )
            logger.info("✅ Service Account credentials настроены успешно")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки Service Account: {e}")
            return False
