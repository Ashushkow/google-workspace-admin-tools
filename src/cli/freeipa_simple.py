#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простые CLI команды для FreeIPA (без DI контейнера)
"""

import click
import logging
from pathlib import Path

from ..services.freeipa_client import create_freeipa_config_template, test_freeipa_connection


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
def info():
    """Показать информацию о FreeIPA интеграции"""
    click.echo("🔗 FreeIPA Integration для Admin Team Tools")
    click.echo("=" * 50)
    click.echo("")
    click.echo("📋 Доступные команды:")
    click.echo("  create-config   - Создать шаблон конфигурации")
    click.echo("  test-connection - Тестировать подключение")
    click.echo("  info           - Показать эту информацию")
    click.echo("")
    click.echo("📖 Документация:")
    click.echo("  docs/FREEIPA_INTEGRATION_GUIDE.md")
    click.echo("  FREEIPA_QUICKSTART.md")
    click.echo("")
    click.echo("⚠️ Для расширенных функций требуется:")
    click.echo("  pip install python-freeipa requests-kerberos")


@freeipa.command()
def check_dependencies():
    """Проверить зависимости FreeIPA"""
    click.echo("🔍 Проверка зависимостей FreeIPA...")
    
    # Проверяем python-freeipa
    try:
        import python_freeipa
        click.echo("✅ python-freeipa установлен")
    except ImportError:
        click.echo("❌ python-freeipa не установлен")
        click.echo("   Установите: pip install python-freeipa")
    
    # Проверяем requests-kerberos
    try:
        import requests_kerberos
        click.echo("✅ requests-kerberos установлен")
    except ImportError:
        click.echo("❌ requests-kerberos не установлен")
        click.echo("   Установите: pip install requests-kerberos")
    
    # Проверяем базовые зависимости
    try:
        import requests
        click.echo("✅ requests установлен")
    except ImportError:
        click.echo("❌ requests не установлен")
    
    try:
        import click as _click
        click.echo("✅ click установлен")
    except ImportError:
        click.echo("❌ click не установлен")
    
    click.echo("")
    click.echo("📋 Для полной функциональности установите:")
    click.echo("   pip install python-freeipa requests-kerberos")


if __name__ == '__main__':
    freeipa()
