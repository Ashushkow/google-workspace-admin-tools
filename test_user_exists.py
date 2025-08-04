#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая диагностика функции user_exists
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    # Импортируем необходимые модули
    from src.auth import get_service
    from src.api.users_api import user_exists
    
    print("🔍 Диагностика функции user_exists")
    print("=" * 50)
    
    # Получаем сервис
    print("Получение Google API сервиса...")
    service = get_service()
    
    if not service:
        print("❌ Не удалось получить сервис")
        exit(1)
    
    print("✅ Сервис получен")
    
    # Тестируем с заведомо несуществующим пользователем
    test_email = "absolutely.nonexistent.user.test12345@sputnik8.com"
    print(f"\nПроверка пользователя: {test_email}")
    
    result = user_exists(service, test_email)
    print(f"Результат: {result}")
    print(f"Тип результата: {type(result)}")
    
    if result is None:
        print("❌ ПРОБЛЕМА: функция вернула None")
        print("Это означает ошибку при выполнении API запроса")
    elif result is False:
        print("✅ Всё хорошо: пользователь не найден (как и ожидалось)")
    elif result is True:
        print("⚠️ Неожиданно: пользователь найден")
    
    print("\n" + "=" * 50)
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
