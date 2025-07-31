#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция FreeIPA с Google Workspace Admin Tools
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..services.freeipa_client import FreeIPAService, FreeIPAConfig, FreeIPAUser, FreeIPAGroup
from ..services.user_service import UserService
from ..services.group_service import GroupService
from ..core.domain import User, Group
from ..utils.exceptions import AdminToolsError


logger = logging.getLogger(__name__)


class FreeIPAIntegration:
    """Интеграция FreeIPA с Google Workspace"""
    
    def __init__(self, user_service: UserService, group_service: GroupService):
        self.user_service = user_service
        self.group_service = group_service
        self.freeipa_service: Optional[FreeIPAService] = None
        self.config: Optional[FreeIPAConfig] = None
        self._connected = False
    
    @property
    def freeipa_client(self):
        """Псевдоним для freeipa_service для обратной совместимости"""
        # Возвращаем self, чтобы можно было вызывать асинхронные методы
        return self
    
    def load_config(self, config_path: str = "config/freeipa_config.json") -> bool:
        """Загрузка конфигурации FreeIPA"""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.error(f"Файл конфигурации FreeIPA не найден: {config_path}")
                return False
            
            self.config = FreeIPAConfig.from_file(config_path)
            self.freeipa_service = FreeIPAService(self.config)
            logger.info("Конфигурация FreeIPA загружена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации FreeIPA: {e}")
            return False
    
    async def connect(self) -> bool:
        """Подключение к FreeIPA"""
        if not self.freeipa_service:
            logger.error("FreeIPA сервис не инициализирован. Загрузите конфигурацию.")
            return False
        
        try:
            # Выполняем подключение в отдельном потоке
            loop = asyncio.get_event_loop()
            connected = await loop.run_in_executor(None, self.freeipa_service.connect)
            
            self._connected = connected
            if connected:
                logger.info("✅ Подключение к FreeIPA установлено")
            else:
                logger.error("❌ Не удалось подключиться к FreeIPA")
            
            return connected
            
        except Exception as e:
            logger.error(f"Ошибка подключения к FreeIPA: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Отключение от FreeIPA"""
        if self.freeipa_service and self._connected:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.freeipa_service.disconnect)
                self._connected = False
                logger.info("Отключение от FreeIPA")
            except Exception as e:
                logger.warning(f"Ошибка при отключении от FreeIPA: {e}")
    
    async def test_connection(self) -> bool:
        """Тестирование подключения к FreeIPA"""
        if not self._connected or not self.freeipa_service:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.freeipa_service.test_connection)
            return result
        except Exception as e:
            logger.error(f"Ошибка тестирования подключения FreeIPA: {e}")
            return False
    
    # === Синхронизация пользователей ===
    
    async def sync_user_to_freeipa(self, user_email: str, groups: List[str] = None) -> bool:
        """Синхронизация пользователя из Google Workspace в FreeIPA"""
        if not self._connected:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        if groups is None:
            groups = []
        
        try:
            # Получаем пользователя из Google Workspace
            google_user = await self.user_service.get_user(user_email)
            if not google_user:
                logger.error(f"Пользователь {user_email} не найден в Google Workspace")
                return False
            
            # Синхронизируем в FreeIPA
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.freeipa_service.sync_user_from_google,
                google_user.__dict__,
                groups
            )
            
            if result:
                logger.info(f"✅ Пользователь {user_email} синхронизирован в FreeIPA")
            else:
                logger.error(f"❌ Ошибка синхронизации пользователя {user_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации пользователя {user_email}: {e}")
            return False
    
    async def sync_all_users_to_freeipa(self, domain: str = None, default_groups: List[str] = None) -> Dict[str, bool]:
        """Синхронизация всех пользователей домена в FreeIPA"""
        if not self._connected:
            logger.error("Нет подключения к FreeIPA")
            return {}
        
        if default_groups is None:
            default_groups = []
        
        results = {}
        
        try:
            # Получаем всех пользователей из Google Workspace
            users = await self.user_service.list_users(domain=domain)
            
            logger.info(f"Найдено {len(users)} пользователей для синхронизации")
            
            for user in users:
                try:
                    result = await self.sync_user_to_freeipa(user.email, default_groups)
                    results[user.email] = result
                    
                    # Небольшая пауза между запросами
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Ошибка синхронизации пользователя {user.email}: {e}")
                    results[user.email] = False
            
            # Статистика
            success_count = sum(1 for result in results.values() if result)
            logger.info(f"Синхронизировано: {success_count}/{len(results)} пользователей")
            
            return results
            
        except Exception as e:
            logger.error(f"Ошибка массовой синхронизации пользователей: {e}")
            return results
    
    # === Управление группами ===
    
    async def create_freeipa_group(self, group_name: str, description: str = None) -> bool:
        """Создание группы в FreeIPA"""
        if not self._connected:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            freeipa_group = FreeIPAGroup(
                cn=group_name,
                description=description or f"Группа {group_name}"
            )
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.freeipa_service.create_group,
                freeipa_group
            )
            
            if result:
                logger.info(f"✅ Группа {group_name} создана в FreeIPA")
            else:
                logger.error(f"❌ Ошибка создания группы {group_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка создания группы {group_name}: {e}")
            return False
    
    async def sync_google_groups_to_freeipa(self, domain: str = None) -> Dict[str, bool]:
        """Синхронизация групп из Google Workspace в FreeIPA"""
        if not self._connected:
            logger.error("Нет подключения к FreeIPA")
            return {}
        
        results = {}
        
        try:
            # Получаем все группы из Google Workspace
            google_groups = await self.group_service.list_groups(domain=domain)
            
            logger.info(f"Найдено {len(google_groups)} групп для синхронизации")
            
            for group in google_groups:
                try:
                    result = await self.create_freeipa_group(
                        group.name,
                        group.description
                    )
                    results[group.name] = result
                    
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Ошибка синхронизации группы {group.name}: {e}")
                    results[group.name] = False
            
            # Статистика
            success_count = sum(1 for result in results.values() if result)
            logger.info(f"Синхронизировано: {success_count}/{len(results)} групп")
            
            return results
            
        except Exception as e:
            logger.error(f"Ошибка массовой синхронизации групп: {e}")
            return results
    
    # === Управление членством ===
    
    async def add_user_to_freeipa_group(self, user_email: str, group_name: str) -> bool:
        """Добавление пользователя в группу FreeIPA"""
        if not self._connected:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            # Извлекаем username из email
            username = user_email.split('@')[0]
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.freeipa_service.add_user_to_group,
                username,
                group_name
            )
            
            if result:
                logger.info(f"✅ Пользователь {user_email} добавлен в группу {group_name}")
            else:
                logger.error(f"❌ Ошибка добавления пользователя {user_email} в группу {group_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя {user_email} в группу {group_name}: {e}")
            return False
    
    async def sync_google_group_members_to_freeipa(self, group_email: str) -> Dict[str, bool]:
        """Синхронизация членов группы Google в FreeIPA"""
        if not self._connected:
            logger.error("Нет подключения к FreeIPA")
            return {}
        
        results = {}
        
        try:
            # Получаем членов группы из Google Workspace
            members = await self.group_service.get_group_members(group_email)
            group_name = group_email.split('@')[0]  # Используем часть до @ как имя группы
            
            logger.info(f"Синхронизация {len(members)} членов группы {group_email}")
            
            for member in members:
                try:
                    result = await self.add_user_to_freeipa_group(member.email, group_name)
                    results[member.email] = result
                    
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Ошибка добавления {member.email} в группу {group_name}: {e}")
                    results[member.email] = False
            
            # Статистика
            success_count = sum(1 for result in results.values() if result)
            logger.info(f"Добавлено в группу: {success_count}/{len(results)} пользователей")
            
            return results
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации членов группы {group_email}: {e}")
            return results
    
    # === Отчеты и статистика ===
    
    async def get_freeipa_stats(self) -> Dict[str, Any]:
        """Получение статистики FreeIPA"""
        if not self._connected:
            return {"error": "Нет подключения к FreeIPA"}
        
        try:
            loop = asyncio.get_event_loop()
            
            # Получаем статистику параллельно
            users_task = loop.run_in_executor(None, self.freeipa_service.list_users, None, 1000)
            groups_task = loop.run_in_executor(None, self.freeipa_service.list_groups, None, 1000)
            
            users, groups = await asyncio.gather(users_task, groups_task)
            
            return {
                "users_count": len(users),
                "groups_count": len(groups),
                "server_url": self.config.server_url if self.config else "Unknown",
                "domain": self.config.domain if self.config else "Unknown",
                "connected": self._connected
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики FreeIPA: {e}")
            return {"error": str(e)}
    
    async def compare_users_with_google(self, domain: str = None) -> Dict[str, Any]:
        """Сравнение пользователей Google Workspace и FreeIPA"""
        if not self._connected:
            return {"error": "Нет подключения к FreeIPA"}
        
        try:
            # Получаем пользователей из обеих систем
            loop = asyncio.get_event_loop()
            
            google_users_task = self.user_service.list_users(domain=domain)
            freeipa_users_task = loop.run_in_executor(None, self.freeipa_service.list_users, None, 1000)
            
            google_users, freeipa_users = await asyncio.gather(google_users_task, freeipa_users_task)
            
            # Создаем множества email адресов
            google_emails = {user.email for user in google_users}
            freeipa_emails = {user.get('mail', [''])[0] for user in freeipa_users if user.get('mail')}
            
            # Сравниваем
            only_in_google = google_emails - freeipa_emails
            only_in_freeipa = freeipa_emails - google_emails
            in_both = google_emails & freeipa_emails
            
            return {
                "google_users_count": len(google_emails),
                "freeipa_users_count": len(freeipa_emails),
                "only_in_google": list(only_in_google),
                "only_in_freeipa": list(only_in_freeipa),
                "in_both": list(in_both),
                "sync_needed": len(only_in_google)
            }
            
        except Exception as e:
            logger.error(f"Ошибка сравнения пользователей: {e}")
            return {"error": str(e)}
    
    # === Context manager ===
    
    async def __aenter__(self):
        """Async context manager entry"""
        if not self.config:
            raise AdminToolsError("FreeIPA конфигурация не загружена")
        
        connected = await self.connect()
        if not connected:
            raise AdminToolsError("Не удалось подключиться к FreeIPA")
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    # === Дополнительные методы для совместимости с UI ===
    
    async def get_groups(self, search_filter: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение списка групп FreeIPA (асинхронная версия)"""
        if not self._connected or not self.freeipa_service:
            logger.error("Нет подключения к FreeIPA")
            return []
        
        try:
            loop = asyncio.get_event_loop()
            groups = await loop.run_in_executor(
                None,
                self.freeipa_service.get_groups,
                search_filter,
                limit
            )
            return groups
        except Exception as e:
            logger.error(f"Ошибка получения групп FreeIPA: {e}")
            return []
    
    async def get_group(self, group_name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о группе FreeIPA (асинхронная версия)"""
        if not self._connected or not self.freeipa_service:
            logger.error("Нет подключения к FreeIPA")
            return None
        
        try:
            loop = asyncio.get_event_loop()
            group_info = await loop.run_in_executor(
                None,
                self.freeipa_service.get_group,
                group_name
            )
            return group_info
        except Exception as e:
            logger.error(f"Ошибка получения группы {group_name}: {e}")
            return None
    
    async def get_group_members(self, group_name: str) -> List[str]:
        """Получение списка участников группы FreeIPA (асинхронная версия)"""
        if not self._connected or not self.freeipa_service:
            logger.error("Нет подключения к FreeIPA")
            return []
        
        try:
            loop = asyncio.get_event_loop()
            members = await loop.run_in_executor(
                None,
                self.freeipa_service.get_group_members,
                group_name
            )
            return members if members else []
        except Exception as e:
            logger.error(f"Ошибка получения участников группы {group_name}: {e}")
            return []
    
    async def list_users(self, search_filter: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение списка пользователей FreeIPA (асинхронная версия)"""
        if not self._connected or not self.freeipa_service:
            logger.error("Нет подключения к FreeIPA")
            return []
        
        try:
            loop = asyncio.get_event_loop()
            users = await loop.run_in_executor(
                None,
                self.freeipa_service.list_users,
                search_filter,
                limit
            )
            return users if users else []
        except Exception as e:
            logger.error(f"Ошибка получения пользователей FreeIPA: {e}")
            return []
    
    async def add_user_to_group(self, user_uid: str, group_name: str) -> bool:
        """Добавление пользователя в группу FreeIPA (асинхронная версия)"""
        if not self._connected or not self.freeipa_service:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.freeipa_service.add_user_to_group,
                user_uid,
                group_name
            )
            if result:
                logger.info(f"✅ Пользователь {user_uid} добавлен в группу {group_name}")
            return result
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя {user_uid} в группу {group_name}: {e}")
            return False
    
    async def remove_user_from_group(self, user_uid: str, group_name: str) -> bool:
        """Удаление пользователя из группы FreeIPA (асинхронная версия)"""
        if not self._connected or not self.freeipa_service:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.freeipa_service.remove_user_from_group,
                user_uid,
                group_name
            )
            if result:
                logger.info(f"✅ Пользователь {user_uid} удален из группы {group_name}")
            return result
        except Exception as e:
            logger.error(f"Ошибка удаления пользователя {user_uid} из группы {group_name}: {e}")
            return False
    
    async def create_group(self, group_name: str, description: str = None) -> bool:
        """Создание группы FreeIPA (асинхронная версия)"""
        if not self._connected or not self.freeipa_service:
            logger.error("Нет подключения к FreeIPA")
            return False
        
        try:
            freeipa_group = FreeIPAGroup(
                cn=group_name,
                description=description or f"Группа {group_name}"
            )
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.freeipa_service.create_group,
                freeipa_group
            )
            
            return result
        except Exception as e:
            logger.error(f"Ошибка создания группы {group_name}: {e}")
            return False


# === Утилиты ===

async def setup_freeipa_integration(user_service: UserService, group_service: GroupService, 
                                   config_path: str = "config/freeipa_config.json") -> Optional[FreeIPAIntegration]:
    """Настройка интеграции FreeIPA"""
    try:
        integration = FreeIPAIntegration(user_service, group_service)
        
        if not integration.load_config(config_path):
            logger.error("Не удалось загрузить конфигурацию FreeIPA")
            return None
        
        if not await integration.connect():
            logger.error("Не удалось подключиться к FreeIPA")
            return None
        
        logger.info("✅ FreeIPA интеграция настроена")
        return integration
        
    except Exception as e:
        logger.error(f"Ошибка настройки FreeIPA интеграции: {e}")
        return None
