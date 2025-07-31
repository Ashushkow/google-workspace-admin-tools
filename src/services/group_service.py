#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Бизнес-логика для работы с группами.
"""

from typing import List, Optional, Dict, Any
from ..core.domain import Group, GroupType
from ..repositories.interfaces import IGroupRepository, ICacheRepository, IAuditRepository
from ..core.di_container import inject, service
from ..utils.exceptions import GroupNotFoundError, ValidationError
from ..utils.validators import validate_email, validate_group_data
import logging


@service(singleton=True)
class GroupService:
    """Сервис для работы с группами"""
    
    def __init__(self, 
                 group_repository: IGroupRepository,
                 cache_repository: ICacheRepository,
                 audit_repository: IAuditRepository):
        self.group_repo = group_repository
        self.cache_repo = cache_repository
        self.audit_repo = audit_repository
        self.logger = logging.getLogger(__name__)
        
        # Кэшированные данные для GUI
        self._cached_groups: List[Group] = []
    
    @property
    def groups(self) -> List[Group]:
        """Список групп для обратной совместимости с GUI"""
        return self._cached_groups
    
    async def refresh_cache(self):
        """Обновить кэшированные данные"""
        try:
            self._cached_groups = await self.get_all_groups()
            self.logger.info(f"Кэш групп обновлен: {len(self._cached_groups)} групп")
        except Exception as e:
            self.logger.error(f"Ошибка обновления кэша групп: {e}")
    
    async def get_all_groups(self, use_cache: bool = True) -> List[Group]:
        """
        Получить все группы
        
        Args:
            use_cache: Использовать кэш
            
        Returns:
            Список групп
        """
        cache_key = "groups:all"
        
        if use_cache:
            cached_groups = await self.cache_repo.get(cache_key)
            if cached_groups:
                self.logger.debug("Группы загружены из кэша")
                return cached_groups
        
        groups = await self.group_repo.get_all()
        
        if use_cache:
            await self.cache_repo.set(cache_key, groups, ttl=300)  # 5 минут
        
        self.logger.info(f"Загружено {len(groups)} групп")
        return groups
    
    async def get_group_by_email(self, email: str) -> Optional[Group]:
        """
        Получить группу по email
        
        Args:
            email: Email группы
            
        Returns:
            Группа или None
        """
        if not validate_email(email):
            raise ValidationError(f"Неверный формат email: {email}")
        
        cache_key = f"group:email:{email}"
        cached_group = await self.cache_repo.get(cache_key)
        
        if cached_group:
            return cached_group
        
        group = await self.group_repo.get_by_email(email)
        
        if group:
            await self.cache_repo.set(cache_key, group, ttl=300)
        
        return group
    
    async def create_group(self, group_data: Dict[str, Any], created_by: str = "system") -> Group:
        """
        Создать новую группу
        
        Args:
            group_data: Данные группы
            created_by: Кто создал группу
            
        Returns:
            Созданная группа
        """
        # Валидация данных
        validation_errors = validate_group_data(group_data)
        if validation_errors:
            raise ValidationError(f"Ошибки валидации: {validation_errors}")
        
        # Проверка существования группы
        existing_group = await self.get_group_by_email(group_data['email'])
        if existing_group:
            raise ValidationError(f"Группа с email {group_data['email']} уже существует")
        
        # Создание группы
        group = Group(**group_data)
        created_group = await self.group_repo.create(group)
        
        # Очистка кэша
        await self._clear_group_cache()
        
        # Аудит
        await self.audit_repo.log_action(
            user=created_by,
            action="create_group",
            resource=f"group:{created_group.email}",
            details={"group_data": group_data}
        )
        
        self.logger.info(f"Создана группа: {created_group.email}")
        return created_group
    
    async def add_member(self, group_email: str, member_email: str, added_by: str = "system", verify: bool = True) -> bool:
        """
        Добавить участника в группу
        
        Args:
            group_email: Email группы
            member_email: Email участника
            added_by: Кто добавил участника
            verify: Проверить ли применение изменений
            
        Returns:
            True если добавлен успешно
        """
        # Проверка существования группы
        group = await self.get_group_by_email(group_email)
        if not group:
            raise GroupNotFoundError(f"Группа {group_email} не найдена")
        
        # Добавление участника с верификацией
        result = await self.group_repo.add_member(group_email, member_email, verify=verify)
        
        if result:
            # Очистка кэша
            await self._clear_group_cache()
            
            # Аудит
            await self.audit_repo.log_action(
                user=added_by,
                action="add_group_member",
                resource=f"group:{group_email}",
                details={
                    "member_email": member_email,
                    "verified": verify
                }
            )
            
            verification_status = "с верификацией" if verify else "без верификации"
            self.logger.info(f"Добавлен участник {member_email} в группу {group_email} {verification_status}")
        
        return result
    
    async def remove_member(self, group_email: str, member_email: str, removed_by: str = "system", verify: bool = True) -> bool:
        """
        Удалить участника из группы
        
        Args:
            group_email: Email группы
            member_email: Email участника
            removed_by: Кто удалил участника
            verify: Проверить ли применение изменений
            
        Returns:
            True если удален успешно
        """
        # Проверка существования группы
        group = await self.get_group_by_email(group_email)
        if not group:
            raise GroupNotFoundError(f"Группа {group_email} не найдена")
        
        # Удаление участника с верификацией
        result = await self.group_repo.remove_member(group_email, member_email, verify=verify)
        
        if result:
            # Очистка кэша
            await self._clear_group_cache()
            
            # Аудит
            await self.audit_repo.log_action(
                user=removed_by,
                action="remove_group_member",
                resource=f"group:{group_email}",
                details={
                    "member_email": member_email,
                    "verified": verify
                }
            )
            
            verification_status = "с верификацией" if verify else "без верификации"
            self.logger.info(f"Удален участник {member_email} из группы {group_email} {verification_status}")
        
        return result
    
    async def get_group_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику групп
        
        Returns:
            Словарь со статистикой
        """
        cache_key = "groups:statistics"
        cached_stats = await self.cache_repo.get(cache_key)
        
        if cached_stats:
            return cached_stats
        
        all_groups = await self.get_all_groups()
        
        stats = {
            'total_groups': len(all_groups),
            'security_groups': len([g for g in all_groups if g.group_type == GroupType.SECURITY]),
            'distribution_groups': len([g for g in all_groups if g.group_type == GroupType.DISTRIBUTION]),
            'admin_created_groups': len([g for g in all_groups if g.admin_created]),
            'total_members': sum(g.members_count for g in all_groups)
        }
        
        # Кэшируем на 15 минут
        await self.cache_repo.set(cache_key, stats, ttl=900)
        
        return stats
    
    async def _clear_group_cache(self):
        """Очистить кэш групп"""
        await self.cache_repo.delete("groups:all")
        await self.cache_repo.delete("groups:statistics")
    
    def get_operation_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику операций с группами
        
        Returns:
            Словарь со статистикой времени выполнения операций
        """
        if hasattr(self.group_repo, 'get_operation_statistics'):
            return self.group_repo.get_operation_statistics()
        return {}
    
    def get_recent_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получить последние операции с группами
        
        Args:
            limit: Максимальное количество операций
            
        Returns:
            Список последних операций
        """
        if hasattr(self.group_repo, 'get_recent_operations'):
            return self.group_repo.get_recent_operations(limit)
        return []
    
    def clear_operation_history(self):
        """Очистить историю операций"""
        if hasattr(self.group_repo, 'clear_operation_history'):
            self.group_repo.clear_operation_history()
            self.logger.info("История операций с группами очищена")
    
    async def get_group_propagation_status(self, group_email: str) -> Dict[str, Any]:
        """
        Получить статус распространения изменений группы
        
        Args:
            group_email: Email группы
            
        Returns:
            Словарь с информацией о статусе группы
        """
        if hasattr(self.group_repo, 'get_group_propagation_status'):
            return await self.group_repo.get_group_propagation_status(group_email)
        return {'error': 'Функция недоступна в текущей реализации репозитория'}
