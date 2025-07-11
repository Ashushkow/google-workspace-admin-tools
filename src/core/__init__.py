#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пакет core содержит основную бизнес-логику приложения.
"""

from .application import Application
from .domain import User, Group, OrganizationalUnit
from ..services import UserService, GroupService
from ..repositories.interfaces import IUserRepository, IGroupRepository
from .di_container import container, inject, service

__all__ = [
    'Application',
    'User', 'Group', 'OrganizationalUnit',
    'UserService', 'GroupService',
    'IUserRepository', 'IGroupRepository',
    'container', 'inject', 'service'
]
