#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Доменные модели для Admin Team Tools.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UserStatus(Enum):
    """Статус пользователя"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class GroupType(Enum):
    """Тип группы"""
    SECURITY = "security"
    DISTRIBUTION = "distribution"
    DYNAMIC = "dynamic"


@dataclass
class User:
    """Модель пользователя Google Workspace"""
    primary_email: str
    full_name: str
    user_id: str = ""  # Google User ID
    first_name: str = ""
    last_name: str = ""
    status: UserStatus = UserStatus.ACTIVE
    suspended: bool = False
    org_unit_path: str = "/"
    last_login_time: Optional[datetime] = None
    creation_time: Optional[datetime] = None
    phone: str = ""
    recovery_email: str = ""
    employee_id: str = ""
    department: str = ""
    manager: str = ""
    title: str = ""
    location: str = ""
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    groups: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Постобработка после создания"""
        if not self.first_name and not self.last_name:
            parts = self.full_name.split(" ", 1)
            self.first_name = parts[0] if parts else ""
            self.last_name = parts[1] if len(parts) > 1 else ""
    
    @property
    def email(self) -> str:
        """Алиас для primary_email для обратной совместимости"""
        return self.primary_email
    
    @property
    def id(self) -> str:
        """Алиас для user_id для обратной совместимости"""
        return self.user_id
    
    @property
    def is_suspended(self) -> bool:
        """Алиас для suspended для обратной совместимости"""
        return self.suspended
    
    @property
    def is_active(self) -> bool:
        """Проверка активности пользователя"""
        return self.status == UserStatus.ACTIVE and not self.suspended
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя"""
        return self.full_name or f"{self.first_name} {self.last_name}".strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            'primaryEmail': self.primary_email,
            'name': {
                'fullName': self.full_name,
                'givenName': self.first_name,
                'familyName': self.last_name
            },
            'suspended': self.suspended,
            'orgUnitPath': self.org_unit_path,
            'phones': [{'value': self.phone, 'type': 'work'}] if self.phone else [],
            'recoveryEmail': self.recovery_email,
            'externalIds': [{'value': self.employee_id, 'type': 'organization'}] if self.employee_id else [],
            'organizations': [{
                'department': self.department,
                'title': self.title,
                'location': self.location
            }] if any([self.department, self.title, self.location]) else []
        }


@dataclass
class Group:
    """Модель группы Google Workspace"""
    email: str
    name: str
    description: str = ""
    group_type: GroupType = GroupType.SECURITY
    members_count: int = 0
    admin_created: bool = False
    direct_members_count: int = 0
    aliases: List[str] = field(default_factory=list)
    members: List[str] = field(default_factory=list)
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя группы"""
        return self.name or self.email
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            'email': self.email,
            'name': self.name,
            'description': self.description,
            'adminCreated': self.admin_created,
            'aliases': self.aliases
        }


@dataclass
class OrganizationalUnit:
    """Модель организационного подразделения"""
    name: str
    org_unit_path: str
    description: str = ""
    parent_org_unit_path: str = ""
    block_inheritance: bool = False
    
    @property
    def full_path(self) -> str:
        """Полный путь подразделения"""
        return self.org_unit_path


@dataclass
class CalendarEvent:
    """Модель события календаря"""
    id: str
    summary: str
    description: str = ""
    start_time: datetime = None
    end_time: datetime = None
    attendees: List[str] = field(default_factory=list)
    location: str = ""
    creator: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            'id': self.id,
            'summary': self.summary,
            'description': self.description,
            'start': {'dateTime': self.start_time.isoformat() if self.start_time else None},
            'end': {'dateTime': self.end_time.isoformat() if self.end_time else None},
            'attendees': [{'email': email} for email in self.attendees],
            'location': self.location
        }


@dataclass
class APIQuota:
    """Модель квоты API"""
    service: str
    limit: int
    used: int
    remaining: int
    reset_time: datetime
    
    @property
    def usage_percentage(self) -> float:
        """Процент использования квоты"""
        return (self.used / self.limit) * 100 if self.limit > 0 else 0
    
    @property
    def is_near_limit(self) -> bool:
        """Проверка близости к лимиту"""
        return self.usage_percentage > 80


@dataclass
class AuditLog:
    """Модель записи аудита"""
    timestamp: datetime
    user: str
    action: str
    resource: str
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    user_agent: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'user': self.user,
            'action': self.action,
            'resource': self.resource,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
