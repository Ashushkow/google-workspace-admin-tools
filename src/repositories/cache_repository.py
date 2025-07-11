#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реализация репозитория кэша.
"""

from typing import Any, Optional
from .interfaces import ICacheRepository
from ..core.di_container import service
import logging
import json
import time
from pathlib import Path


@service(singleton=True)
class MemoryCacheRepository(ICacheRepository):
    """Простой репозиторий кэша в памяти"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._ttl = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        if key in self._cache:
            # Проверяем TTL
            if key in self._ttl and time.time() > self._ttl[key]:
                await self.delete(key)
                return None
            
            self.logger.debug(f"Кэш HIT: {key}")
            return self._cache[key]
        
        self.logger.debug(f"Кэш MISS: {key}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Установить значение в кэш"""
        try:
            self._cache[key] = value
            
            if ttl:
                self._ttl[key] = time.time() + ttl
            
            self.logger.debug(f"Кэш SET: {key} (TTL: {ttl})")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка записи в кэш: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удалить значение из кэша"""
        try:
            if key in self._cache:
                del self._cache[key]
            
            if key in self._ttl:
                del self._ttl[key]
            
            self.logger.debug(f"Кэш DELETE: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка удаления из кэша: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        if key in self._cache:
            # Проверяем TTL
            if key in self._ttl and time.time() > self._ttl[key]:
                await self.delete(key)
                return False
            return True
        return False
    
    async def clear(self) -> bool:
        """Очистить весь кэш"""
        try:
            self._cache.clear()
            self._ttl.clear()
            self.logger.info("Кэш очищен")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка очистки кэша: {e}")
            return False


@service(singleton=True)
class FileCacheRepository(ICacheRepository):
    """Файловый репозиторий кэша"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_file(self, key: str) -> Path:
        """Получить путь к файлу кэша"""
        # Заменяем небезопасные символы
        safe_key = key.replace(":", "_").replace("/", "_").replace("\\", "_")
        return self.cache_dir / f"{safe_key}.json"
    
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            self.logger.debug(f"Кэш MISS: {key}")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверяем TTL
            if 'ttl' in data and time.time() > data['ttl']:
                await self.delete(key)
                return None
            
            self.logger.debug(f"Кэш HIT: {key}")
            return data['value']
        
        except Exception as e:
            self.logger.error(f"Ошибка чтения кэша {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Установить значение в кэш"""
        cache_file = self._get_cache_file(key)
        
        try:
            data = {'value': value}
            
            if ttl:
                data['ttl'] = time.time() + ttl
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"Кэш SET: {key} (TTL: {ttl})")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка записи кэша {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удалить значение из кэша"""
        cache_file = self._get_cache_file(key)
        
        try:
            if cache_file.exists():
                cache_file.unlink()
            
            self.logger.debug(f"Кэш DELETE: {key}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка удаления кэша {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return False
        
        # Проверяем TTL
        value = await self.get(key)
        return value is not None
    
    async def clear(self) -> bool:
        """Очистить весь кэш"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            
            self.logger.info("Кэш очищен")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка очистки кэша: {e}")
            return False


# Псевдоним для основного использования
CacheRepository = MemoryCacheRepository
