#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI приложение Admin Team Tools с поддержкой FreeIPA
"""

import logging
import click
import asyncio
from typing import Optional

from ..core.di_container import container
from ..services.user_service import UserService
from ..services.group_service import GroupService


logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Подробный вывод')
@click.pass_context
def cli(ctx, verbose):
    """Admin Team Tools - Управление Google Workspace и FreeIPA"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.group()
def users():
    """Управление пользователями"""
    pass


@cli.group()
def groups():
    """Управление группами"""
    pass


@users.command()
@click.option('--domain', '-d', help='Домен для фильтрации')
@click.option('--limit', '-l', default=100, help='Максимальное количество результатов')
async def list(domain: Optional[str], limit: int):
    """Список пользователей Google Workspace"""
    try:
        user_service = container.resolve(UserService)
        users = await user_service.list_users(domain=domain, max_results=limit)
        
        click.echo(f"📊 Найдено пользователей: {len(users)}")
        for user in users:
            click.echo(f"  👤 {user.email} - {user.full_name}")
            
    except Exception as e:
        click.echo(f"❌ Ошибка получения пользователей: {e}", err=True)


@users.command()
@click.argument('email')
async def show(email: str):
    """Показать информацию о пользователе"""
    try:
        user_service = container.resolve(UserService)
        user = await user_service.get_user(email)
        
        if not user:
            click.echo(f"❌ Пользователь {email} не найден", err=True)
            return
        
        click.echo(f"👤 Пользователь: {user.email}")
        click.echo(f"  Имя: {user.full_name}")
        click.echo(f"  Статус: {'Активен' if user.suspended == False else 'Заблокирован'}")
        if hasattr(user, 'org_unit_path'):
            click.echo(f"  Подразделение: {user.org_unit_path}")
            
    except Exception as e:
        click.echo(f"❌ Ошибка получения пользователя: {e}", err=True)


@groups.command()
@click.option('--domain', '-d', help='Домен для фильтрации')
@click.option('--limit', '-l', default=100, help='Максимальное количество результатов')
async def list(domain: Optional[str], limit: int):
    """Список групп Google Workspace"""
    try:
        group_service = container.resolve(GroupService)
        groups = await group_service.list_groups(domain=domain, max_results=limit)
        
        click.echo(f"📊 Найдено групп: {len(groups)}")
        for group in groups:
            click.echo(f"  👥 {group.email} - {group.name}")
            
    except Exception as e:
        click.echo(f"❌ Ошибка получения групп: {e}", err=True)


@groups.command()
@click.argument('email')
async def members(email: str):
    """Показать членов группы"""
    try:
        group_service = container.resolve(GroupService)
        members = await group_service.get_group_members(email)
        
        click.echo(f"👥 Группа: {email}")
        click.echo(f"📊 Членов: {len(members)}")
        
        for member in members:
            click.echo(f"  👤 {member.email} ({member.role})")
            
    except Exception as e:
        click.echo(f"❌ Ошибка получения членов группы: {e}", err=True)


# Регистрируем группу команд FreeIPA (упрощенная версия)
try:
    from .freeipa_simple import freeipa
    cli.add_command(freeipa)
except ImportError as e:
    logger.warning(f"FreeIPA commands not available: {e}")


# Wrapper для async команд
def _run_async_command(func):
    """Wrapper для запуска async команд"""
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


# Применяем wrapper к async командам
users.commands['list'].callback = _run_async_command(users.commands['list'].callback)
users.commands['show'].callback = _run_async_command(users.commands['show'].callback)
groups.commands['list'].callback = _run_async_command(groups.commands['list'].callback)
groups.commands['members'].callback = _run_async_command(groups.commands['members'].callback)


class CLIApplication:
    """CLI приложение с поддержкой FreeIPA"""
    
    def __init__(self, user_service=None, group_service=None):
        self.user_service = user_service
        self.group_service = group_service
        self.logger = logging.getLogger(__name__)
    
    async def run(self) -> int:
        """Запуск CLI приложения"""
        self.logger.info("Запуск CLI режима")
        
        try:
            # Запускаем CLI через click
            cli()
            return 0
        except Exception as e:
            self.logger.error(f"Ошибка CLI: {e}")
            return 1


if __name__ == '__main__':
    cli()
