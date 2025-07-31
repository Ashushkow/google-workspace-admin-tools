#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты для проверки применения изменений в группах Google Workspace
"""

import time
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OperationTiming:
    """Информация о времени выполнения операции"""
    operation: str
    start_time: float
    end_time: float
    success: bool
    group_email: str
    user_email: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """Длительность операции в секундах"""
        return self.end_time - self.start_time


class GroupChangeVerifier:
    """Утилита для проверки применения изменений в группах Google"""
    
    def __init__(self, google_client):
        """
        Инициализация верификатора
        
        Args:
            google_client: Экземпляр GoogleAPIClient
        """
        self.google_client = google_client
        self.logger = logging.getLogger(__name__)
    
    def verify_member_removal(self, group_email: str, user_email: str, 
                            max_retries: int = 3, retry_delay: int = 5) -> bool:
        """
        Проверяет, что пользователь действительно удален из группы
        
        Args:
            group_email: Email группы
            user_email: Email пользователя
            max_retries: Максимальное количество попыток проверки
            retry_delay: Задержка между попытками в секундах
            
        Returns:
            True если пользователь удален, False если все еще в группе
        """
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Проверка удаления пользователя {user_email} из группы {group_email}, попытка {attempt + 1}")
                
                members = self.google_client.get_group_members(group_email)
                
                # Проверяем, есть ли пользователь в списке участников
                user_found = any(
                    member.get('email', '').lower() == user_email.lower() 
                    for member in members
                )
                
                if not user_found:
                    self.logger.info(f"✅ Пользователь {user_email} успешно удален из группы {group_email}")
                    return True
                    
                if attempt < max_retries - 1:
                    self.logger.warning(f"⏳ Пользователь {user_email} все еще в группе {group_email}, ожидание {retry_delay} сек...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"❌ Пользователь {user_email} не был удален из группы {group_email} после {max_retries} попыток")
                    
            except Exception as e:
                self.logger.error(f"Ошибка при проверке группы {group_email}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    
        return False
    
    def verify_member_addition(self, group_email: str, user_email: str,
                             max_retries: int = 3, retry_delay: int = 5) -> bool:
        """
        Проверяет, что пользователь действительно добавлен в группу
        
        Args:
            group_email: Email группы
            user_email: Email пользователя
            max_retries: Максимальное количество попыток проверки
            retry_delay: Задержка между попытками в секундах
            
        Returns:
            True если пользователь добавлен, False если все еще не в группе
        """
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Проверка добавления пользователя {user_email} в группу {group_email}, попытка {attempt + 1}")
                
                members = self.google_client.get_group_members(group_email)
                
                user_found = any(
                    member.get('email', '').lower() == user_email.lower() 
                    for member in members
                )
                
                if user_found:
                    self.logger.info(f"✅ Пользователь {user_email} успешно добавлен в группу {group_email}")
                    return True
                    
                if attempt < max_retries - 1:
                    self.logger.warning(f"⏳ Пользователь {user_email} еще не появился в группе {group_email}, ожидание {retry_delay} сек...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"❌ Пользователь {user_email} не был добавлен в группу {group_email} после {max_retries} попыток")
                    
            except Exception as e:
                self.logger.error(f"Ошибка при проверке группы {group_email}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    
        return False
    
    def get_propagation_status(self, group_email: str) -> Dict[str, Any]:
        """
        Получает статус распространения изменений группы
        
        Args:
            group_email: Email группы
            
        Returns:
            Словарь с информацией о статусе группы
        """
        try:
            if not self.google_client.service:
                return {'error': 'Google API сервис не инициализирован'}
            
            # Основная информация о группе
            group_info = self.google_client.service.groups().get(groupKey=group_email).execute()
            
            # Количество участников
            members = self.google_client.get_group_members(group_email)
            
            return {
                'group_email': group_email,
                'group_name': group_info.get('name', ''),
                'member_count': len(members),
                'last_updated': group_info.get('adminCreated', ''),
                'status': 'active' if members else 'empty',
                'direct_members_count': group_info.get('directMembersCount', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса группы {group_email}: {e}")
            return {'error': str(e)}


class GroupOperationMonitor:
    """Мониторинг производительности операций с группами"""
    
    def __init__(self):
        self.timings: List[OperationTiming] = []
        self.logger = logging.getLogger(__name__)
    
    def time_operation(self, operation: str, group_email: str, user_email: str = None):
        """
        Контекстный менеджер для измерения времени операций
        
        Args:
            operation: Название операции
            group_email: Email группы
            user_email: Email пользователя (опционально)
            
        Returns:
            Контекстный менеджер для измерения времени
        """
        class TimingContext:
            def __init__(self, monitor, operation, group_email, user_email):
                self.monitor = monitor
                self.operation = operation
                self.group_email = group_email
                self.user_email = user_email
                self.start_time = None
                self.success = False
            
            def __enter__(self):
                self.start_time = time.time()
                self.monitor.logger.info(f"🚀 Начало операции: {self.operation}")
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                end_time = time.time()
                self.success = exc_type is None
                
                timing = OperationTiming(
                    operation=self.operation,
                    start_time=self.start_time,
                    end_time=end_time,
                    success=self.success,
                    group_email=self.group_email,
                    user_email=self.user_email
                )
                
                self.monitor.timings.append(timing)
                
                status = "✅ успешно" if self.success else "❌ с ошибкой"
                self.monitor.logger.info(f"⏱️ Операция {self.operation} завершена {status} за {timing.duration:.2f} сек")
        
        return TimingContext(self, operation, group_email, user_email)
    
    def get_average_times(self) -> Dict[str, Dict[str, float]]:
        """
        Получает средние времена выполнения операций
        
        Returns:
            Словарь со статистикой по операциям
        """
        if not self.timings:
            return {}
        
        by_operation = {}
        for timing in self.timings:
            if timing.operation not in by_operation:
                by_operation[timing.operation] = []
            by_operation[timing.operation].append(timing.duration)
        
        result = {}
        for operation, times in by_operation.items():
            result[operation] = {
                'average': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'count': len(times),
                'total_time': sum(times)
            }
        
        return result
    
    def get_recent_operations(self, limit: int = 10) -> List[OperationTiming]:
        """
        Получает последние операции
        
        Args:
            limit: Максимальное количество операций
            
        Returns:
            Список последних операций
        """
        return sorted(self.timings, key=lambda x: x.start_time, reverse=True)[:limit]
    
    def clear_history(self):
        """Очищает историю операций"""
        self.timings.clear()
        self.logger.info("История операций очищена")
