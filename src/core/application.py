#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главное приложение Admin Team Tools с улучшенной архитектурой.
"""

import asyncio
import logging
from typing import Optional
from pathlib import Path

from .di_container import container
from .domain import User, Group
from ..services.user_service import UserService
from ..services.group_service import GroupService
from ..repositories.google_api_repository import GoogleUserRepository, GoogleGroupRepository
from ..repositories.cache_repository import CacheRepository
from ..repositories.audit_repository import SQLiteAuditRepository
from ..config.enhanced_config import config
from ..utils.enhanced_logger import setup_logging
from ..utils.exceptions import AdminToolsError, ConfigurationError
from ..utils.health_check import HealthChecker


class Application:
    """Главное приложение Admin Team Tools"""
    
    def __init__(self):
        self.logger: Optional[logging.Logger] = None
        self.health_checker: Optional[HealthChecker] = None
        self.user_service: Optional[UserService] = None
        self.group_service: Optional[GroupService] = None
        self._running = False
        self._setup_complete = False
    
    async def setup(self) -> bool:
        """
        Настройка приложения
        
        Returns:
            True если настройка успешна
        """
        try:
            # Настройка логирования
            self.logger = setup_logging(config.settings.app_log_level)
            self.logger.info("🚀 Запуск Admin Team Tools v{config.settings.app_version}")
            
            # Валидация конфигурации
            await self._validate_configuration()
            
            # Настройка DI контейнера
            await self._setup_dependencies()
            
            # Проверка здоровья системы
            self.health_checker = HealthChecker()
            health_status = await self.health_checker.check_all()
            
            if not health_status.is_healthy:
                self.logger.error("Проверка здоровья системы не пройдена")
                for issue in health_status.issues:
                    self.logger.error(f"  • {issue}")
                return False
            
            # Получение сервисов
            self.user_service = container.resolve(UserService)
            self.group_service = container.resolve(GroupService)
            
            self._setup_complete = True
            self.logger.info("✅ Настройка приложения завершена успешно")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при настройке приложения: {e}")
            else:
                print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
            return False
    
    async def start(self) -> int:
        """
        Запуск приложения
        
        Returns:
            Код выхода
        """
        if not self._setup_complete:
            success = await self.setup()
            if not success:
                return 1
        
        try:
            self._running = True
            self.logger.info("🏃 Приложение запущено")
            
            # Если режим CLI
            if config.settings.cli_mode:
                return await self._run_cli()
            
            # Если режим GUI
            return await self._run_gui()
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ Приложение остановлено пользователем")
            return 0
        except Exception as e:
            self.logger.error(f"Ошибка при запуске приложения: {e}")
            return 1
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Корректное завершение работы приложения"""
        if self._running:
            self.logger.info("🛑 Завершение работы приложения...")
            self._running = False
            
            # Очистка ресурсов
            await self._cleanup_resources()
            
            self.logger.info("✅ Приложение завершено")
    
    async def _validate_configuration(self):
        """Валидация конфигурации"""
        try:
            # Проверка настроек
            settings = config.settings
            
            # Проверка файла credentials
            creds_path = Path(settings.google_application_credentials)
            if not creds_path.exists():
                raise ConfigurationError(
                    f"Файл credentials не найден: {creds_path}\\n"
                    f"Настройте Google API согласно docs/API_SETUP.md"
                )
            
            # Проверка домена
            if settings.google_workspace_domain == "yourdomain.com":
                raise ConfigurationError(
                    "Необходимо настроить домен Google Workspace в .env файле"
                )
            
            # Проверка email администратора
            if settings.google_workspace_admin == "admin@yourdomain.com":
                raise ConfigurationError(
                    "Необходимо настроить email администратора в .env файле"
                )
            
            # Создание необходимых директорий
            Path("logs").mkdir(exist_ok=True)
            Path("data").mkdir(exist_ok=True)
            Path("cache").mkdir(exist_ok=True)
            
            self.logger.info("✅ Конфигурация валидна")
            
        except Exception as e:
            raise ConfigurationError(f"Ошибка валидации конфигурации: {e}")
    
    async def _setup_dependencies(self):
        """Настройка контейнера зависимостей"""
        from ..repositories.interfaces import IUserRepository, IGroupRepository, ICacheRepository, IAuditRepository
        
        # Регистрация репозиториев с интерфейсами
        container.register(IUserRepository, GoogleUserRepository, singleton=True)
        container.register(IGroupRepository, GoogleGroupRepository, singleton=True)
        container.register(ICacheRepository, CacheRepository, singleton=True)
        container.register(IAuditRepository, SQLiteAuditRepository, singleton=True)
        
        # Регистрация сервисов
        container.register(UserService, singleton=True)
        container.register(GroupService, singleton=True)
        
        self.logger.info("✅ Зависимости настроены")
    
    async def _run_cli(self) -> int:
        """Запуск в CLI режиме"""
        from ..cli.main import CLIApplication
        
        cli_app = CLIApplication(
            user_service=self.user_service,
            group_service=self.group_service
        )
        
        return await cli_app.run()
    
    async def _run_gui(self) -> int:
        """Запуск в GUI режиме"""
        try:
            from ..ui.main_window import AdminToolsMainWindow
            from ..api.service_adapter import ServiceAdapter
            
            self.logger.info("🖥️ Запуск GUI приложения...")
            
            # Создаем адаптер для совместимости с GUI
            service_adapter = ServiceAdapter(
                user_service=self.user_service,
                group_service=self.group_service
            )
            
            # Создаем GUI приложение
            gui_app = AdminToolsMainWindow(service=service_adapter)
            
            # Запускаем GUI (это блокирующая операция)
            gui_app.mainloop()
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска GUI: {e}")
            return 1
    
    async def _cleanup_resources(self):
        """Очистка ресурсов"""
        try:
            # Очистка кэша
            if hasattr(self, 'cache_repo'):
                await self.cache_repo.close()
            
            # Закрытие соединений с БД
            if hasattr(self, 'audit_repo'):
                await self.audit_repo.close()
            
            # Очистка временных файлов
            temp_files = Path("temp").glob("*")
            for temp_file in temp_files:
                if temp_file.is_file():
                    temp_file.unlink()
            
            self.logger.info("✅ Ресурсы очищены")
            
        except Exception as e:
            self.logger.error(f"Ошибка при очистке ресурсов: {e}")


# Функция для запуска приложения
async def main() -> int:
    """Главная функция"""
    app = Application()
    return await app.start()


# Точка входа для CLI
def cli_main():
    """Синхронная точка входа для CLI"""
    return asyncio.run(main())


if __name__ == "__main__":
    exit_code = cli_main()
    exit(exit_code)
