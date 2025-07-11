#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Бизнес-логика для работы с пользователями.
"""

from typing import List, Optional, Dict, Any
from ..core.domain import User, UserStatus
from ..repositories.interfaces import IUserRepository, ICacheRepository, IAuditRepository
from ..core.di_container import inject, service
from ..utils.exceptions import UserNotFoundError, ValidationError
from ..utils.validators import validate_email, validate_user_data
import logging


@service(singleton=True)
class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, 
                 user_repository: IUserRepository,
                 cache_repository: ICacheRepository,
                 audit_repository: IAuditRepository):
        self.user_repo = user_repository
        self.cache_repo = cache_repository
        self.audit_repo = audit_repository
        self.logger = logging.getLogger(__name__)
        
        # Кэшированные данные для GUI
        self._cached_users: List[User] = []
        self._cached_groups: List[Dict[str, Any]] = []
    
    @property
    def users(self) -> List[User]:
        """Список пользователей для обратной совместимости с GUI"""
        return self._cached_users
    
    @property
    def groups(self) -> List[Dict[str, Any]]:
        """Список групп для обратной совместимости с GUI"""
        return self._cached_groups
    
    async def refresh_cache(self):
        """Обновить кэшированные данные"""
        try:
            self._cached_users = await self.get_all_users()
            # TODO: Когда будет GroupService, получать группы оттуда
            self._cached_groups = []
            self.logger.info(f"Кэш обновлен: {len(self._cached_users)} пользователей")
        except Exception as e:
            self.logger.error(f"Ошибка обновления кэша: {e}")
    
    async def get_all_users(self, use_cache: bool = True) -> List[User]:
        """
        Получить всех пользователей
        
        Args:
            use_cache: Использовать кэш
            
        Returns:
            Список пользователей
        """
        cache_key = "users:all"
        
        if use_cache:
            cached_users = await self.cache_repo.get(cache_key)
            if cached_users:
                self.logger.debug("Пользователи загружены из кэша")
                return cached_users
        
        users = await self.user_repo.get_all()
        
        if use_cache:
            await self.cache_repo.set(cache_key, users, ttl=300)  # 5 минут
        
        self.logger.info(f"Загружено {len(users)} пользователей")
        return users
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            Пользователь или None
        """
        if not validate_email(email):
            raise ValidationError(f"Неверный формат email: {email}")
        
        cache_key = f"user:email:{email}"
        cached_user = await self.cache_repo.get(cache_key)
        
        if cached_user:
            return cached_user
        
        user = await self.user_repo.get_by_email(email)
        
        if user:
            await self.cache_repo.set(cache_key, user, ttl=300)
        
        return user
    
    async def create_user(self, user_data: Dict[str, Any], created_by: str = "system") -> User:
        """
        Создать нового пользователя
        
        Args:
            user_data: Данные пользователя
            created_by: Кто создал пользователя
            
        Returns:
            Созданный пользователь
        """
        # Валидация данных
        validation_errors = validate_user_data(user_data)
        if validation_errors:
            raise ValidationError(f"Ошибки валидации: {validation_errors}")
        
        # Проверка существования пользователя
        existing_user = await self.get_user_by_email(user_data['primary_email'])
        if existing_user:
            raise ValidationError(f"Пользователь с email {user_data['primary_email']} уже существует")
        
        # Создание пользователя
        user = User(**user_data)
        created_user = await self.user_repo.create(user)
        
        # Очистка кэша
        await self._clear_user_cache()
        
        # Аудит
        await self.audit_repo.log_action(
            user=created_by,
            action="create_user",
            resource=f"user:{created_user.primary_email}",
            details={"user_data": user_data}
        )
        
        self.logger.info(f"Создан пользователь: {created_user.primary_email}")
        return created_user
    
    async def update_user(self, user: User, updated_by: str = "system") -> User:
        """
        Обновить пользователя
        
        Args:
            user: Пользователь для обновления
            updated_by: Кто обновил пользователя
            
        Returns:
            Обновленный пользователь
        """
        # Проверка существования пользователя
        existing_user = await self.get_user_by_email(user.primary_email)
        if not existing_user:
            raise UserNotFoundError(f"Пользователь {user.primary_email} не найден")
        
        # Обновление
        updated_user = await self.user_repo.update(user)
        
        # Очистка кэша
        await self._clear_user_cache()
        await self.cache_repo.delete(f"user:email:{user.primary_email}")
        
        # Аудит
        await self.audit_repo.log_action(
            user=updated_by,
            action="update_user",
            resource=f"user:{updated_user.primary_email}",
            details={"updated_fields": user.to_dict()}
        )
        
        self.logger.info(f"Обновлен пользователь: {updated_user.primary_email}")
        return updated_user
    
    async def suspend_user(self, email: str, suspended_by: str = "system") -> User:
        """
        Заблокировать пользователя
        
        Args:
            email: Email пользователя
            suspended_by: Кто заблокировал пользователя
            
        Returns:
            Заблокированный пользователь
        """
        user = await self.get_user_by_email(email)
        if not user:
            raise UserNotFoundError(f"Пользователь {email} не найден")
        
        user.suspended = True
        user.status = UserStatus.SUSPENDED
        
        updated_user = await self.update_user(user, suspended_by)
        
        # Аудит
        await self.audit_repo.log_action(
            user=suspended_by,
            action="suspend_user",
            resource=f"user:{email}",
            details={"reason": "suspended"}
        )
        
        self.logger.warning(f"Пользователь заблокирован: {email}")
        return updated_user
    
    async def activate_user(self, email: str, activated_by: str = "system") -> User:
        """
        Активировать пользователя
        
        Args:
            email: Email пользователя
            activated_by: Кто активировал пользователя
            
        Returns:
            Активированный пользователь
        """
        user = await self.get_user_by_email(email)
        if not user:
            raise UserNotFoundError(f"Пользователь {email} не найден")
        
        user.suspended = False
        user.status = UserStatus.ACTIVE
        
        updated_user = await self.update_user(user, activated_by)
        
        # Аудит
        await self.audit_repo.log_action(
            user=activated_by,
            action="activate_user",
            resource=f"user:{email}",
            details={"reason": "activated"}
        )
        
        self.logger.info(f"Пользователь активирован: {email}")
        return updated_user
    
    async def delete_user(self, email: str, deleted_by: str = "system") -> bool:
        """
        Удалить пользователя
        
        Args:
            email: Email пользователя
            deleted_by: Кто удалил пользователя
            
        Returns:
            True если удален успешно
        """
        user = await self.get_user_by_email(email)
        if not user:
            raise UserNotFoundError(f"Пользователь {email} не найден")
        
        # Удаление
        result = await self.user_repo.delete(email)
        
        if result:
            # Очистка кэша
            await self._clear_user_cache()
            await self.cache_repo.delete(f"user:email:{email}")
            
            # Аудит
            await self.audit_repo.log_action(
                user=deleted_by,
                action="delete_user",
                resource=f"user:{email}",
                details={"user_data": user.to_dict()}
            )
            
            self.logger.warning(f"Пользователь удален: {email}")
        
        return result
    
    async def search_users(self, query: str) -> List[User]:
        """
        Поиск пользователей
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Список найденных пользователей
        """
        if not query or len(query) < 3:
            raise ValidationError("Поисковый запрос должен содержать минимум 3 символа")
        
        cache_key = f"users:search:{query}"
        cached_results = await self.cache_repo.get(cache_key)
        
        if cached_results:
            return cached_results
        
        users = await self.user_repo.search(query)
        
        # Кэшируем результаты поиска на 5 минут
        await self.cache_repo.set(cache_key, users, ttl=300)
        
        self.logger.info(f"Найдено {len(users)} пользователей по запросу: {query}")
        return users
    
    async def get_users_by_org_unit(self, org_unit_path: str) -> List[User]:
        """
        Получить пользователей по организационному подразделению
        
        Args:
            org_unit_path: Путь к подразделению
            
        Returns:
            Список пользователей
        """
        cache_key = f"users:org_unit:{org_unit_path}"
        cached_users = await self.cache_repo.get(cache_key)
        
        if cached_users:
            return cached_users
        
        users = await self.user_repo.get_by_org_unit(org_unit_path)
        
        # Кэшируем на 10 минут
        await self.cache_repo.set(cache_key, users, ttl=600)
        
        self.logger.info(f"Найдено {len(users)} пользователей в подразделении: {org_unit_path}")
        return users
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику пользователей
        
        Returns:
            Словарь со статистикой
        """
        cache_key = "users:statistics"
        cached_stats = await self.cache_repo.get(cache_key)
        
        if cached_stats:
            return cached_stats
        
        all_users = await self.get_all_users()
        
        stats = {
            'total_users': len(all_users),
            'active_users': len([u for u in all_users if u.is_active]),
            'suspended_users': len([u for u in all_users if u.suspended]),
            'users_by_org_unit': {},
            'users_by_status': {}
        }
        
        # Группировка по подразделениям
        for user in all_users:
            org_unit = user.org_unit_path
            if org_unit not in stats['users_by_org_unit']:
                stats['users_by_org_unit'][org_unit] = 0
            stats['users_by_org_unit'][org_unit] += 1
        
        # Группировка по статусам
        for user in all_users:
            status = user.status.value
            if status not in stats['users_by_status']:
                stats['users_by_status'][status] = 0
            stats['users_by_status'][status] += 1
        
        # Кэшируем на 15 минут
        await self.cache_repo.set(cache_key, stats, ttl=900)
        
        return stats
    
    async def _clear_user_cache(self):
        """Очистить кэш пользователей"""
        await self.cache_repo.delete("users:all")
        await self.cache_repo.delete("users:statistics")
