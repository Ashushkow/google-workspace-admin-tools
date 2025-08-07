# -*- mode: python ; coding: utf-8 -*-
"""
Улучшенный spec файл для компиляции Admin Team Tools v2.2.0
"""

import os
from pathlib import Path

# Определяем пути
project_root = Path.cwd()
src_path = project_root / 'src'

# Данные для включения в сборку
datas = [
    # Конфигурационные файлы
    ('credentials.json', '.'),
    ('.env', '.'),
    ('.env.oauth2', '.'),
    
    # Папки с ресурсами
    ('config', 'config'),
    ('templates', 'templates'),
    ('docs', 'docs'),
    
    # Исключаем логи и временные файлы
    # ('logs', 'logs'),  # Не включаем логи
]

# Скрытые импорты для Google API и других библиотек
hiddenimports = [
    # Google API
    'google.api_core',
    'google.auth',
    'google.auth.transport',
    'google.auth.transport.requests',
    'google.auth.transport.urllib3',
    'google.oauth2',
    'google.oauth2.credentials',
    'google.oauth2.service_account',
    'googleapiclient',
    'googleapiclient.discovery',
    'googleapiclient.errors',
    'googleapiclient.http',
    
    # HTTP и запросы
    'httplib2',
    'requests',
    'urllib3',
    
    # Tkinter компоненты
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'tkinter.simpledialog',
    'tkinter.font',
    
    # Асинхронность
    'asyncio',
    'concurrent.futures',
    'threading',
    
    # Работа с данными
    'json',
    'csv',
    'datetime',
    'pathlib',
    'logging',
    'configparser',
    
    # Валидация и типы
    'pydantic',
    'pydantic.dataclasses',
    'pydantic_settings',
    'typing',
    'typing_extensions',
    
    # FreeIPA (опционально)
    'python_freeipa',
    'requests_kerberos',
    
    # Локальные модули
    'src.core',
    'src.api',
    'src.ui',
    'src.utils',
    'src.config',
    'src.themes',
    'src.hotkeys',
]

# Бинарные файлы (если есть)
binaries = []

# Исключения
excludes = [
    'pytest',
    'pytest-cov',
    'black',
    'flake8',
    'mypy',
    'pip',
    'setuptools',
    'wheel',
    'distutils',
    'test',
    'tests',
    'unittest',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_root), str(src_path)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

# Фильтруем дубликаты
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AdminTeamTools_v2.2.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Убираем консоль для GUI приложения
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Можно добавить иконку: 'icon.ico'
    version_file=None,  # Можно добавить версию: 'version.txt'
)
