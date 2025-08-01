#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API клиент для работы с "Моей Командой" (MyTeam)
Интеграция с системой ismyteam.ru для создания и управления пользователями
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MyTeamUser:
    """Структура пользователя "Моей Команды"""
    id: Optional[str] = None
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    phone: str = ""
    department: str = ""
    position: str = ""
    is_active: bool = True


@dataclass
class MyTeamApiConfig:
    """Конфигурация API "Моей Команды"""
    base_url: str = "https://sputnik8.ismyteam.ru"
    api_token: str = ""
    timeout: int = 30
    verify_ssl: bool = True


class MyTeamAPI:
    """API клиент для работы с "Моей Командой"""
    
    def __init__(self, config: MyTeamApiConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'AdminTools-MyTeam-Integration/1.0'
        })
        
        if config.api_token:
            self.session.headers['Authorization'] = f'Bearer {config.api_token}'
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> requests.Response:
        """Выполняет HTTP запрос к API"""
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            logger.debug(f"API Request: {method} {url} -> {response.status_code}")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к API: {e}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """Тестирует подключение к API"""
        try:
            # Пробуем базовые endpoints
            endpoints_to_test = [
                ("/api/users", "GET"),
                ("/api/v1/users", "GET"),
                ("/api/v2/users", "GET")
            ]
            
            results = {}
            for endpoint, method in endpoints_to_test:
                try:
                    response = self._make_request(method, endpoint)
                    results[endpoint] = {
                        'status_code': response.status_code,
                        'accessible': response.status_code != 404,
                        'requires_auth': response.status_code == 401
                    }
                except Exception as e:
                    results[endpoint] = {
                        'status_code': None,
                        'accessible': False,
                        'error': str(e)
                    }
            
            return {
                'success': any(r.get('accessible', False) for r in results.values()),
                'endpoints': results,
                'config_status': 'configured' if self.config.api_token else 'no_token'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'config_status': 'error'
            }
    
    def create_user(self, user: MyTeamUser) -> Dict[str, Any]:
        """
        Создает нового пользователя в "Моей Команде"
        
        Args:
            user: Объект с данными пользователя
            
        Returns:
            Результат операции с информацией о созданном пользователе
        """
        # Формируем данные для API
        user_data = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username or user.email.split('@')[0],
            'phone': user.phone,
            'department': user.department,
            'position': user.position,
            'is_active': user.is_active
        }
        
        # Убираем пустые поля
        user_data = {k: v for k, v in user_data.items() if v}
        
        try:
            # Пробуем разные endpoints для создания пользователя
            endpoints = ['/api/users', '/api/v1/users', '/api/v2/users']
            
            for endpoint in endpoints:
                try:
                    response = self._make_request('POST', endpoint, data=user_data)
                    
                    if response.status_code == 201:
                        # Успешное создание
                        result_data = response.json() if response.content else {}
                        return {
                            'success': True,
                            'message': f'Пользователь {user.email} успешно создан в "Моей Команде"',
                            'user_data': result_data,
                            'endpoint_used': endpoint
                        }
                    elif response.status_code == 409:
                        # Пользователь уже существует
                        return {
                            'success': False,
                            'message': f'Пользователь {user.email} уже существует в "Моей Команде"',
                            'error_code': 'user_exists'
                        }
                    elif response.status_code == 401:
                        # Проблемы с авторизацией
                        return {
                            'success': False,
                            'message': 'Ошибка авторизации. Проверьте API токен.',
                            'error_code': 'auth_error'
                        }
                    elif response.status_code == 400:
                        # Ошибка валидации данных
                        error_detail = response.json() if response.content else {}
                        return {
                            'success': False,
                            'message': f'Ошибка валидации данных: {error_detail}',
                            'error_code': 'validation_error',
                            'details': error_detail
                        }
                    
                except requests.exceptions.RequestException:
                    continue  # Пробуем следующий endpoint
            
            # Если все endpoints не работают
            return {
                'success': False,
                'message': 'Не удалось найти рабочий API endpoint для создания пользователя',
                'error_code': 'no_working_endpoint'
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания пользователя: {e}")
            return {
                'success': False,
                'message': f'Ошибка создания пользователя: {str(e)}',
                'error_code': 'unexpected_error'
            }
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Получает информацию о пользователе по ID"""
        try:
            endpoints = [f'/api/users/{user_id}', f'/api/v1/users/{user_id}', f'/api/v2/users/{user_id}']
            
            for endpoint in endpoints:
                try:
                    response = self._make_request('GET', endpoint)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'user_data': response.json(),
                            'endpoint_used': endpoint
                        }
                except requests.exceptions.RequestException:
                    continue
            
            return {
                'success': False,
                'message': f'Пользователь с ID {user_id} не найден',
                'error_code': 'user_not_found'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Ошибка получения пользователя: {str(e)}',
                'error_code': 'unexpected_error'
            }
    
    def list_users(self, limit: int = 100) -> Dict[str, Any]:
        """Получает список пользователей"""
        try:
            endpoints = ['/api/users', '/api/v1/users', '/api/v2/users']
            params = {'limit': limit} if limit else {}
            
            for endpoint in endpoints:
                try:
                    response = self._make_request('GET', endpoint, params=params)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'users': response.json(),
                            'endpoint_used': endpoint
                        }
                except requests.exceptions.RequestException:
                    continue
            
            return {
                'success': False,
                'message': 'Не удалось получить список пользователей',
                'error_code': 'no_working_endpoint'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Ошибка получения списка пользователей: {str(e)}',
                'error_code': 'unexpected_error'
            }


def create_myteam_api(api_token: str = "", base_url: str = "https://sputnik8.ismyteam.ru") -> MyTeamAPI:
    """
    Создает экземпляр API клиента для "Моей Команды"
    
    Args:
        api_token: API токен для авторизации
        base_url: Базовый URL API
        
    Returns:
        Настроенный экземпляр MyTeamAPI
    """
    config = MyTeamApiConfig(
        base_url=base_url,
        api_token=api_token,
        timeout=30,
        verify_ssl=True
    )
    
    return MyTeamAPI(config)


# Вспомогательные функции для интеграции с существующим кодом
def validate_myteam_user_data(email: str, first_name: str, last_name: str, 
                             phone: str = "", department: str = "", position: str = "") -> Dict[str, Any]:
    """Валидация данных пользователя перед отправкой в API"""
    errors = []
    
    if not email or '@' not in email:
        errors.append("Некорректный email адрес")
    
    if not first_name.strip():
        errors.append("Имя обязательно для заполнения")
    
    if not last_name.strip():
        errors.append("Фамилия обязательна для заполнения")
    
    if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
        errors.append("Некорректный формат телефона")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }