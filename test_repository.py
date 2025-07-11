#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест GoogleUserRepository с реальными пользователями
"""

import os
import sys
import asyncio
from pathlib import Path

# Принудительно перезагружаем .env
from dotenv import load_dotenv
load_dotenv(override=True)

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

async def test_repository():
    """Тестируем repository"""
    print("=== ТЕСТ REPOSITORY ===")
    
    from src.repositories.google_api_repository import GoogleUserRepository
    
    repo = GoogleUserRepository()
    print(f"Repository создан: {repo}")
    
    # Инициализируем
    await repo._ensure_initialized()
    print(f"Инициализирован: {repo._initialized}")
    
    # Получаем пользователей
    users = await repo.get_all()
    print(f"Получено пользователей: {len(users)}")
    
    for user in users:
        print(f"   • {user.primary_email} ({user.full_name})")

if __name__ == "__main__":
    asyncio.run(test_repository())
