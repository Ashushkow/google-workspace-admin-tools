#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерфейсы репозиториев для доступа к данным.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..core.domain import User, Group, OrganizationalUnit, CalendarEvent


class IUserRepository(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    async def get_all(self) -> List[User]:
        """Получить всех пользователей"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Создать пользователя"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        pass
    
    @abstractmethod
    async def delete(self, email: str) -> bool:
        """Удалить пользователя"""
        pass
    
    @abstractmethod
    async def search(self, query: str) -> List[User]:
        """Поиск пользователей"""
        pass
    
    @abstractmethod
    async def get_by_org_unit(self, org_unit_path: str) -> List[User]:
        """Получить пользователей по организационному подразделению"""
        pass


class IGroupRepository(ABC):
    """Интерфейс репозитория групп"""
    
    @abstractmethod
    async def get_all(self) -> List[Group]:
        """Получить все группы"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Group]:
        """Получить группу по email"""
        pass
    
    @abstractmethod
    async def create(self, group: Group) -> Group:
        """Создать группу"""
        pass
    
    @abstractmethod
    async def update(self, group: Group) -> Group:
        """Обновить группу"""
        pass
    
    @abstractmethod
    async def delete(self, email: str) -> bool:
        """Удалить группу"""
        pass
    
    @abstractmethod
    async def add_member(self, group_email: str, member_email: str) -> bool:
        """Добавить участника в группу"""
        pass
    
    @abstractmethod
    async def remove_member(self, group_email: str, member_email: str) -> bool:
        """Удалить участника из группы"""
        pass
    
    @abstractmethod
    async def get_members(self, group_email: str) -> List[str]:
        """Получить участников группы"""
        pass


class IOrgUnitRepository(ABC):
    """Интерфейс репозитория организационных подразделений"""
    
    @abstractmethod
    async def get_all(self) -> List[OrganizationalUnit]:
        """Получить все подразделения"""
        pass
    
    @abstractmethod
    async def get_by_path(self, path: str) -> Optional[OrganizationalUnit]:
        """Получить подразделение по пути"""
        pass
    
    @abstractmethod
    async def create(self, org_unit: OrganizationalUnit) -> OrganizationalUnit:
        """Создать подразделение"""
        pass
    
    @abstractmethod
    async def update(self, org_unit: OrganizationalUnit) -> OrganizationalUnit:
        """Обновить подразделение"""
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Удалить подразделение"""
        pass


class ICalendarRepository(ABC):
    """Интерфейс репозитория календарей"""
    
    @abstractmethod
    async def get_events(self, calendar_id: str, start_date: str = None, end_date: str = None) -> List[CalendarEvent]:
        """Получить события календаря"""
        pass
    
    @abstractmethod
    async def create_event(self, calendar_id: str, event: CalendarEvent) -> CalendarEvent:
        """Создать событие"""
        pass
    
    @abstractmethod
    async def update_event(self, calendar_id: str, event: CalendarEvent) -> CalendarEvent:
        """Обновить событие"""
        pass
    
    @abstractmethod
    async def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Удалить событие"""
        pass
    
    @abstractmethod
    async def get_calendars(self) -> List[Dict[str, Any]]:
        """Получить список календарей"""
        pass


class ICacheRepository(ABC):
    """Интерфейс репозитория кэша"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Установить значение в кэш"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Удалить значение из кэша"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Очистить весь кэш"""
        pass


class IAuditRepository(ABC):
    """Интерфейс репозитория аудита"""
    
    @abstractmethod
    async def log_action(self, user: str, action: str, resource: str, details: Dict[str, Any] = None) -> bool:
        """Записать действие в аудит"""
        pass
    
    @abstractmethod
    async def get_logs(self, user: str = None, action: str = None, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Получить записи аудита"""
        pass
    
    @abstractmethod
    async def cleanup_old_logs(self, days: int = 90) -> int:
        """Очистить старые записи аудита"""
        pass
