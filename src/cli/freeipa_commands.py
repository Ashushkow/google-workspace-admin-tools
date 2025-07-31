#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI команды для работы с FreeIPA
"""

import asyncio
import click
import logging
from typing import List, Optional
from pathlib import Path

from ..integrations.freeipa_integration import FreeIPAIntegration, setup_freeipa_integration
from ..services.user_service import UserService
from ..services.group_service import GroupService
from ..services.freeipa_client import create_freeipa_config_template, test_freeipa_connection
from ..utils.enhanced_logger import setup_logging


logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def freeipa(ctx):
    """Команды для работы с FreeIPA"""
    pass


@freeipa.command()
@click.option('--output', '-o', default='config/freeipa_config.json', help='Путь к файлу конфигурации')
def create_config(output: str):
    """Создать шаблон конфигурации FreeIPA"""
    try:
        create_freeipa_config_template(output)
        click.echo(f"✅ Шаблон конфигурации создан: {output}")
        click.echo("📝 Отредактируйте файл с вашими данными FreeIPA")
    except Exception as e:
        click.echo(f"❌ Ошибка создания конфигурации: {e}", err=True)


@freeipa.command()
@click.option('--config', '-c', default='config/freeipa_config.json', help='Путь к файлу конфигурации')
def test_connection(config: str):
    """Тестировать подключение к FreeIPA"""
    try:
        if test_freeipa_connection(config):
            click.echo("✅ Подключение к FreeIPA успешно")
        else:
            click.echo("❌ Ошибка подключения к FreeIPA", err=True)
    except Exception as e:
        click.echo(f"❌ Ошибка тестирования: {e}", err=True)


@freeipa.command()
@click.option('--config', '-c', default='config/freeipa_config.json', help='Путь к файлу конфигурации')
async def stats(config: str):
    """Показать статистику FreeIPA"""
    try:
        # Временно отключаем до полной настройки DI
        click.echo("⚠️ Команда временно недоступна - требуется настройка DI контейнера")
        return
        
        user_service = container.resolve(UserService)
        group_service = container.resolve(GroupService)
        
        integration = FreeIPAIntegration(user_service, group_service)
        
        if not integration.load_config(config):
            click.echo("❌ Не удалось загрузить конфигурацию", err=True)
            return
        
        async with integration:
            stats_data = await integration.get_freeipa_stats()
            
            if 'error' in stats_data:
                click.echo(f"❌ Ошибка: {stats_data['error']}", err=True)
                return
            
            click.echo("📊 Статистика FreeIPA:")
            click.echo(f"  Сервер: {stats_data['server_url']}")
            click.echo(f"  Домен: {stats_data['domain']}")
            click.echo(f"  Подключен: {'✅' if stats_data['connected'] else '❌'}")
            click.echo(f"  Пользователей: {stats_data['users_count']}")
            click.echo(f"  Групп: {stats_data['groups_count']}")
            
    except Exception as e:
        click.echo(f"❌ Ошибка получения статистики: {e}", err=True)


@freeipa.command()
@click.argument('email')
@click.option('--groups', '-g', multiple=True, help='Группы для добавления пользователя')
@click.option('--config', '-c', default='config/freeipa_config.json', help='Путь к файлу конфигурации')
async def sync_user(email: str, groups: tuple, config: str):
    """Синхронизировать пользователя из Google Workspace в FreeIPA"""
    try:
        user_service = container.resolve(UserService)
        group_service = container.resolve(GroupService)
        
        integration = FreeIPAIntegration(user_service, group_service)
        
        if not integration.load_config(config):
            click.echo("❌ Не удалось загрузить конфигурацию", err=True)
            return
        
        async with integration:
            groups_list = list(groups) if groups else []
            result = await integration.sync_user_to_freeipa(email, groups_list)
            
            if result:
                click.echo(f"✅ Пользователь {email} синхронизирован в FreeIPA")
                if groups_list:
                    click.echo(f"📁 Добавлен в группы: {', '.join(groups_list)}")
            else:
                click.echo(f"❌ Ошибка синхронизации пользователя {email}", err=True)
                
    except Exception as e:
        click.echo(f"❌ Ошибка синхронизации: {e}", err=True)


@freeipa.command()
@click.option('--domain', '-d', help='Домен для фильтрации пользователей')
@click.option('--groups', '-g', multiple=True, help='Группы по умолчанию для всех пользователей')
@click.option('--config', '-c', default='config/freeipa_config.json', help='Путь к файлу конфигурации')
@click.option('--confirm', is_flag=True, help='Подтвердить синхронизацию без запроса')
async def sync_all_users(domain: Optional[str], groups: tuple, config: str, confirm: bool):
    """Синхронизировать всех пользователей из Google Workspace в FreeIPA"""
    try:
        user_service = container.resolve(UserService)
        group_service = container.resolve(GroupService)
        
        integration = FreeIPAIntegration(user_service, group_service)
        
        if not integration.load_config(config):
            click.echo("❌ Не удалось загрузить конфигурацию", err=True)
            return
        
        # Предварительная проверка
        users = await user_service.list_users(domain=domain)
        click.echo(f"📊 Найдено {len(users)} пользователей для синхронизации")
        
        if groups:
            click.echo(f"📁 Группы по умолчанию: {', '.join(groups)}")
        
        if not confirm:
            if not click.confirm('Продолжить синхронизацию?'):
                click.echo("Отменено")
                return
        
        async with integration:
            groups_list = list(groups) if groups else []
            results = await integration.sync_all_users_to_freeipa(domain, groups_list)
            
            # Показываем результаты
            success_count = sum(1 for result in results.values() if result)
            total_count = len(results)
            
            click.echo(f"\n📋 Результаты синхронизации:")
            click.echo(f"  ✅ Успешно: {success_count}")
            click.echo(f"  ❌ Ошибки: {total_count - success_count}")
            click.echo(f"  📊 Всего: {total_count}")
            
            # Показываем неудачные синхронизации
            failed_users = [email for email, result in results.items() if not result]
            if failed_users:
                click.echo(f"\n❌ Пользователи с ошибками:")
                for email in failed_users[:10]:  # Показываем только первые 10
                    click.echo(f"  • {email}")
                if len(failed_users) > 10:
                    click.echo(f"  ... и еще {len(failed_users) - 10}")
                    
    except Exception as e:
        click.echo(f"❌ Ошибка массовой синхронизации: {e}", err=True)


@freeipa.command()
@click.argument('name')
@click.option('--description', '-d', help='Описание группы')
@click.option('--config', '-c', default='config/freeipa_config.json', help='Путь к файлу конфигурации')
async def create_group(name: str, description: Optional[str], config: str):
    """Создать группу в FreeIPA"""
    try:
        user_service = container.resolve(UserService)
        group_service = container.resolve(GroupService)
        
        integration = FreeIPAIntegration(user_service, group_service)
        
        if not integration.load_config(config):
            click.echo("❌ Не удалось загрузить конфигурацию", err=True)
            return
        
        async with integration:
            result = await integration.create_freeipa_group(name, description)
            
            if result:
                click.echo(f"✅ Группа {name} создана в FreeIPA")
                if description:
                    click.echo(f"📝 Описание: {description}")
            else:
                click.echo(f"❌ Ошибка создания группы {name}", err=True)
                
    except Exception as e:
        click.echo(f"❌ Ошибка создания группы: {e}", err=True)


@freeipa.command()
@click.option('--domain', '-d', help='Домен для фильтрации групп')
@click.option('--config', '-c', default='config/freeipa_config.json', help='Путь к файлу конфигурации')
@click.option('--confirm', is_flag=True, help='Подтвердить синхронизацию без запроса')
async def sync_groups(domain: Optional[str], config: str, confirm: bool):
    """Синхронизировать группы из Google Workspace в FreeIPA"""
    try:
        user_service = container.resolve(UserService)
        group_service = container.resolve(GroupService)
        
        integration = FreeIPAIntegration(user_service, group_service)
        
        if not integration.load_config(config):
            click.echo("❌ Не удалось загрузить конфигурацию", err=True)
            return
        
        # Предварительная проверка
        groups = await group_service.list_groups(domain=domain)
        click.echo(f"📊 Найдено {len(groups)} групп для синхронизации")
        
        if not confirm:
            if not click.confirm('Продолжить синхронизацию групп?'):
                click.echo("Отменено")
                return
        
        async with integration:
            results = await integration.sync_google_groups_to_freeipa(domain)
            
            # Показываем результаты
            success_count = sum(1 for result in results.values() if result)
            total_count = len(results)
            
            click.echo(f"\n📋 Результаты синхронизации групп:")
            click.echo(f"  ✅ Успешно: {success_count}")
            click.echo(f"  ❌ Ошибки: {total_count - success_count}")
            click.echo(f"  📊 Всего: {total_count}")
            
    except Exception as e:
        click.echo(f"❌ Ошибка синхронизации групп: {e}", err=True)


@freeipa.command()
@click.argument('user_email')
@click.argument('group_name')
@click.option('--config', '-c', default='config/freeipa_config.json', help='Путь к файлу конфигурации')
async def add_user_to_group(user_email: str, group_name: str, config: str):
    """Добавить пользователя в группу FreeIPA"""
    try:
        user_service = container.resolve(UserService)
        group_service = container.resolve(GroupService)
        
        integration = FreeIPAIntegration(user_service, group_service)
        
        if not integration.load_config(config):
            click.echo("❌ Не удалось загрузить конфигурацию", err=True)
            return
        
        async with integration:
            result = await integration.add_user_to_freeipa_group(user_email, group_name)
            
            if result:
                click.echo(f"✅ Пользователь {user_email} добавлен в группу {group_name}")
            else:
                click.echo(f"❌ Ошибка добавления пользователя в группу", err=True)
                
    except Exception as e:
        click.echo(f"❌ Ошибка добавления в группу: {e}", err=True)


@freeipa.command()
@click.option('--domain', '-d', help='Домен для фильтрации')
@click.option('--config', '-c', default='config/freeipa_config.json', help='Путь к файлу конфигурации')
async def compare_users(domain: Optional[str], config: str):
    """Сравнить пользователей Google Workspace и FreeIPA"""
    try:
        user_service = container.resolve(UserService)
        group_service = container.resolve(GroupService)
        
        integration = FreeIPAIntegration(user_service, group_service)
        
        if not integration.load_config(config):
            click.echo("❌ Не удалось загрузить конфигурацию", err=True)
            return
        
        async with integration:
            comparison = await integration.compare_users_with_google(domain)
            
            if 'error' in comparison:
                click.echo(f"❌ Ошибка: {comparison['error']}", err=True)
                return
            
            click.echo("📊 Сравнение пользователей:")
            click.echo(f"  Google Workspace: {comparison['google_users_count']}")
            click.echo(f"  FreeIPA: {comparison['freeipa_users_count']}")
            click.echo(f"  В обеих системах: {len(comparison['in_both'])}")
            click.echo(f"  Только в Google: {len(comparison['only_in_google'])}")
            click.echo(f"  Только в FreeIPA: {len(comparison['only_in_freeipa'])}")
            click.echo(f"  Требуют синхронизации: {comparison['sync_needed']}")
            
            if comparison['only_in_google']:
                click.echo(f"\n📝 Пользователи только в Google (первые 10):")
                for email in comparison['only_in_google'][:10]:
                    click.echo(f"  • {email}")
                    
    except Exception as e:
        click.echo(f"❌ Ошибка сравнения: {e}", err=True)


# Регистрируем async команды
def _run_async_command(func):
    """Wrapper для запуска async команд"""
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

# Применяем wrapper к async командам
stats.callback = _run_async_command(stats.callback)
sync_user.callback = _run_async_command(sync_user.callback)
sync_all_users.callback = _run_async_command(sync_all_users.callback)
create_group.callback = _run_async_command(create_group.callback)
sync_groups.callback = _run_async_command(sync_groups.callback)
add_user_to_group.callback = _run_async_command(add_user_to_group.callback)
compare_users.callback = _run_async_command(compare_users.callback)
