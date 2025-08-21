#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реализация репозиториев для Google API.
"""

from typing import List, Optional
from ..core.domain import User, Group
from .interfaces import IUserRepository, IGroupRepository
from ..core.di_container import service
from ..api.google_api_client import GoogleAPIClient
from ..config.enhanced_config import config
import logging

try:
    from googleapiclient.errors import HttpError
except ImportError:
    HttpError = Exception


@service(singleton=True)
class GoogleUserRepository(IUserRepository):
    """Репозиторий пользователей Google Workspace"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = GoogleAPIClient(config.settings.google_application_credentials)
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Убедиться что клиент инициализирован"""
        if not self._initialized:
            self._initialized = self.client.initialize()
            if not self._initialized:
                self.logger.warning("Google API клиент не инициализирован, используем заглушки")
    
    async def get_all(self) -> List[User]:
        """Получить всех пользователей"""
        await self._ensure_initialized()
        
        # ИСПРАВЛЕНИЕ: Используем тот же подход что и ServiceAdapter - прямой вызов auth.get_service()
        try:
            # Импортируем прямой доступ к Google API
            from ..auth import get_service
            
            self.logger.info("📡 Получение пользователей через прямой Google API...")
            service = get_service()
            
            # Получаем ВСЕХ пользователей с пагинацией (тот же код что в ServiceAdapter)
            all_users = []
            page_token = None
            page_count = 0
            
            while True:
                page_count += 1
                self.logger.info(f"  📄 Загружаем страницу пользователей {page_count}...")
                
                request_params = {
                    'customer': 'my_customer',
                    'maxResults': 500,  # Максимум за один запрос
                    'orderBy': 'email'
                }
                
                if page_token:
                    request_params['pageToken'] = page_token
                
                result = service.users().list(**request_params).execute()
                page_users = result.get('users', [])
                
                if page_users:
                    all_users.extend(page_users)
                    self.logger.info(f"    ↳ Получено {len(page_users)} пользователей на странице {page_count} (всего: {len(all_users)})")
                else:
                    self.logger.info(f"    ⚠️ Страница {page_count} пуста, завершаем загрузку")
                    break
                
                # Проверяем есть ли следующая страница
                page_token = result.get('nextPageToken')
                if not page_token:
                    self.logger.info(f"    🏁 Достигнута последняя страница пользователей")
                    break
                
                # Защита от бесконечного цикла
                if page_count > 50:
                    self.logger.warning(f"    ⚠️ Остановлено после {page_count} страниц")
                    break
            
            # Конвертируем в объекты User
            users: List[User] = []
            for api_user in all_users:
                users.append(
                    User(
                        user_id=api_user.get('id', ''),
                        primary_email=api_user.get('primaryEmail', ''),
                        full_name=api_user.get('name', {}).get('fullName', ''),
                        first_name=api_user.get('name', {}).get('givenName', ''),
                        last_name=api_user.get('name', {}).get('familyName', ''),
                        suspended=api_user.get('suspended', False),
                        org_unit_path=api_user.get('orgUnitPath', '/')
                    )
                )
            
            if users:
                self.logger.info(f"✅ Получено {len(users)} пользователей из прямого Google API")
                return users
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения пользователей через прямой API: {e}")
        
        # Фолбек - демо-данные только если всё провалилось
        self.logger.warning("⚠️ ВНИМАНИЕ: Используются демо-данные! Проверьте настройки Google API")
        
        # Получаем настроенный домен
        configured_domain = self._get_configured_domain()
        
        return [
            User(
                user_id="demo1",
                primary_email=f"demo1@{configured_domain}",
                full_name="Демо Пользователь 1 (ТЕСТ)",
                first_name="Демо",
                last_name="Пользователь 1"
            ),
            User(
                user_id="demo2", 
                primary_email=f"demo2@{configured_domain}",
                full_name="Демо Пользователь 2 (ТЕСТ)",
                first_name="Демо",
                last_name="Пользователь 2"
            )
        ]
    
    def _get_configured_domain(self) -> str:
        """Получить настроенный домен из конфигурации"""
        try:
            from ..config.enhanced_config import config
            domain = config.settings.google_workspace_domain
            if domain and domain != "yourdomain.com":
                return domain
            return "example.com"
        except:
            return "example.com"
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        await self._ensure_initialized()
        
        if not self._initialized:
            demo = await self.get_all()
            for u in demo:
                if u.email.lower() == email.lower():
                    return u
            return None
        
        try:
            api_user = self.client.get_user_by_email(email)
            if not api_user:
                return None
            return User(
                user_id=api_user.get('id', ''),
                primary_email=api_user.get('primaryEmail', ''),
                full_name=api_user.get('name', {}).get('fullName', ''),
                first_name=api_user.get('name', {}).get('givenName', ''),
                last_name=api_user.get('name', {}).get('familyName', ''),
                suspended=api_user.get('suspended', False),
                org_unit_path=api_user.get('orgUnitPath', '/')
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска пользователя {email}: {e}")
            return None
    
    async def create(self, user: User) -> User:
        """Создать пользователя"""
        await self._ensure_initialized()
        self.logger.info(f"Создание пользователя {user.email} (заглушка)")
        # TODO: Реализовать создание через Google API
        return user
    
    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        await self._ensure_initialized()
        self.logger.info(f"Обновление пользователя {user.email} (заглушка)")
        # TODO: Реализовать обновление через Google API
        return user
    
    async def delete(self, email: str) -> bool:
        """Удалить пользователя"""
        await self._ensure_initialized()
        self.logger.info(f"Удаление пользователя {email} (заглушка)")
        # TODO: Реализовать удаление через Google API
        return True
    
    async def search(self, query: str) -> List[User]:
        """Поиск пользователей"""
        await self._ensure_initialized()
        
        # Получаем всех пользователей и фильтруем
        all_users = await self.get_all()
        q = query.lower()
        
        filtered = [u for u in all_users if q in u.email.lower() or q in u.full_name.lower()]
        
        self.logger.info(f"Найдено {len(filtered)} пользователей по запросу '{query}'")
        return filtered
    
    async def get_by_org_unit(self, org_unit_path: str) -> List[User]:
        """Получить пользователей по организационному подразделению"""
        await self._ensure_initialized()
        
        # Получаем всех пользователей и фильтруем по OU
        all_users = await self.get_all()
        filtered = [u for u in all_users if u.org_unit_path == org_unit_path]
        
        self.logger.info(f"Найдено {len(filtered)} пользователей в OU '{org_unit_path}'")
        return filtered


@service(singleton=True)
class GoogleGroupRepository(IGroupRepository):
    """Репозиторий групп Google Workspace"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = GoogleAPIClient(config.settings.google_application_credentials)
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Убедиться что клиент инициализирован"""
        if not self._initialized:
            self._initialized = self.client.initialize()
            if not self._initialized:
                self.logger.warning("Google API клиент не инициализирован, используем заглушки")
    
    async def get_all(self) -> List[Group]:
        """Получить все группы"""
        await self._ensure_initialized()
        
        if not self._initialized:
            self.logger.info("API недоступен, возвращаем пустой список групп")
            return []
        
        try:
            # Получаем все группы через Google API (без ограничений)
            api_groups = self.client.get_groups()
            groups: List[Group] = []
            
            for g in api_groups:
                groups.append(
                    Group(
                        email=g.get('email', ''),
                        name=g.get('name', ''),
                        description=g.get('description', ''),
                        members_count=int(g.get('directMembersCount', 0) or 0)
                    )
                )
            
            self.logger.info(f"Получено {len(groups)} групп из Google API")
            return groups
            
        except Exception as e:
            self.logger.error(f"Ошибка получения групп: {e}")
            return []
    
    async def get_by_email(self, email: str) -> Optional[Group]:
        """Получить группу по email"""
        await self._ensure_initialized()
        
        all_groups = await self.get_all()
        for group in all_groups:
            if group.email.lower() == email.lower():
                return group
        return None
    
    async def create(self, group: Group) -> Group:
        """Создать группу"""
        await self._ensure_initialized()
        self.logger.info(f"Создание группы {group.email} (заглушка)")
        # TODO: Реализовать создание через Google API
        return group
    
    async def update(self, group: Group) -> Group:
        """Обновить группу"""
        await self._ensure_initialized()
        self.logger.info(f"Обновление группы {group.email} (заглушка)")
        # TODO: Реализовать обновление через Google API
        return group
    
    async def delete(self, email: str) -> bool:
        """Удалить группу"""
        await self._ensure_initialized()
        self.logger.info(f"Удаление группы {email} (заглушка)")
        # TODO: Реализовать удаление через Google API
        return True
    
    async def add_member(self, group_email: str, member_email: str) -> bool:
        """Добавить участника в группу"""
        await self._ensure_initialized()
        
        if not self._initialized:
            self.logger.warning("API недоступен, добавление невозможно")
            return False
        
        try:
            return self.client.add_group_member(group_email, member_email)
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления {member_email} в {group_email}: {e}")
            return False
    
    async def remove_member(self, group_email: str, member_email: str) -> bool:
        """Удалить участника из группы"""
        await self._ensure_initialized()
        
        if not self._initialized:
            self.logger.warning("API недоступен, удаление невозможно")
            return False
        
        try:
            return self.client.remove_group_member(group_email, member_email)
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления {member_email} из {group_email}: {e}")
            return False
    
    async def get_members(self, group_email: str) -> List[str]:
        """Получить участников группы"""
        await self._ensure_initialized()
        
        if not self._initialized:
            return []
        
        try:
            members = self.client.get_group_members(group_email)
            return [m.get('email', '') for m in members if m.get('email')]
            
        except Exception as e:
            self.logger.error(f"Ошибка получения участников {group_email}: {e}")
            return []
