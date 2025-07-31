#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация отправки приветственного письма.
"""

import sys
import os
from pathlib import Path

# Добавляем src в Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.api.google_api_client import GoogleAPIClient
from src.api.gmail_api import create_gmail_service
from src.config.enhanced_config import config


def demo_welcome_email():
    """Демонстрация отправки приветственного письма"""
    print("📧 ДЕМОНСТРАЦИЯ ПРИВЕТСТВЕННОГО ПИСЬМА")
    print("=" * 50)
    
    # Запрашиваем email получателя
    recipient_email = input("Введите email получателя (для демонстрации): ").strip()
    
    if not recipient_email:
        print("❌ Email не указан")
        return
    
    if '@' not in recipient_email:
        print("❌ Некорректный email")
        return
    
    # Инициализируем клиент
    print("\n🔧 Инициализация Google API...")
    client = GoogleAPIClient(config.settings.google_application_credentials)
    
    if not client.initialize():
        print("❌ Не удалось инициализировать Google API")
        return
    
    # Создаем Gmail сервис
    print("📧 Создание Gmail сервиса...")
    gmail_service = create_gmail_service(client.credentials)
    
    if not gmail_service:
        print("❌ Не удалось создать Gmail сервис")
        return
    
    # Отправляем демо письмо
    print(f"📤 Отправка демонстрационного письма на {recipient_email}...")
    
    success = gmail_service.send_welcome_email(
        to_email=recipient_email,
        user_name="Демо Пользователь",
        temporary_password="DemoPass123!",
        admin_email=config.settings.google_workspace_admin
    )
    
    if success:
        print(f"✅ Демонстрационное письмо отправлено на {recipient_email}")
        print("\n📧 Проверьте почту получателя!")
        print("💡 Письмо может попасть в папку 'Спам' при первой отправке")
    else:
        print("❌ Не удалось отправить письмо")
        print("🔍 Проверьте логи для получения подробной информации об ошибке")


def show_email_template():
    """Показать шаблон приветственного письма"""
    print("📄 ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР ШАБЛОНА ПИСЬМА")
    print("=" * 50)
    
    # Инициализируем клиент
    client = GoogleAPIClient(config.settings.google_application_credentials)
    
    if not client.initialize():
        print("❌ Не удалось инициализировать Google API")
        return
    
    # Создаем Gmail сервис  
    gmail_service = create_gmail_service(client.credentials)
    
    if not gmail_service:
        print("❌ Не удалось создать Gmail сервис")
        return
    
    # Создаем демонстрационное сообщение
    demo_text = gmail_service._create_text_welcome_template(
        user_name="Иван Петров",
        email="ivan.petrov@sputnik8.com", 
        password="TempPass123!"
    )
    
    print("📝 Текстовая версия письма:")
    print("-" * 50)
    print(demo_text)
    print("-" * 50)
    
    print("\n💡 HTML версия содержит дополнительное форматирование,")
    print("   цвета, кнопки и корпоративный дизайн.")


def main():
    """Главная функция"""
    print("📧 Gmail API Demo Tool")
    print("Демонстрация отправки приветственных писем для Google Workspace\n")
    
    while True:
        print("\nВыберите действие:")
        print("1. 📧 Отправить демонстрационное письмо")
        print("2. 📄 Показать шаблон письма")
        print("3. ❌ Выход")
        
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == '1':
            demo_welcome_email()
        elif choice == '2':
            show_email_template()
        elif choice == '3':
            print("👋 До свидания!")
            break
        else:
            print("❌ Некорректный выбор")


if __name__ == "__main__":
    main()
