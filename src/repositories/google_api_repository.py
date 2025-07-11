#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реализация репозиториев для Google API.
"""

from typing import List, Optional, Dict, Any
from ..core.domain import User, Group, OrganizationalUnit
from .interfaces import IUserRepository, IGroupRepository, IOrgUnitRepository
from ..core.di_container import service
from ..api.google_api_client import GoogleAPIClient
from ..config.enhanced_config import config
import logging


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
        
        # Временное решение: всегда пытаемся получить реальных пользователей
        try:
            # Получаем ВСЕХ пользователей через Google API (без ограничений)
            api_users = self.client.get_users()  # Убрано ограничение max_results=100
            users = []
            
            for api_user in api_users:
                user = User(
                    user_id=api_user.get('id', ''),
                    primary_email=api_user.get('primaryEmail', ''),
                    full_name=api_user.get('name', {}).get('fullName', ''),
                    first_name=api_user.get('name', {}).get('givenName', ''),
                    last_name=api_user.get('name', {}).get('familyName', ''),
                    suspended=api_user.get('suspended', False),
                    org_unit_path=api_user.get('orgUnitPath', '/')
                )
                users.append(user)
            
            if users:
                self.logger.info(f"Получено {len(users)} реальных пользователей из Google API")
                return users
            else:
                self.logger.warning("Реальные пользователи не найдены, используем демо-данные")
                
        except Exception as e:
            self.logger.error(f"Ошибка получения реальных пользователей: {e}")
        
        # Если не удалось получить реальных пользователей, возвращаем демо-данные
        if not self._initialized:
            # Возвращаем демо-данные если API недоступен
            self.logger.info("API недоступен, возвращаем демо пользователей")
            return [
                User(
                    user_id="demo1",
                    primary_email="demo1@example.com",
                    full_name="Демо Пользователь 1",
                    first_name="Демо",
                    last_name="Пользователь 1"
                ),
                User(
                    user_id="demo2", 
                    primary_email="demo2@example.com",
                    full_name="Демо Пользователь 2",
                    first_name="Демо",
                    last_name="Пользователь 2"
                )
            ]
        
        return []
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        await self._ensure_initialized()
        
        if not self._initialized:
            self.logger.info(f"API недоступен, поиск пользователя {email} в демо данных")
            # Поиск в демо данных
            demo_users = await self.get_all()
            for user in demo_users:
                if user.email == email:
                    return user
            return None
        
        try:
            # Поиск через Google API
            api_users = self.client.get_users(max_results=1)
            for api_user in api_users:
                if api_user.get('primaryEmail', '').lower() == email.lower():
                    return User(
                        user_id=api_user.get('id', ''),
                        primary_email=api_user.get('primaryEmail', ''),
                        full_name=api_user.get('name', {}).get('fullName', ''),
                        first_name=api_user.get('name', {}).get('givenName', ''),
                        last_name=api_user.get('name', {}).get('familyName', ''),
                        suspended=api_user.get('suspended', False),
                        org_unit_path=api_user.get('orgUnitPath', '/')
                    )
            return None
            
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
        query_lower = query.lower()
        
        filtered_users = [
            user for user in all_users
            if query_lower in user.email.lower() or query_lower in user.full_name.lower()
        ]
        
        self.logger.info(f"Найдено {len(filtered_users)} пользователей по запросу '{query}'")
        return filtered_users
    
    async def get_by_org_unit(self, org_unit_path: str) -> List[User]:
        """Получить пользователей по организационному подразделению"""
        await self._ensure_initialized()
        
        # Получаем всех пользователей и фильтруем по OU
        all_users = await self.get_all()
        
        filtered_users = [
            user for user in all_users
            if user.org_unit_path == org_unit_path
        ]
        
        self.logger.info(f"Найдено {len(filtered_users)} пользователей в OU '{org_unit_path}'")
        return filtered_users


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
            # Возвращаем демо-данные если API недоступен
            self.logger.info("API недоступен, возвращаем демо группы")
            return [
                Group(
                    id="demo-group1",
                    email="group1@example.com",
                    name="Демо Группа 1",
                    description="Первая демонстрационная группа"
                ),
                Group(
                    id="demo-group2",
                    email="group2@example.com", 
                    name="Демо Группа 2",
                    description="Вторая демонстрационная группа"
                )
            ]
        
        try:
            # Получаем все группы через Google API (без ограничений)
            api_groups = self.client.get_groups()
            groups = []
            
            for api_group in api_groups:
                group = Group(
                    id=api_group.get('id', ''),
                    email=api_group.get('email', ''),
                    name=api_group.get('name', ''),
                    description=api_group.get('description', ''),
                    members_count=int(api_group.get('directMembersCount', 0))
                )
                groups.append(group)
            
            self.logger.info(f"Получено {len(groups)} групп из Google API")
            return groups
            
        except Exception as e:
            self.logger.error(f"Ошибка получения групп: {e}")
            return []
    
    async def get_by_email(self, email: str) -> Optional[Group]:
        """Получить группу по email"""
        await self._ensure_initialized()
        
        # Поиск среди всех групп
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
    
    async def get_members(self, group_email: str) -> List[str]:
        """Получить участников группы"""
        await self._ensure_initialized()
        self.logger.info(f"Получение участников группы {group_email} (заглушка)")
        # TODO: Реализовать через Google API
        return []
    
    async def add_member(self, group_email: str, user_email: str) -> bool:
        """Добавить участника в группу"""
        await self._ensure_initialized()
        
        if not self.service:
            logger.error("Google API клиент не инициализирован")
            return False
            
        try:
            body = {
                'email': user_email,
                'role': 'MEMBER'
            }
            
            self.service.members().insert(
                groupKey=group_email,
                body=body
            ).execute()
            
            self.logger.info(f"✅ Пользователь {user_email} успешно добавлен в группу {group_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка добавления пользователя {user_email} в группу {group_email}: {str(e)}")
            if isinstance(e, HttpError):
                self.logger.error(f"🔍 HTTP статус: {e.resp.status}")
                self.logger.error(f"🔍 Ответ сервера: {e.content}")
            return False
    
    async def remove_member(self, group_email: str, user_email: str) -> bool:
        """Удалить участника из группы"""
        await self._ensure_initialized()
        self.logger.info(f"Удаление {user_email} из группы {group_email} (заглушка)")
        # TODO: Реализовать через Google API
        return True
        self.logger = logging.getLogger(__name__)
    
    async def get_all(self) -> List[Group]:
        """Получить все группы"""
        # TODO: Реализовать через Google API
        self.logger.info("Получение всех групп (заглушка)")
        return []
    
    async def get_by_email(self, email: str) -> Optional[Group]:
        """Получить группу по email"""
        # TODO: Реализовать через Google API
        self.logger.info(f"Получение группы {email} (заглушка)")
        return None
    
    async def create(self, group: Group) -> Group:
        """Создать группу"""
        # TODO: Реализовать через Google API
        self.logger.info(f"Создание группы {group.email} (заглушка)")
        return group
    
    async def update(self, group: Group) -> Group:
        """Обновить группу"""
        # TODO: Реализовать через Google API
        self.logger.info(f"Обновление группы {group.email} (заглушка)")
        return group
    
    async def delete(self, email: str) -> bool:
        """Удалить группу"""
        # TODO: Реализовать через Google API
        self.logger.info(f"Удаление группы {email} (заглушка)")
        return True
    
    async def add_member(self, group_email: str, member_email: str) -> bool:
        """Добавить участника в группу"""
        # TODO: Реализовать через Google API
        self.logger.info(f"Добавление {member_email} в группу {group_email} (заглушка)")
        return True
    
    async def remove_member(self, group_email: str, member_email: str) -> bool:
        """Удалить участника из группы"""
        # TODO: Реализовать через Google API
        self.logger.info(f"Удаление {member_email} из группы {group_email} (заглушка)")
        return True
    
    async def get_members(self, group_email: str) -> List[str]:
        """Получить участников группы"""
        # TODO: Реализовать через Google API
        self.logger.info(f"Получение участников группы {group_email} (заглушка)")
        return []
