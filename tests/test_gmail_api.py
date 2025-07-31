#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование Gmail API для отправки приветственных писем.
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.api.google_api_client import GoogleAPIClient
from src.api.gmail_api import create_gmail_service
from src.config.enhanced_config import config


def test_gmail_api():
    """Тестирование Gmail API"""
    print("🧪 ТЕСТИРОВАНИЕ GMAIL API")
    print("=" * 50)
    
    # Инициализируем Google API клиент
    print("🔧 Инициализация Google API клиента...")
    client = GoogleAPIClient(config.settings.google_application_credentials)
    
    if not client.initialize():
        print("❌ Не удалось инициализировать Google API клиент")
        return False
    
    print("✅ Google API клиент инициализирован")
    
    # Проверяем Gmail API
    if not hasattr(client, 'gmail_service') or not client.gmail_service:
        print("❌ Gmail API сервис недоступен")
        return False
    
    print("✅ Gmail API сервис доступен")
    
    # Создаем Gmail сервис
    gmail_service = create_gmail_service(client.credentials)
    
    if not gmail_service:
        print("❌ Не удалось создать Gmail сервис")
        return False
    
    print("✅ Gmail сервис создан")
    
    # Тестируем доступ к Gmail API
    print("\n🔍 Тестирование доступа к Gmail API...")
    if not gmail_service.test_gmail_access():
        print("❌ Нет доступа к Gmail API")
        return False
    
    print("✅ Доступ к Gmail API подтвержден")
    
    # Тестируем создание сообщения (без отправки)
    print("\n📧 Тестирование создания приветственного письма...")
    test_message = gmail_service.create_welcome_message(
        to_email="test@example.com",
        user_name="Тестовый Пользователь",
        temporary_password="TempPass123!",
        admin_email=config.settings.google_workspace_admin
    )
    
    if not test_message:
        print("❌ Не удалось создать тестовое сообщение")
        return False
    
    print("✅ Тестовое сообщение создано успешно")
    print(f"📏 Размер сообщения: {len(test_message['raw'])} символов")
    
    # Предупреждение о тесте отправки
    print("\n⚠️  ВНИМАНИЕ: Для полного тестирования отправки письма")
    print("   требуется указать реальный email в качестве получателя.")
    print("   Раскомментируйте код ниже и укажите свой email для теста.")
    
    # Тестирование отправки (закомментировано для безопасности)
    """
    print("\n📤 Тестирование отправки письма...")
    test_email = "your-email@domain.com"  # Замените на свой email
    
    success = gmail_service.send_welcome_email(
        to_email=test_email,
        user_name="Тестовый Пользователь",
        temporary_password="TempPass123!",
        admin_email=config.settings.google_workspace_admin
    )
    
    if success:
        print(f"✅ Тестовое письмо отправлено на {test_email}")
    else:
        print("❌ Не удалось отправить тестовое письмо")
        return False
    """
    
    print("\n🎉 Все тесты Gmail API пройдены успешно!")
    return True


def check_gmail_scopes():
    """Проверка наличия Gmail scope в конфигурации"""
    print("\n🔍 Проверка Gmail scopes...")
    
    gmail_scope = 'https://www.googleapis.com/auth/gmail.send'
    
    if gmail_scope in config.google.scopes:
        print(f"✅ Gmail scope найден: {gmail_scope}")
        return True
    else:
        print(f"❌ Gmail scope отсутствует: {gmail_scope}")
        print("📋 Текущие scopes:")
        for i, scope in enumerate(config.google.scopes, 1):
            print(f"  {i}. {scope}")
        return False


def main():
    """Главная функция"""
    print("📧 Gmail API Testing Tool")
    print("Этот инструмент проверяет работу Gmail API для отправки приветственных писем.\n")
    
    # Проверяем scopes
    if not check_gmail_scopes():
        print("\n❌ Gmail scope не настроен. Добавьте его в конфигурацию и перезапустите токен OAuth.")
        return
    
    # Тестируем Gmail API
    try:
        success = test_gmail_api()
        
        if success:
            print("\n🎊 Gmail API готов к использованию!")
            print("✅ Теперь при создании пользователей будут автоматически отправляться приветственные письма.")
        else:
            print("\n❌ Gmail API не настроен корректно")
            print("📖 Проверьте документацию по настройке Gmail API")
            
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
