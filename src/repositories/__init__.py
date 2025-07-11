#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пакет репозиториев для доступа к данным.
"""

from .interfaces import (
    IUserRepository,
    IGroupRepository,
    IOrgUnitRepository,
    ICalendarRepository,
    ICacheRepository,
    IAuditRepository
)

__all__ = [
    'IUserRepository',
    'IGroupRepository', 
    'IOrgUnitRepository',
    'ICalendarRepository',
    'ICacheRepository',
    'IAuditRepository'
]
