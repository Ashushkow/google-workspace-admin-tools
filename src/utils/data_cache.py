# -*- coding: utf-8 -*-
"""
Кэширование данных для оптимизации работы с Google API.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional


class DataCache:
    """
    Класс для кэширования данных пользователей, групп и подразделений.
    Реализует TTL (Time To Live) кэширование для оптимизации запросов к API.
    """
    
    def __init__(self, cache_duration: int = 300):
        """
        Инициализация кэша.
        
        Args:
            cache_duration: Время жизни кэша в секундах (по умолчанию 5 минут)
        """
        self.users_cache: List[Dict[str, Any]] = []
        self.groups_cache: List[Dict[str, Any]] = []
        self.orgunits_cache: List[Dict[str, Any]] = []
        self.last_users_update: Optional[datetime] = None
        self.last_groups_update: Optional[datetime] = None
        self.cache_duration = cache_duration
        
    def is_cache_valid(self, last_update: Optional[datetime]) -> bool:
        """
        Проверяет актуальность кэша.
        
        Args:
            last_update: Время последнего обновления
            
        Returns:
            True если кэш актуален, False если нужно обновить
        """
        if last_update is None:
            return False
        return (datetime.now() - last_update).seconds < self.cache_duration
    
    def get_users(self, service: Any, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Получает пользователей из кэша или загружает через API.
        
        Args:
            service: Сервис Google Directory API
            force_refresh: Принудительное обновление кэша
            
        Returns:
            Список пользователей
        """
        if not force_refresh and self.is_cache_valid(self.last_users_update):
            return self.users_cache
        
        try:
            users = []
            page_token = None
            
            while True:
                result = service.users().list(
                    customer='my_customer',
                    maxResults=500,
                    pageToken=page_token,
                    fields='users(primaryEmail,name,suspended,orgUnitPath,creationTime),nextPageToken'
                ).execute()
                
                users.extend(result.get('users', []))
                page_token = result.get('nextPageToken')
                
                if not page_token:
                    break
            
            self.users_cache = users
            self.last_users_update = datetime.now()
            return users
            
        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")
            return self.users_cache
    
    def get_groups(self, service: Any, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Получает группы из кэша или загружает через API.
        
        Args:
            service: Сервис Google Directory API  
            force_refresh: Принудительное обновление кэша
            
        Returns:
            Список групп
        """
        if not force_refresh and self.is_cache_valid(self.last_groups_update):
            return self.groups_cache
            
        try:
            groups = []
            page_token = None
            
            while True:
                result = service.groups().list(
                    customer='my_customer',
                    maxResults=200,
                    pageToken=page_token
                ).execute()
                
                groups.extend(result.get('groups', []))
                page_token = result.get('nextPageToken')
                
                if not page_token:
                    break
            
            self.groups_cache = groups
            self.last_groups_update = datetime.now()
            return groups
            
        except Exception as e:
            print(f"Ошибка загрузки групп: {e}")
            return self.groups_cache
    
    def clear_cache(self):
        """Очищает весь кэш."""
        self.users_cache.clear()
        self.groups_cache.clear()
        self.orgunits_cache.clear()
        self.last_users_update = None
        self.last_groups_update = None


# Глобальный экземпляр кэша
data_cache = DataCache()
