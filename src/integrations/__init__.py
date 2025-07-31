#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль интеграций Admin Team Tools
"""

# Условный импорт FreeIPA - не загружаем при старте приложения
try:
    from .freeipa_integration import FreeIPAIntegration, setup_freeipa_integration
    FREEIPA_AVAILABLE = True
except ImportError:
    FreeIPAIntegration = None
    setup_freeipa_integration = None
    FREEIPA_AVAILABLE = False

__all__ = [
    'FreeIPAIntegration',
    'setup_freeipa_integration',
    'FREEIPA_AVAILABLE'
]
