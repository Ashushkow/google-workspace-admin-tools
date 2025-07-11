#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация для тестов pytest.
"""

import os
import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

@pytest.fixture
def mock_google_service():
    """Мок для Google API service"""
    service = Mock()
    service.users.return_value.list.return_value.execute.return_value = {
        'users': [
            {
                'primaryEmail': 'test@example.com',
                'name': {'fullName': 'Test User'},
                'suspended': False,
                'orgUnitPath': '/',
                'lastLoginTime': '2023-01-01T00:00:00.000Z'
            }
        ]
    }
    return service

@pytest.fixture
def mock_credentials():
    """Мок для Google credentials"""
    with patch('google.oauth2.service_account.Credentials') as mock_creds:
        mock_creds.from_service_account_file.return_value = Mock()
        yield mock_creds

@pytest.fixture
def temp_config_dir(tmp_path):
    """Временная директория для конфигурации"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Создаем тестовый файл настроек
    settings_file = config_dir / "settings.json"
    settings_file.write_text('{"theme": "light", "language": "ru"}')
    
    # Создаем тестовый файл credentials
    credentials_file = tmp_path / "credentials.json"
    credentials_file.write_text('''{
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\\ntest-key\\n-----END PRIVATE KEY-----\\n",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "subject": "admin@test.com"
    }''')
    
    return tmp_path

@pytest.fixture
def mock_env_vars():
    """Мок для переменных окружения"""
    env_vars = {
        'GOOGLE_WORKSPACE_DOMAIN': 'test.com',
        'GOOGLE_WORKSPACE_ADMIN': 'admin@test.com',
        'APP_DEBUG': 'True',
        'LOG_LEVEL': 'DEBUG'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture(autouse=True)
def cleanup_logs():
    """Очистка логов после тестов"""
    yield
    # Очищаем логи после каждого теста
    log_files = Path('logs').glob('*.log')
    for log_file in log_files:
        if log_file.exists():
            log_file.unlink()

class TestConfig:
    """Конфигурация для тестов"""
    
    # Тестовые данные
    TEST_DOMAIN = "test.com"
    TEST_ADMIN_EMAIL = "admin@test.com"
    TEST_USER_EMAIL = "user@test.com"
    
    # Моки для Google API
    @staticmethod
    def mock_google_api_response(users=None, groups=None):
        """Создать мок ответа Google API"""
        response = {}
        
        if users:
            response['users'] = users
        if groups:
            response['groups'] = groups
            
        return response
