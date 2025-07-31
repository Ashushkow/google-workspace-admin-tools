#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пакет core содержит основную бизнес-логику приложения.
"""

# Убираем импорт Application и сервисов чтобы избежать циклических импортов
# from .application import Application
from .domain import User, Group, OrganizationalUnit
# Убираем импорт сервисов из-за циклического импорта
# from ..services import UserService, GroupService
from ..repositories.interfaces import IUserRepository, IGroupRepository
from .di_container import container, inject, service

__all__ = [
    # 'Application',  # временно убрано из-за циклического импорта
    'User', 'Group', 'OrganizationalUnit',
    'UserService', 'GroupService',
    'IUserRepository', 'IGroupRepository',
    'container', 'inject', 'service'
]
