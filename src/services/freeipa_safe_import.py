#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Безопасный импорт FreeIPA модулей с обработкой ошибок Kerberos
"""

import logging

logger = logging.getLogger(__name__)

# Флаги доступности
FREEIPA_AVAILABLE = False
KERBEROS_AVAILABLE = False
FREEIPA_IMPORT_ERROR = None

# Классы и функции по умолчанию
FreeIPAClient = None
FreeIPAError = Exception
HTTPKerberosAuth = None
OPTIONAL = None

# Попытка импорта python-freeipa
try:
    from python_freeipa import Client as FreeIPAClient
    from python_freeipa.exceptions import FreeIPAError
    FREEIPA_AVAILABLE = True
    logger.info("✅ python-freeipa импортирован успешно")
except Exception as e:
    error_str = str(e).lower()
    
    if "kerberos" in error_str or "kfw" in error_str or "gssapi" in error_str:
        # Kerberos ошибка - пробуем наш stub
        logger.warning(f"⚠️ Kerberos недоступен, используем stub: {e}")
        try:
            from .freeipa_client_stub import Client as FreeIPAClient, FreeIPAError
            FREEIPA_AVAILABLE = True
            FREEIPA_IMPORT_ERROR = f"Kerberos недоступен (используется stub): {e}"
            logger.info("✅ FreeIPA stub импортирован")
        except Exception as stub_error:
            logger.error(f"❌ Не удалось импортировать FreeIPA stub: {stub_error}")
            FREEIPA_IMPORT_ERROR = f"Stub failed: {stub_error}"
    else:
        # Другая ошибка
        logger.error(f"❌ Ошибка импорта python-freeipa: {e}")
        FREEIPA_IMPORT_ERROR = str(e)

# Попытка импорта Kerberos
try:
    from requests_kerberos import HTTPKerberosAuth, OPTIONAL
    KERBEROS_AVAILABLE = True
except Exception as e:
    logger.info(f"ℹ️ Kerberos не доступен: {e}")

def get_freeipa_status():
    """Получить статус доступности FreeIPA"""
    return {
        'freeipa_available': FREEIPA_AVAILABLE,
        'kerberos_available': KERBEROS_AVAILABLE,
        'import_error': FREEIPA_IMPORT_ERROR,
        'client_class': FreeIPAClient.__name__ if FreeIPAClient else None
    }

def create_freeipa_client(*args, **kwargs):
    """Безопасное создание FreeIPA клиента"""
    if not FREEIPA_AVAILABLE:
        raise ImportError(f"FreeIPA недоступен: {FREEIPA_IMPORT_ERROR}")
    
    return FreeIPAClient(*args, **kwargs)
