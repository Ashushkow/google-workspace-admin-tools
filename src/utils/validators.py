#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система валидации данных для Admin Team Tools.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime


def validate_email(email: str) -> bool:
    """
    Валидация email адреса
    
    Args:
        email: Email для проверки
        
    Returns:
        True если email валиден
    """
    if not email or not isinstance(email, str):
        return False
    
    # Простая регулярка для email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Валидация телефонного номера
    
    Args:
        phone: Телефон для проверки
        
    Returns:
        True если телефон валиден
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Убираем все символы кроме цифр и +
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Проверяем формат
    if clean_phone.startswith('+'):
        # Международный формат
        return len(clean_phone) >= 10 and len(clean_phone) <= 15
    else:
        # Местный формат
        return len(clean_phone) >= 7 and len(clean_phone) <= 11


def validate_password(password: str) -> tuple[bool, List[str]]:
    """
    Валидация пароля
    
    Args:
        password: Пароль для проверки
        
    Returns:
        Кортеж (валиден, список ошибок)
    """
    errors = []
    
    if not password or not isinstance(password, str):
        errors.append("Пароль не может быть пустым")
        return False, errors
    
    if len(password) < 8:
        errors.append("Пароль должен содержать минимум 8 символов")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Пароль должен содержать заглавные буквы")
    
    if not re.search(r'[a-z]', password):
        errors.append("Пароль должен содержать строчные буквы")
    
    if not re.search(r'\d', password):
        errors.append("Пароль должен содержать цифры")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Пароль должен содержать специальные символы")
    
    return len(errors) == 0, errors


def validate_org_unit_path(path: str) -> bool:
    """
    Валидация пути организационного подразделения
    
    Args:
        path: Путь для проверки
        
    Returns:
        True если путь валиден
    """
    if not path or not isinstance(path, str):
        return False
    
    # Путь должен начинаться с /
    if not path.startswith('/'):
        return False
    
    # Проверяем каждый компонент пути
    components = path.split('/')[1:]  # Убираем первый пустой элемент
    
    for component in components:
        if not component:  # Пустой компонент
            return False
        
        # Проверяем допустимые символы
        if not re.match(r'^[a-zA-Z0-9_\-\s]+$', component):
            return False
    
    return True


def validate_user_data(user_data: Dict[str, Any]) -> List[str]:
    """
    Валидация данных пользователя
    
    Args:
        user_data: Данные пользователя
        
    Returns:
        Список ошибок валидации
    """
    errors = []
    
    # Обязательные поля
    required_fields = ['primary_email', 'full_name']
    
    for field in required_fields:
        if field not in user_data or not user_data[field]:
            errors.append(f"Поле '{field}' обязательно для заполнения")
    
    # Валидация email
    if 'primary_email' in user_data:
        if not validate_email(user_data['primary_email']):
            errors.append("Неверный формат email")
    
    # Валидация имени
    if 'full_name' in user_data:
        name = user_data['full_name']
        if not isinstance(name, str) or len(name.strip()) < 2:
            errors.append("Имя должно содержать минимум 2 символа")
    
    # Валидация телефона
    if 'phone' in user_data and user_data['phone']:
        if not validate_phone(user_data['phone']):
            errors.append("Неверный формат телефона")
    
    # Валидация email восстановления
    if 'recovery_email' in user_data and user_data['recovery_email']:
        if not validate_email(user_data['recovery_email']):
            errors.append("Неверный формат email восстановления")
    
    # Валидация пути подразделения
    if 'org_unit_path' in user_data and user_data['org_unit_path']:
        if not validate_org_unit_path(user_data['org_unit_path']):
            errors.append("Неверный формат пути подразделения")
    
    # Валидация пароля
    if 'password' in user_data and user_data['password']:
        is_valid, password_errors = validate_password(user_data['password'])
        if not is_valid:
            errors.extend(password_errors)
    
    return errors


def validate_group_data(group_data: Dict[str, Any]) -> List[str]:
    """
    Валидация данных группы
    
    Args:
        group_data: Данные группы
        
    Returns:
        Список ошибок валидации
    """
    errors = []
    
    # Обязательные поля
    required_fields = ['email', 'name']
    
    for field in required_fields:
        if field not in group_data or not group_data[field]:
            errors.append(f"Поле '{field}' обязательно для заполнения")
    
    # Валидация email группы
    if 'email' in group_data:
        if not validate_email(group_data['email']):
            errors.append("Неверный формат email группы")
    
    # Валидация имени группы
    if 'name' in group_data:
        name = group_data['name']
        if not isinstance(name, str) or len(name.strip()) < 2:
            errors.append("Имя группы должно содержать минимум 2 символа")
    
    # Валидация описания
    if 'description' in group_data and group_data['description']:
        description = group_data['description']
        if len(description) > 500:
            errors.append("Описание группы не должно превышать 500 символов")
    
    return errors


def validate_calendar_event_data(event_data: Dict[str, Any]) -> List[str]:
    """
    Валидация данных события календаря
    
    Args:
        event_data: Данные события
        
    Returns:
        Список ошибок валидации
    """
    errors = []
    
    # Обязательные поля
    required_fields = ['summary', 'start_time', 'end_time']
    
    for field in required_fields:
        if field not in event_data or not event_data[field]:
            errors.append(f"Поле '{field}' обязательно для заполнения")
    
    # Валидация времени
    if 'start_time' in event_data and 'end_time' in event_data:
        start_time = event_data['start_time']
        end_time = event_data['end_time']
        
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                errors.append("Неверный формат времени начала")
        
        if isinstance(end_time, str):
            try:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                errors.append("Неверный формат времени окончания")
        
        if isinstance(start_time, datetime) and isinstance(end_time, datetime):
            if start_time >= end_time:
                errors.append("Время начала должно быть раньше времени окончания")
    
    # Валидация участников
    if 'attendees' in event_data and event_data['attendees']:
        attendees = event_data['attendees']
        if not isinstance(attendees, list):
            errors.append("Список участников должен быть массивом")
        else:
            for attendee in attendees:
                if isinstance(attendee, str):
                    if not validate_email(attendee):
                        errors.append(f"Неверный формат email участника: {attendee}")
                elif isinstance(attendee, dict) and 'email' in attendee:
                    if not validate_email(attendee['email']):
                        errors.append(f"Неверный формат email участника: {attendee['email']}")
    
    # Валидация заголовка
    if 'summary' in event_data:
        summary = event_data['summary']
        if not isinstance(summary, str) or len(summary.strip()) < 1:
            errors.append("Заголовок события не может быть пустым")
        elif len(summary) > 200:
            errors.append("Заголовок события не должен превышать 200 символов")
    
    return errors


def sanitize_string(value: str, max_length: int = None) -> str:
    """
    Очистка строки от опасных символов
    
    Args:
        value: Строка для очистки
        max_length: Максимальная длина
        
    Returns:
        Очищенная строка
    """
    if not isinstance(value, str):
        return ""
    
    # Убираем лишние пробелы
    value = value.strip()
    
    # Убираем опасные символы
    dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    # Ограничиваем длину
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value


def validate_json_data(data: Any, schema: Dict[str, Any]) -> List[str]:
    """
    Валидация данных по схеме
    
    Args:
        data: Данные для валидации
        schema: Схема валидации
        
    Returns:
        Список ошибок
    """
    errors = []
    
    if not isinstance(data, dict):
        errors.append("Данные должны быть объектом")
        return errors
    
    # Проверка обязательных полей
    if 'required' in schema:
        for field in schema['required']:
            if field not in data:
                errors.append(f"Поле '{field}' обязательно")
    
    # Проверка типов полей
    if 'properties' in schema:
        for field, field_schema in schema['properties'].items():
            if field in data:
                field_value = data[field]
                field_type = field_schema.get('type')
                
                if field_type == 'string' and not isinstance(field_value, str):
                    errors.append(f"Поле '{field}' должно быть строкой")
                elif field_type == 'integer' and not isinstance(field_value, int):
                    errors.append(f"Поле '{field}' должно быть целым числом")
                elif field_type == 'boolean' and not isinstance(field_value, bool):
                    errors.append(f"Поле '{field}' должно быть булевым значением")
                elif field_type == 'array' and not isinstance(field_value, list):
                    errors.append(f"Поле '{field}' должно быть массивом")
    
    return errors
