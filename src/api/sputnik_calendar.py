#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилита для управления календарем SPUTNIK (общий).
Специализированный класс для работы с общим календарем команды.
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .calendar_api import GoogleCalendarAPI, CalendarInfo, CalendarPermission

logger = logging.getLogger(__name__)


@dataclass
class SputnikMember:
    """Участник календаря SPUTNIK"""
    email: str
    role: str
    name: str = ""
    department: str = ""
    active: bool = True


class SputnikCalendarManager:
    """Менеджер для календаря SPUTNIK (общий)"""
    
    # URL календаря SPUTNIK (общий)
    SPUTNIK_CALENDAR_URL = "https://calendar.google.com/calendar/u/0?cid=dGNvNXZpcWxjNnZ0MjBsYmtsaDAzdTJrYjhAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ"
    
    # ID календаря (декодированный из URL)
    SPUTNIK_CALENDAR_ID = "tco5viqlc6vt20lbklh03u2kb8@group.calendar.google.com"
    
    def __init__(self, credentials_path: str = "credentials.json"):
        """
        Инициализация менеджера календаря SPUTNIK
        
        Args:
            credentials_path: Путь к файлу учетных данных
        """
        self.calendar_api = GoogleCalendarAPI(credentials_path)
        self.calendar_id = self.SPUTNIK_CALENDAR_ID
        self.calendar_info: Optional[CalendarInfo] = None
        
    def initialize(self) -> bool:
        """
        Инициализация и проверка доступа к календарю
        
        Returns:
            True если инициализация успешна
        """
        try:
            # Аутентификация
            if not self.calendar_api.authenticate():
                logger.error("Не удалось аутентифицироваться в Google Calendar API")
                return False
            
            # Проверяем доступ к календарю SPUTNIK
            self.calendar_info = self.calendar_api.get_calendar_by_id(self.calendar_id)
            
            if not self.calendar_info:
                logger.error(f"Не удалось получить доступ к календарю SPUTNIK: {self.calendar_id}")
                return False
            
            logger.info(f"✅ Подключение к календарю SPUTNIK успешно: {self.calendar_info.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации календаря SPUTNIK: {e}")
            return False
    
    def get_calendar_info(self) -> Optional[CalendarInfo]:
        """
        Получение информации о календаре SPUTNIK
        
        Returns:
            Информация о календаре
        """
        return self.calendar_info
    
    def get_members(self) -> List[SputnikMember]:
        """
        Получение списка участников календаря SPUTNIK
        
        Returns:
            Список участников
        """
        try:
            permissions = self.calendar_api.get_calendar_permissions(self.calendar_id)
            members = []
            
            for permission in permissions:
                # Пропускаем системные разрешения
                if permission.scope_type != 'user':
                    continue
                
                member = SputnikMember(
                    email=permission.user_email,
                    role=permission.role
                )
                members.append(member)
            
            logger.info(f"Найдено участников календаря SPUTNIK: {len(members)}")
            return members
            
        except Exception as e:
            logger.error(f"Ошибка получения участников календаря SPUTNIK: {e}")
            return []
    
    def add_member(self, email: str, role: str = 'reader', name: str = "", department: str = "") -> bool:
        """
        Добавление участника к календарю SPUTNIK
        
        Args:
            email: Email нового участника
            role: Роль доступа (reader, writer, owner)
            name: Имя участника (опционально)
            department: Отдел участника (опционально)
            
        Returns:
            True если участник добавлен успешно
        """
        try:
            # Проверяем, не добавлен ли уже этот пользователь
            existing_members = self.get_members()
            for member in existing_members:
                if member.email.lower() == email.lower():
                    logger.warning(f"Участник {email} уже добавлен к календарю SPUTNIK")
                    return False
            
            # Добавляем участника
            success = self.calendar_api.add_user_to_calendar(self.calendar_id, email, role)
            
            if success:
                logger.info(f"✅ Участник {email} добавлен к календарю SPUTNIK с ролью {role}")
                
                # Логируем дополнительную информацию, если предоставлена
                if name or department:
                    logger.info(f"   Дополнительная информация: {name} ({department})")
            else:
                logger.error(f"❌ Не удалось добавить участника {email} к календарю SPUTNIK")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка добавления участника {email} к календарю SPUTNIK: {e}")
            return False
    
    def remove_member(self, email: str) -> bool:
        """
        Удаление участника из календаря SPUTNIK
        
        Args:
            email: Email участника для удаления
            
        Returns:
            True если участник удален успешно
        """
        try:
            # Проверяем, есть ли такой участник
            existing_members = self.get_members()
            member_found = False
            
            for member in existing_members:
                if member.email.lower() == email.lower():
                    member_found = True
                    break
            
            if not member_found:
                logger.warning(f"Участник {email} не найден в календаре SPUTNIK")
                return False
            
            # Удаляем участника
            success = self.calendar_api.remove_user_from_calendar(self.calendar_id, email)
            
            if success:
                logger.info(f"✅ Участник {email} удален из календаря SPUTNIK")
            else:
                logger.error(f"❌ Не удалось удалить участника {email} из календаря SPUTNIK")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка удаления участника {email} из календаря SPUTNIK: {e}")
            return False
    
    def change_member_role(self, email: str, new_role: str) -> bool:
        """
        Изменение роли участника календаря SPUTNIK
        
        Args:
            email: Email участника
            new_role: Новая роль (reader, writer, owner)
            
        Returns:
            True если роль изменена успешно
        """
        try:
            # Проверяем, есть ли такой участник
            existing_members = self.get_members()
            current_member = None
            
            for member in existing_members:
                if member.email.lower() == email.lower():
                    current_member = member
                    break
            
            if not current_member:
                logger.warning(f"Участник {email} не найден в календаре SPUTNIK")
                return False
            
            # Изменяем роль
            success = self.calendar_api.update_user_role(self.calendar_id, email, new_role)
            
            if success:
                logger.info(f"✅ Роль участника {email} в календаре SPUTNIK изменена с {current_member.role} на {new_role}")
            else:
                logger.error(f"❌ Не удалось изменить роль участника {email} в календаре SPUTNIK")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка изменения роли участника {email} в календаре SPUTNIK: {e}")
            return False
    
    def add_multiple_members(self, members_data: List[Dict[str, str]], default_role: str = 'reader') -> Dict[str, bool]:
        """
        Массовое добавление участников к календарю SPUTNIK
        
        Args:
            members_data: Список данных участников [{'email': '...', 'role': '...', 'name': '...'}]
            default_role: Роль по умолчанию
            
        Returns:
            Словарь с результатами добавления {email: success}
        """
        results = {}
        
        logger.info(f"Начинаем массовое добавление {len(members_data)} участников к календарю SPUTNIK")
        
        for member_data in members_data:
            email = member_data.get('email', '').strip()
            role = member_data.get('role', default_role)
            name = member_data.get('name', '')
            department = member_data.get('department', '')
            
            if not email:
                logger.warning("Пропускаем участника без email")
                continue
            
            # Добавляем участника
            success = self.add_member(email, role, name, department)
            results[email] = success
            
            # Небольшая пауза между запросами для избежания лимитов API
            import time
            time.sleep(0.5)
        
        successful_adds = sum(1 for success in results.values() if success)
        logger.info(f"Массовое добавление завершено: {successful_adds}/{len(results)} успешно")
        
        return results
    
    def get_member_statistics(self) -> Dict[str, int]:
        """
        Получение статистики участников календаря SPUTNIK
        
        Returns:
            Статистика по ролям
        """
        members = self.get_members()
        stats = {
            'total': len(members),
            'owners': 0,
            'writers': 0,
            'readers': 0,
            'other': 0
        }
        
        for member in members:
            if member.role == 'owner':
                stats['owners'] += 1
            elif member.role == 'writer':
                stats['writers'] += 1
            elif member.role == 'reader':
                stats['readers'] += 1
            else:
                stats['other'] += 1
        
        return stats
    
    def export_members_to_dict(self) -> List[Dict[str, str]]:
        """
        Экспорт участников в формат словаря
        
        Returns:
            Список участников в формате словаря
        """
        members = self.get_members()
        
        members_list = []
        for member in members:
            member_dict = {
                'email': member.email,
                'role': member.role,
                'name': member.name,
                'department': member.department,
                'active': str(member.active)
            }
            members_list.append(member_dict)
        
        return members_list
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Простая валидация email адреса
        
        Args:
            email: Email для проверки
            
        Returns:
            True если email корректный
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def get_role_description(role: str) -> str:
        """
        Получение описания роли на русском языке
        
        Args:
            role: Роль на английском
            
        Returns:
            Описание роли на русском
        """
        descriptions = {
            'owner': 'Владелец - полный доступ к календарю и управлению участниками',
            'writer': 'Редактор - может создавать и изменять события',
            'reader': 'Читатель - может только просматривать события',
            'freeBusyReader': 'Просмотр занятости - видит только информацию о занятости'
        }
        return descriptions.get(role, f'Неизвестная роль: {role}')


def create_sputnik_calendar_manager(credentials_path: str = "credentials.json") -> Optional[SputnikCalendarManager]:
    """
    Создание и инициализация менеджера календаря SPUTNIK
    
    Args:
        credentials_path: Путь к файлу учетных данных
        
    Returns:
        Инициализированный менеджер или None при ошибке
    """
    try:
        manager = SputnikCalendarManager(credentials_path)
        
        if manager.initialize():
            return manager
        else:
            logger.error("Не удалось инициализировать менеджер календаря SPUTNIK")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка создания менеджера календаря SPUTNIK: {e}")
        return None


# Пример использования
if __name__ == "__main__":
    import sys
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Создаем менеджер календаря SPUTNIK
    manager = create_sputnik_calendar_manager()
    
    if not manager:
        print("❌ Не удалось инициализировать менеджер календаря SPUTNIK")
        sys.exit(1)
    
    # Получаем информацию о календаре
    calendar_info = manager.get_calendar_info()
    if calendar_info:
        print(f"📅 Календарь: {calendar_info.name}")
        print(f"👤 Владелец: {calendar_info.owner}")
    
    # Получаем участников
    members = manager.get_members()
    print(f"👥 Участников: {len(members)}")
    
    for member in members:
        role_desc = manager.get_role_description(member.role)
        print(f"  • {member.email} - {role_desc}")
    
    # Статистика
    stats = manager.get_member_statistics()
    print(f"📊 Статистика: {stats}")
