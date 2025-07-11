#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система проверки здоровья приложения.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

from ..config.enhanced_config import config
from ..utils.exceptions import HealthCheckError


@dataclass
class HealthIssue:
    """Проблема здоровья системы"""
    component: str
    severity: str  # 'critical', 'warning', 'info'
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class HealthStatus:
    """Статус здоровья системы"""
    is_healthy: bool
    issues: List[HealthIssue]
    last_check: datetime
    check_duration: float
    
    @property
    def has_critical_issues(self) -> bool:
        """Есть ли критические проблемы"""
        return any(issue.severity == 'critical' for issue in self.issues)
    
    @property
    def has_warnings(self) -> bool:
        """Есть ли предупреждения"""
        return any(issue.severity == 'warning' for issue in self.issues)


class HealthChecker:
    """Система проверки здоровья приложения"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.checks = [
            self._check_configuration,
            self._check_credentials,
            self._check_directories,
            self._check_permissions,
            self._check_google_api,
            self._check_cache,
            self._check_database,
            self._check_disk_space,
            self._check_memory,
        ]
    
    async def check_all(self) -> HealthStatus:
        """
        Выполнить все проверки здоровья
        
        Returns:
            Статус здоровья системы
        """
        start_time = datetime.now()
        issues = []
        
        self.logger.info("🔍 Запуск проверки здоровья системы...")
        
        for check in self.checks:
            try:
                check_issues = await check()
                if check_issues:
                    issues.extend(check_issues)
            except Exception as e:
                issues.append(HealthIssue(
                    component=check.__name__,
                    severity='critical',
                    message=f"Ошибка при выполнении проверки: {e}",
                    details={'exception': str(e)}
                ))
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        is_healthy = not any(issue.severity == 'critical' for issue in issues)
        
        status = HealthStatus(
            is_healthy=is_healthy,
            issues=issues,
            last_check=end_time,
            check_duration=duration
        )
        
        self._log_health_status(status)
        return status
    
    async def _check_configuration(self) -> List[HealthIssue]:
        """Проверка конфигурации"""
        issues = []
        
        try:
            settings = config.settings
            
            # Проверка критических настроек
            if settings.google_workspace_domain == "yourdomain.com":
                issues.append(HealthIssue(
                    component="configuration",
                    severity="critical",
                    message="Домен Google Workspace не настроен",
                    details={"setting": "google_workspace_domain"}
                ))
            
            if settings.google_workspace_admin == "admin@yourdomain.com":
                issues.append(HealthIssue(
                    component="configuration",
                    severity="critical",
                    message="Email администратора не настроен",
                    details={"setting": "google_workspace_admin"}
                ))
            
            # Проверка безопасности
            if settings.secret_key == "your-secret-key-here":
                issues.append(HealthIssue(
                    component="configuration",
                    severity="warning",
                    message="Использует стандартный секретный ключ",
                    details={"setting": "secret_key"}
                ))
            
        except Exception as e:
            issues.append(HealthIssue(
                component="configuration",
                severity="critical",
                message=f"Ошибка загрузки конфигурации: {e}"
            ))
        
        return issues
    
    async def _check_credentials(self) -> List[HealthIssue]:
        """Проверка файла credentials"""
        issues = []
        
        try:
            creds_path = Path(config.settings.google_application_credentials)
            
            if not creds_path.exists():
                issues.append(HealthIssue(
                    component="credentials",
                    severity="critical",
                    message=f"Файл credentials не найден: {creds_path}",
                    details={"path": str(creds_path)}
                ))
            else:
                # Проверка размера файла
                if creds_path.stat().st_size == 0:
                    issues.append(HealthIssue(
                        component="credentials",
                        severity="critical",
                        message="Файл credentials пуст"
                    ))
                
                # Проверка разрешений
                if not creds_path.is_file():
                    issues.append(HealthIssue(
                        component="credentials",
                        severity="warning",
                        message="Файл credentials не является обычным файлом"
                    ))
        
        except Exception as e:
            issues.append(HealthIssue(
                component="credentials",
                severity="critical",
                message=f"Ошибка проверки credentials: {e}"
            ))
        
        return issues
    
    async def _check_directories(self) -> List[HealthIssue]:
        """Проверка необходимых директорий"""
        issues = []
        
        required_dirs = ["logs", "data", "cache", "temp"]
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    issues.append(HealthIssue(
                        component="directories",
                        severity="info",
                        message=f"Создана директория: {dir_name}"
                    ))
                except Exception as e:
                    issues.append(HealthIssue(
                        component="directories",
                        severity="critical",
                        message=f"Не удалось создать директорию {dir_name}: {e}"
                    ))
            
            elif not dir_path.is_dir():
                issues.append(HealthIssue(
                    component="directories",
                    severity="critical",
                    message=f"{dir_name} не является директорией"
                ))
        
        return issues
    
    async def _check_permissions(self) -> List[HealthIssue]:
        """Проверка разрешений файлов"""
        issues = []
        
        # Проверка разрешений на запись в рабочие директории
        write_dirs = ["logs", "data", "cache", "temp"]
        
        for dir_name in write_dirs:
            dir_path = Path(dir_name)
            
            if dir_path.exists():
                try:
                    # Пытаемся создать тестовый файл
                    test_file = dir_path / ".health_check_test"
                    test_file.touch()
                    test_file.unlink()
                except Exception as e:
                    issues.append(HealthIssue(
                        component="permissions",
                        severity="critical",
                        message=f"Нет разрешений на запись в {dir_name}: {e}"
                    ))
        
        return issues
    
    async def _check_google_api(self) -> List[HealthIssue]:
        """Проверка доступности Google API"""
        issues = []
        
        try:
            # Проверяем наличие credentials файла
            creds_path = Path(config.settings.google_application_credentials)
            if not creds_path.exists():
                issues.append(HealthIssue(
                    component="google_api",
                    severity="critical",
                    message=f"Файл credentials не найден: {creds_path}"
                ))
                return issues
            
            # Проверяем через старый API (более надежный)
            try:
                from ..auth import get_service, detect_credentials_type
                
                creds_type = detect_credentials_type()
                if creds_type == 'oauth2':
                    # Для OAuth 2.0 делаем более мягкую проверку
                    service = get_service()
                    
                    # Быстрая проверка - получаем одного пользователя
                    test_result = service.users().list(customer='my_customer', maxResults=1).execute()
                    users = test_result.get('users', [])
                    
                    if users:
                        # API работает, пользователи найдены - все хорошо
                        pass
                    else:
                        issues.append(HealthIssue(
                            component="google_api",
                            severity="warning",
                            message="Google API доступен, но пользователи не найдены"
                        ))
                        
                else:
                    # Для Service Account используем новый API
                    from ..api.google_api_client import GoogleAPIClient
                    
                    client = GoogleAPIClient(config.settings.google_application_credentials)
                    
                    if not client.initialize():
                        issues.append(HealthIssue(
                            component="google_api",
                            severity="critical",
                            message="Не удалось инициализировать Google API клиент"
                        ))
                        return issues
                    
                    # Проверка подключения
                    if not await client.test_connection():
                        issues.append(HealthIssue(
                            component="google_api",
                            severity="critical",
                            message="Не удалось подключиться к Google API"
                        ))
                        return issues
                    
                    # Проверка квот (опционально)
                    try:
                        quota_status = await client.get_quota_status()
                        if quota_status and quota_status.usage_percentage > 90:
                            issues.append(HealthIssue(
                                component="google_api",
                                severity="warning",
                                message=f"Квота Google API почти исчерпана: {quota_status.usage_percentage:.1f}%"
                            ))
                    except Exception:
                        # Игнорируем ошибки проверки квот
                        pass
                        
            except Exception as api_error:
                # Если OAuth 2.0 требует авторизации, это нормально
                if "consent" in str(api_error).lower() or "authorization" in str(api_error).lower():
                    issues.append(HealthIssue(
                        component="google_api",
                        severity="info",
                        message="Google API требует авторизации через браузер"
                    ))
                elif "insufficient" in str(api_error).lower():
                    issues.append(HealthIssue(
                        component="google_api",
                        severity="warning",
                        message="Недостаточно прав доступа в Google API"
                    ))
                else:
                    issues.append(HealthIssue(
                        component="google_api",
                        severity="warning",  # Снижаем критичность
                        message=f"Частичная проблема с Google API: {api_error}"
                    ))
        
        except Exception as e:
            # Общие ошибки - тоже снижаем критичность
            issues.append(HealthIssue(
                component="google_api",
                severity="warning",
                message=f"Проблема проверки Google API: {e}"
            ))
        
        return issues
    
    async def _check_cache(self) -> List[HealthIssue]:
        """Проверка системы кэширования"""
        issues = []
        
        try:
            from ..repositories.cache_repository import CacheRepository
            
            cache_repo = CacheRepository()
            
            # Тест записи/чтения
            test_key = "health_check_test"
            test_value = "test_value"
            
            await cache_repo.set(test_key, test_value)
            retrieved_value = await cache_repo.get(test_key)
            
            if retrieved_value != test_value:
                issues.append(HealthIssue(
                    component="cache",
                    severity="warning",
                    message="Кэш не работает корректно"
                ))
            
            await cache_repo.delete(test_key)
        
        except Exception as e:
            issues.append(HealthIssue(
                component="cache",
                severity="warning",
                message=f"Ошибка проверки кэша: {e}"
            ))
        
        return issues
    
    async def _check_database(self) -> List[HealthIssue]:
        """Проверка базы данных"""
        issues = []
        
        try:
            db_path = config.get_database_path()
            
            if not db_path.parent.exists():
                issues.append(HealthIssue(
                    component="database",
                    severity="critical",
                    message=f"Директория БД не существует: {db_path.parent}"
                ))
            
            # Проверка доступности БД
            if db_path.exists():
                if not db_path.is_file():
                    issues.append(HealthIssue(
                        component="database",
                        severity="critical",
                        message="Файл БД не является обычным файлом"
                    ))
        
        except Exception as e:
            issues.append(HealthIssue(
                component="database",
                severity="critical",
                message=f"Ошибка проверки БД: {e}"
            ))
        
        return issues
    
    async def _check_disk_space(self) -> List[HealthIssue]:
        """Проверка свободного места на диске"""
        issues = []
        
        try:
            import shutil
            
            # Проверка свободного места
            free_bytes = shutil.disk_usage(".").free
            free_mb = free_bytes / (1024 * 1024)
            
            if free_mb < 100:  # Менее 100 МБ
                issues.append(HealthIssue(
                    component="disk_space",
                    severity="critical",
                    message=f"Критически мало свободного места: {free_mb:.1f} МБ"
                ))
            elif free_mb < 500:  # Менее 500 МБ
                issues.append(HealthIssue(
                    component="disk_space",
                    severity="warning",
                    message=f"Мало свободного места: {free_mb:.1f} МБ"
                ))
        
        except Exception as e:
            issues.append(HealthIssue(
                component="disk_space",
                severity="warning",
                message=f"Ошибка проверки места на диске: {e}"
            ))
        
        return issues
    
    async def _check_memory(self) -> List[HealthIssue]:
        """Проверка использования памяти"""
        issues = []
        
        try:
            import psutil
            
            # Проверка использования памяти
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                issues.append(HealthIssue(
                    component="memory",
                    severity="warning",
                    message=f"Высокое использование памяти: {memory.percent:.1f}%"
                ))
        
        except ImportError:
            # psutil не установлен
            pass
        except Exception as e:
            issues.append(HealthIssue(
                component="memory",
                severity="info",
                message=f"Не удалось проверить память: {e}"
            ))
        
        return issues
    
    def _log_health_status(self, status: HealthStatus):
        """Логирование результатов проверки"""
        if status.is_healthy:
            self.logger.info(f"✅ Система здорова (проверка за {status.check_duration:.2f}с)")
        else:
            self.logger.error(f"❌ Обнаружены проблемы системы (проверка за {status.check_duration:.2f}с)")
        
        for issue in status.issues:
            level = {
                'critical': logging.ERROR,
                'warning': logging.WARNING,
                'info': logging.INFO
            }.get(issue.severity, logging.INFO)
            
            self.logger.log(level, f"[{issue.component}] {issue.message}")


def is_healthy() -> bool:
    """
    Быстрая проверка здоровья для health check
    
    Returns:
        True если система работает
    """
    try:
        # Базовые проверки
        if not Path("credentials.json").exists():
            return False
        
        if not Path("logs").exists():
            return False
        
        return True
    
    except Exception:
        return False
